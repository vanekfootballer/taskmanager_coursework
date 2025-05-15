from .models import CustomUser

#обработка данных пользователя после аутенфикации VK
def save_vk_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'vk-oauth2':

        user.vk_id = response.get('id')
        
        if not user.email and response.get('email'):
            user.email = response.get('email')
            user.email_verified = True 
        
        user.save()