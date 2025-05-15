document.addEventListener('DOMContentLoaded', () => {
    const emailInput = document.getElementById('email');
    const clearEmailButton = document.getElementById('clearEmail');
    const errorMessage = document.getElementById('errorMessage');
    const forgotPasswordForm = document.getElementById('forgotPasswordForm');

    // Очистка email
    clearEmailButton.addEventListener('click', () => {
        emailInput.value = '';
        errorMessage.style.display = 'none';
    });

    // Обработка формы восстановления пароля
    forgotPasswordForm.addEventListener('submit', function(event) {
        errorMessage.style.display = 'none';
        if (!emailInput.value) {
            event.preventDefault();
            errorMessage.textContent = 'Пожалуйста, введите email';
            errorMessage.style.display = 'block';
        }
    });

    // Функция для проверки email
    function validateEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }
});