document.addEventListener('DOMContentLoaded', () => {
    const mainContainer = document.getElementById('mainContainer');
    const taskMenu = document.getElementById('taskMenu');
    const taskList = document.getElementById('taskList');
    const taskInput = document.getElementById('taskInput');
    const taskDeadline = document.getElementById('taskDeadline');
    const taskSubcategory = document.getElementById('taskSubcategory');
    const addTaskButton = document.getElementById('addTask');
    const errorMessage = document.getElementById('errorMessage');
    const taskMenuTitle = document.getElementById('taskMenuTitle');
    const backToMain = document.getElementById('backToMain');
    
    let currentCategory = null;

    // Обработка выбора категории
    document.querySelectorAll('.icon-box').forEach(box => {
        box.addEventListener('click', async () => {
            const categorySlug = box.getAttribute('data-category');
            try {
                const response = await fetch(`/category/${categorySlug}/`);
                const data = await response.json();
                if (data.success) {
                    currentCategory = data.category;
                    taskMenuTitle.textContent = `Задачи - ${currentCategory.name}`;
                    updateSubcategories(data.subcategories);
                    renderTasks(data.tasks);
                    mainContainer.style.display = 'none';
                    taskMenu.style.display = 'block';
                } else {
                    showError(data.error || 'Ошибка загрузки категории');
                }
            } catch (error) {
                showError('Ошибка соединения с сервером');
                console.error('Error:', error);
            }
        });
    });

    // Добавление новой задачи
    addTaskButton.addEventListener('click', async () => {
        const title = taskInput.value.trim();
        const deadline = taskDeadline.value;
        const subcategoryId = taskSubcategory.value;
        if (!title || !subcategoryId) {
            showError('Заполните название и выберите подкатегорию');
            return;
        }
        try {
            const response = await fetch('/add-task/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    title: title,
                    deadline: deadline,
                    subcategory_id: subcategoryId
                })
            });
            const data = await response.json();
            if (data.success) {
                if (data.task.category_id === currentCategory.id) {
                    addTaskToUI(data.task);
                }
                taskInput.value = '';
                taskDeadline.value = '';
                errorMessage.style.display = 'none';
            } else {
                showError(data.error || 'Ошибка при добавлении задачи');
            }
        } catch (error) {
            showError('Ошибка соединения с сервером');
            console.error('Error:', error);
        }
    });

    // Возвращение на главную
    backToMain.addEventListener('click', () => {
        taskMenu.style.display = 'none';
        mainContainer.style.display = 'flex';
    });

    // Обновление списка подкатегорий
    function updateSubcategories(subcategories) {
        taskSubcategory.innerHTML = '';
        subcategories.forEach(sub => {
            const option = document.createElement('option');
            option.value = sub.id;
            option.textContent = sub.name;
            taskSubcategory.appendChild(option);
        });
    }

    // Отображение задач
    function renderTasks(tasks) {
        taskList.innerHTML = '';
        if (tasks.length === 0) {
            taskList.innerHTML = '<p class="no-tasks">Нет задач в этой категории</p>';
            return;
        }
        const tasksBySubcategory = {};
        tasks.forEach(task => {
            if (!tasksBySubcategory[task.subcategory_id]) {
                tasksBySubcategory[task.subcategory_id] = [];
            }
            tasksBySubcategory[task.subcategory_id].push(task);
        });
        taskSubcategory.querySelectorAll('option').forEach(option => {
            const subcategoryId = parseInt(option.value);
            const tasks = tasksBySubcategory[subcategoryId] || [];
            if (tasks.length > 0) {
                const header = document.createElement('h3');
                header.textContent = option.textContent;
                taskList.appendChild(header);
                tasks.forEach(task => {
                    taskList.appendChild(createTaskElement(task));
                });
            }
        });
    }

    // Создание HTML элемента задачи
    function createTaskElement(task) {
        const li = document.createElement('li');
        li.dataset.taskId = task.id;
        li.innerHTML = `
            <div class="task-content">
                <span class="task-title">${task.title}</span>
                ${task.deadline ? `<span class="task-deadline">До: ${task.deadline}</span>` : ''}
            </div>
            <button class="delete-task" onclick="deleteTaskHandler(${task.id})">
                <i class="fas fa-trash"></i>
            </button>
        `;
        return li;
    }

    // Добавление задачи в интерфейс
    function addTaskToUI(task) {
        const taskElement = createTaskElement(task);
        let subcategoryHeader = null;
        const headers = taskList.querySelectorAll('h3');
        for (const header of headers) {
            if (header.textContent === task.subcategory_name) {
                subcategoryHeader = header;
                break;
            }
        }
        if (!subcategoryHeader) {
            subcategoryHeader = document.createElement('h3');
            subcategoryHeader.textContent = task.subcategory_name;
            taskList.appendChild(subcategoryHeader);
            const noTasksMsg = taskList.querySelector('.no-tasks');
            if (noTasksMsg) noTasksMsg.remove();
        }
        subcategoryHeader.insertAdjacentElement('afterend', taskElement);
    }
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }
});

// Удаление задачи
async function deleteTaskHandler(taskId) {
    if (!confirm('Вы точно хотите удалить эту задачу?')) return;
    try {
        const response = await fetch(`/delete-task/${taskId}/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            credentials: 'include'
        });
        const data = await response.json();
        if (data.success) {
            const taskElement = document.querySelector(`li[data-task-id="${taskId}"]`);
            if (taskElement) {
                // Удаляем заголовок подкатегории, если это последняя задача
                const subcategoryHeader = taskElement.previousElementSibling;
                if (subcategoryHeader?.tagName === 'H3') {
                    const nextElement = subcategoryHeader.nextElementSibling;
                    if (!nextElement || nextElement.tagName !== 'LI') {
                        subcategoryHeader.remove();
                    }
                }
                taskElement.remove();
                // Если задач не осталось, показываем сообщение
                if (!document.querySelector('#taskList li')) {
                    const taskList = document.getElementById('taskList');
                    taskList.innerHTML = '<p class="no-tasks">Нет задач в этой категории</p>';
                }
            }
        } else {
            alert('Ошибка: ' + (data.error || 'Не удалось удалить задачу'));
        }
    } catch (error) {
        console.error('Ошибка при удалении:', error);
        alert('Ошибка соединения с сервером');
    }
}

// Получение CSRF токена
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}