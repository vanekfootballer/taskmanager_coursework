import random
import string
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from .models import CustomUser, VerificationCode
from .forms import CustomUserCreationForm, EmailVerificationForm, CustomPasswordResetForm, CustomSetPasswordForm
from social_django.models import UserSocialAuth
from social_core.exceptions import AuthAlreadyAssociated
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.backends import ModelBackend

#Генерация рандомного шестизначного кода
def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

#Отправка письма и кода подтверждения на указанный email
def send_verification_email(user, code):
    subject = 'Код подтверждения для регистрации'
    message = f'''
    Здравствуйте, {user.username}!
    
    Ваш код подтверждения: {code}
    Код действителен в течение 30 минут.
    
    Если вы не регистрировались на нашем сайте, проигнорируйте это письмо.
    '''
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

#Обработка формы регистрации
def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            code = generate_verification_code()
            VerificationCode.objects.create(user=user, code=code)
            try:
                send_verification_email(user, code)
                request.session['verify_user_id'] = user.id
                return redirect('verify_email')
            except Exception as e:
                user.delete()
                messages.error(request, 'Ошибка при отправке письма. Попробуйте позже.')
                return render(request, 'register.html', {'form': form})
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

#Подтверждение email, проверка кода из письма и дальнейшая активизация аккаунта, авторизация пользователя
def verify_email(request):
    user_id = request.session.get('verify_user_id')
    if not user_id:
        return redirect('register')
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return redirect('register')  
    if request.method == 'POST':
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            verification_code = VerificationCode.objects.filter(
                user=user,
                code=code,
                is_used=False
            ).first()
            if verification_code and verification_code.is_valid():
                verification_code.mark_as_used()
                user.is_active = True
                user.email_verified = True
                user.save()
                backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user, backend=backend)
                messages.success(request, 'Email успешно подтвержден!')
                return redirect('index')
            else:
                messages.error(request, 'Неверный или устаревший код подтверждения.')
    else:
        form = EmailVerificationForm()
    return render(request, 'verify_email.html', {
        'form': form,
        'email': user.email,
    })

#Вход в аккаунт
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'redirect': reverse('index')})
                return redirect('index')
            else:
                code = generate_verification_code()
                VerificationCode.objects.create(user=user, code=code)
                send_verification_email(user, code)
                request.session['verify_user_id'] = user.id
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'redirect': reverse('verify_email')})
                messages.info(request, 'Ваш email не подтвержден. Мы отправили новый код подтверждения.')
                return redirect('verify_email')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Неверный email или пароль.'}, status=400)
            messages.error(request, 'Неверный email или пароль.')
    
    return render(request, 'login.html')

#Выход из аккаунта
def logout_view(request):
    logout(request)
    return redirect('login')

#Запрос сброса пароля
def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        #Проверка существования пользователя с такой почтой
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, 'Пользователь с таким email не найден')
            return render(request, 'password_reset_request.html')
        
        #генерация рандомного кода подтверждения
        code = ''.join(random.choices(string.digits, k=6))
        VerificationCode.objects.create(user=user, code=code)

        #Отправка письма
        subject = 'Восстановление пароля'
        message = f'''
        Для восстановления пароля используйте следующий код:
        {code}
        
        Если вы не запрашивали сброс пароля, проигнорируйте это письмо.
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        request.session['reset_email'] = email
        return redirect('password_reset_confirm')
    return render(request, 'password_reset_request.html')

#подтверждение сброса пароля и установка нового
def password_reset_confirm(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('password_reset')
    if request.method == 'POST':
        code = request.POST.get('code')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        # Проверка кода подтверждения

        try:
            user = CustomUser.objects.get(email=email)
            verification_code = VerificationCode.objects.get(
                user=user,
                code=code,
                is_used=False
            )
            if verification_code.is_valid():
                if new_password == confirm_password:
                    user.set_password(new_password)
                    user.save()
                    verification_code.mark_as_used()
                    messages.success(request, 'Пароль успешно изменен!')
                    return redirect('login')
                else:
                    messages.error(request, 'Пароли не совпадают')
            else:
                messages.error(request, 'Неверный или устаревший код')
        except (VerificationCode.DoesNotExist, CustomUser.DoesNotExist):
            messages.error(request, 'Неверный код подтверждения')
    return render(request, 'password_reset_confirm.html', {'email': email})

#Аутенфикация через VK
def vk_auth_callback(request):
    try:
        user = request.user
        if not user.email_verified:
            user.email_verified = True
            user.save()
        return redirect('index')
    except AuthAlreadyAssociated:
        messages.error(request, 'Этот аккаунт VK уже привязан к другому пользователю.')
        return redirect('login')
    except Exception as e:
        messages.error(request, 'Ошибка при аутентификации через VK.')
        return redirect('login')