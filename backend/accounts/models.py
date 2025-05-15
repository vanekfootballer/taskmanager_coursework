from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

#для системы аунтефикации
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    vk_id = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.username

#для верификации (подтверждение кода)
class VerificationCode(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    #действителен ли код, когда был создан
    def is_valid(self):
        return not self.is_used and (timezone.now() - self.created_at).total_seconds() < 1800  
    
    def mark_as_used(self):
        self.is_used = True
        self.save()
