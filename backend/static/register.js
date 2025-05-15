document.addEventListener('DOMContentLoaded', () => {
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password1');
    const passwordConfirmInput = document.getElementById('password2');
    const clearUsernameButton = document.getElementById('clearUsername');
    const clearEmailButton = document.getElementById('clearEmail');
    const clearPasswordButton = document.getElementById('clearPassword');
    const clearPasswordConfirmButton = document.getElementById('clearPassword2');
    const errorMessage = document.getElementById('errorMessage');
    const registerForm = document.getElementById('registerForm');

    // Очистка имени пользователя
    clearUsernameButton.addEventListener('click', () => {
        usernameInput.value = '';
        errorMessage.style.display = 'none';
    });
    
    // Очистка email
    clearEmailButton.addEventListener('click', () => {
        emailInput.value = '';
        errorMessage.style.display = 'none';
    });

    // Очистка пароля
    clearPasswordButton.addEventListener('click', () => {
        passwordInput.value = '';
        errorMessage.style.display = 'none';
    });
    
    // Очистка поля подтверждения пароля
    clearPasswordConfirmButton.addEventListener('click', () => {
        passwordConfirmInput.value = '';
        errorMessage.style.display = 'none';
    });

    // Обработка формы регистрации
    registerForm.addEventListener('submit', function(event) {
        errorMessage.style.display = 'none';
        
        // Проверка заполненности полей
        if (!usernameInput.value || !emailInput.value || !passwordInput.value || !passwordConfirmInput.value) {
            event.preventDefault();
            errorMessage.textContent = 'Пожалуйста, заполните все поля';
            errorMessage.style.display = 'block';
            return;
        }
        
        // Проверка совпадения паролей
        if (passwordInput.value !== passwordConfirmInput.value) {
            event.preventDefault();
            errorMessage.textContent = 'Пароли не совпадают';
            errorMessage.style.display = 'block';
        }
    });
});