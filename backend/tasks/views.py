from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Category, Subcategory, Task
import json
from datetime import datetime

#Инициализация категорий и подкатегорий задач
def initialize_categories():
    if Category.objects.count() == 0:
        categories_data = {
            'marketing': {
                'name': 'Маркетинг', 
                'icon': 'fa-chart-line',
                'subcategories': ['Анализ рынка', 'Реклама', 'SEO']
            },
            'management': {
                'name': 'Менеджмент',
                'icon': 'fa-tasks',
                'subcategories': ['Планирование', 'Контроль', 'Отчетность']
            },
            'development': {
                'name': 'Разработка',
                'icon': 'fa-code',
                'subcategories': ['Фронтенд', 'Бэкенд', 'Анализирование', 'Тестирование']
            },
            'design': {
                'name': 'Дизайн',
                'icon': 'fa-palette',
                'subcategories': ['Прототипирование', 'Визуальный дизайн', 'Анимация']
            }
        }
        for slug, data in categories_data.items():
            category = Category.objects.create(
                name=data['name'],
                slug=slug,
                icon=data['icon']
            )
            for sub_name in data['subcategories']:
                Subcategory.objects.create(
                    name=sub_name,
                    slug=sub_name.lower().replace(' ', '-'),
                    category=category
                )

#Главная страница с категориями задач
@login_required
def index(request):
    initialize_categories()
    categories = Category.objects.all()
    return render(request, 'index.html', {'categories': categories})

#Получение задач категории
@login_required
@require_http_methods(["GET"])
def category_tasks(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    subcategories = Subcategory.objects.filter(category=category)
    tasks = Task.objects.filter(
        user=request.user,
        subcategory__category=category
    ).select_related('subcategory')
    tasks_data = [{
        'id': t.id,
        'title': t.title,
        'deadline': t.deadline.strftime('%Y-%m-%d') if t.deadline else None,
        'subcategory_id': t.subcategory.id,
        'subcategory_name': t.subcategory.name
    } for t in tasks]
    return JsonResponse({
        'success': True,
        'category': {
            'id': category.id,
            'name': category.name,
            'slug': category.slug
        },
        'tasks': tasks_data,
        'subcategories': [
            {'id': s.id, 'name': s.name}
            for s in subcategories
        ]
    })

#Добавление задач
@login_required
@require_http_methods(["POST"])
def add_task(request):
    try:
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        subcategory_id = data.get('subcategory_id')
        if not title or not subcategory_id:
            return JsonResponse({'success': False, 'error': 'Заполните все поля'}, status=400)
        subcategory = Subcategory.objects.select_related('category').get(id=subcategory_id)
        deadline = None
        if data.get('deadline'):
            try:
                deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Неверный формат даты'}, status=400)
        task = Task.objects.create(
            title=title,
            deadline=deadline,
            subcategory=subcategory,
            user=request.user
        )
        return JsonResponse({
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'deadline': data.get('deadline'),
                'subcategory_id': subcategory.id,
                'category_id': subcategory.category.id
            }
        })
    except Subcategory.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Подкатегория не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# Удаление задач
@login_required
@require_http_methods(["DELETE"])
def delete_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id, user=request.user)
        task.delete()
        return JsonResponse({'success': True})
    except Task.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Задача не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)