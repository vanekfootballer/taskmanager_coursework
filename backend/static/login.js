document.addEventListener('DOMContentLoaded', () => {
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const clearEmailButton = document.getElementById('clearEmail');
    const clearPasswordButton = document.getElementById('clearPassword');
    const errorMessage = document.getElementById('errorMessage');
    const loginForm = document.getElementById('loginForm');

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

    // Обработка формы входа
    loginForm.addEventListener('submit', function(event) {
        errorMessage.style.display = 'none';
        
        // Получение CSRF токена
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        
        const csrftoken = getCookie('csrftoken');
        
        // AJAX запрос
        fetch(loginForm.action, {
            method: 'POST',
            body: new FormData(loginForm),
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'include'
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                return response.json();
            }
        })
        .then(data => {
            if (data && data.error) {
                errorMessage.textContent = data.error;
                errorMessage.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
        event.preventDefault();
    });
});