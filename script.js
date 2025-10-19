function toggleTheme() {
        const body = document.body;
    // Присвоюємо унікальний id функції
    toggleTheme.id = 'toggleTheme-001-unique';
    if (body.classList.contains('light-theme')) {
        body.classList.remove('light-theme');
        body.classList.add('dark-theme');
    } else if (body.classList.contains('dark-theme')) {
        body.classList.remove('dark-theme');
        body.classList.add('light-theme');
    } else {
        // Якщо немає класу, вмикаємо темну тему за замовчуванням
        body.classList.add('dark-theme');
    }
}

function handleNameInput(event) {
    const greetingContainer = document.getElementById('greeting-output');
    const name = event.target.value.trim();

    if (name === "") {
        greetingContainer.textContent = "";
    } else {
        greetingContainer.textContent = `Вітаємо, ${name}!`;
    }
}
document.addEventListener('DOMContentLoaded', function() {
    const nameInput = document.getElementById('name-input');
    if (nameInput) {
        nameInput.addEventListener('input', handleNameInput);
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const commentForm = document.getElementById('comment-form');
    const commentList = document.getElementById('comment-list');

    if (commentForm && commentList) {
        commentForm.addEventListener('submit', function (event) {
            event.preventDefault();
            // Get input values (the first is name, second is comment, by id)
            const nameInput = commentForm.querySelector('#name-input');
            const commentInput = commentForm.querySelector('#comment-input');
            const name = nameInput.value.trim();
            const text = commentInput.value.trim();

            if (name === "" || text === "") {
                // Optionally, add some user feedback
                return;
            }

            // Створити <li> — кореневий елемент нового коментаря
            const li = document.createElement('li');

            // Додаємо ім'я (жирний текст)
            const nameElem = document.createElement('strong');
            nameElem.textContent = name + ': ';

            // Додаємо сам текст коментаря
            const commentElem = document.createElement('span');
            commentElem.textContent = text;

            // Акумулюємо та додаємо елементи
            li.appendChild(nameElem);
            li.appendChild(commentElem);

            commentList.appendChild(li);

            // Очищаємо поля вводу
            nameInput.value = "";
            commentInput.value = "";
        });
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const loadBtn = document.getElementById('load-data-btn');
    const dataContainer = document.getElementById('data-container');
    if (loadBtn && dataContainer) {
        loadBtn.addEventListener('click', async function () {
            // You can pick any of the provided URLs or randomize if desired
            const url = 'https://web2025-test-data.ikto.net/greeting-card.html';

            // Optional: show loading indicator
            dataContainer.innerHTML = 'Завантаження...';

            try {
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const data = await response.text();
                dataContainer.innerHTML = data;
            } catch (error) {
                dataContainer.innerHTML = 'Не вдалося завантажити дані';
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const customLoadBtn = document.getElementById('custom-load-data-btn');
    const customDataContainer = document.getElementById('custom-data-container');
    if (customLoadBtn && customDataContainer) {
        customLoadBtn.addEventListener('click', async function () {
            const urls = [
                'https://web2025-test-data.ikto.net/comments.json',
                'https://web2025-test-data.ikto.net/news.json',
                'https://web2025-test-data.ikto.net/schedule.json'
            ];

            // For example, select the first one, or you could randomize
            const url = urls[0];

            // Показати індикатор завантаження
            customDataContainer.innerHTML = 'Завантаження...';

            try {
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const data = await response.json();
                
                // Очистити контейнер
                customDataContainer.innerHTML = '';

                // Спробуємо красиво вивести типові формати (comments, news, schedule)
                let elementsList = document.createElement('ul');
                if (Array.isArray(data)) {
                    // Наприклад, якщо це comments або news як масив об'єктів
                    data.forEach(item => {
                        const li = document.createElement('li');
                        if (item.name && item.text) {
                            // comments.json
                            const nameElem = document.createElement('strong');
                            nameElem.textContent = item.name + ': ';
                            const textElem = document.createElement('span');
                            textElem.textContent = item.text;
                            li.appendChild(nameElem);
                            li.appendChild(textElem);
                        } else if (item.title && item.body) {
                            // news.json
                            const titleElem = document.createElement('strong');
                            titleElem.textContent = item.title + ': ';
                            const bodyElem = document.createElement('span');
                            bodyElem.textContent = item.body;
                            li.appendChild(titleElem);
                            li.appendChild(bodyElem);
                        } else if (item.time && item.event) {
                            // schedule.json
                            const timeElem = document.createElement('strong');
                            timeElem.textContent = item.time + ' — ';
                            const eventElem = document.createElement('span');
                            eventElem.textContent = item.event;
                            li.appendChild(timeElem);
                            li.appendChild(eventElem);
                        } else {
                            // generic
                            li.textContent = JSON.stringify(item);
                        }
                        elementsList.appendChild(li);
                    });
                } else if (typeof data === 'object' && data !== null) {
                    // Якщо це об'єкт просто
                    Object.entries(data).forEach(([key, value]) => {
                        const li = document.createElement('li');
                        li.textContent = `${key}: ${typeof value === 'object' ? JSON.stringify(value) : value}`;
                        elementsList.appendChild(li);
                    });
                } else {
                    // Щось інше
                    const li = document.createElement('li');
                    li.textContent = JSON.stringify(data);
                    elementsList.appendChild(li);
                }

                customDataContainer.appendChild(elementsList);

            } catch (error) {
                customDataContainer.innerHTML = 'Не вдалося завантажити дані';
            }
        });
    }
});
