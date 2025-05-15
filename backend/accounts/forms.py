from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from .models import CustomUser
import re

#обязательная проверка email, 
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Введите ваш email',
        'id': 'email'
    }))
    
    #Кастомная модель пользователя
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')
    
    def right_email(self):
        email = self.cleaned_data.get('email')
        #проверка на пустое значение
        if not email:
            raise forms.ValidationError("Email обязателен для заполнения.")
        #проверка на правильность формата введённого email 
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            raise forms.ValidationError("Введите корректный email адрес.")
        #проверка на существования пользователя с таким email   
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

#форма для ввода кода для подтверждения email
class EmailVerificationForm(forms.Form):
    code = forms.CharField(max_length=6, required=True)
    
    def right_code(self):
        code = self.cleaned_data.get('code')
        if not re.match(r'^\d{6}$', code):
            raise forms.ValidationError("Код должен состоять из 6 цифр.")
        return code

#проверка на существование email
class CustomPasswordResetForm(PasswordResetForm):
    def right_email(self):
        email = self.cleaned_data.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email не найден.")
        return email

class CustomSetPasswordForm(SetPasswordForm):
    pass