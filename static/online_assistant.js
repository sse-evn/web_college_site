let questions = [];

// Загружаем вопросы из JSON
async function loadQuestions() {
    try {
        const response = await fetch("/static/questions.json");
        questions = await response.json();
    } catch (error) {
        console.error("Ошибка загрузки вопросов:", error);
    }
}

// Переключение окна чата
function toggleChat() {
    let chat = document.getElementById('chatBox');
    let chatQuestions = document.getElementById('chatQuestions');

    if (chat.style.display === 'flex') {
        chat.style.display = 'none';
        document.removeEventListener('click', closeChatOnClickOutside);
    } else {
        chat.style.display = 'flex';
        generateQuestions();
        setTimeout(() => {
            document.addEventListener('click', closeChatOnClickOutside);
        }, 100);
    }
}

// Функция закрытия чата при клике вне него
function closeChatOnClickOutside(event) {
    let chat = document.getElementById('chatBox');
    let chatIcon = document.querySelector('.chat-icon');

    if (!chat.contains(event.target) && !chatIcon.contains(event.target)) {
        chat.style.display = 'none';
        document.removeEventListener('click', closeChatOnClickOutside);
    }
}

// Генерация вопросов
function generateQuestions() {
    let chatQuestions = document.getElementById('chatQuestions');
    chatQuestions.innerHTML = "";

    questions.forEach(q => {
        let btn = document.createElement("div");
        btn.className = "chat-question";
        btn.innerText = q.question;
        btn.onclick = () => showAnswer(q.question, q.answer);
        chatQuestions.appendChild(btn);
    });
}

// Отображение ответа
function showAnswer(question, answer) {
    let chatContent = document.getElementById('chatContent');

    chatContent.innerHTML += `<div class="chat-message user">${question}</div>`;

    setTimeout(() => {
        chatContent.innerHTML += `<div class="chat-message">${answer}</div>`;
        chatContent.scrollTop = chatContent.scrollHeight;
    }, 500);
}

// Загружаем вопросы при загрузке страницы
document.addEventListener("DOMContentLoaded", loadQuestions);
