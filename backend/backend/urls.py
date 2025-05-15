#Маршрутизация django
from django.contrib import admin
from django.urls import path, include
from tasks import views as tasks_views
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', accounts_views.register, name='register'),
    path('verify-email/', accounts_views.verify_email, name='verify_email'),
    path('login/', accounts_views.login_view, name='login'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('password-reset/', accounts_views.password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/', accounts_views.password_reset_confirm, name='password_reset_confirm'),
    path('', tasks_views.index, name='index'),
    path('category/<slug:category_slug>/', tasks_views.category_tasks, name='category_tasks'),
    path('add-task/', tasks_views.add_task, name='add_task'),
    path('delete-task/<int:task_id>/', tasks_views.delete_task, name='delete_task'),
    path('social-auth/', include('social_django.urls', namespace='social')),
]
