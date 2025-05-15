#Маршрутизация для приложения Tasks
from django.urls import path
from tasks import views

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<slug:category_slug>/', views.category_tasks, name='category_tasks'),
    path('add-task/', views.add_task, name='add_task'),
    path('delete-task/<int:task_id>/', views.delete_task, name='delete_task'),
]