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

// Генерация 4 случайных вопросов
function generateQuestions() {
    let chatQuestions = document.getElementById('chatQuestions');
    chatQuestions.innerHTML = "";

    let shuffledQuestions = [...questions].sort(() => 0.5 - Math.random());
    let selectedQuestions = shuffledQuestions.slice(0, 4);

    selectedQuestions.forEach(q => {
        let btn = document.createElement("div");
        btn.className = "chat-question";
        btn.innerText = q.question;
        btn.onclick = () => showAnswer(q.question, q.answer);
        chatQuestions.appendChild(btn);
    });
}

// Отображение ответа с последовательной анимацией
function showAnswer(question, answer) {
    let chatContent = document.getElementById('chatContent');

    // Добавляем сообщение пользователя сразу
    let userMessage = document.createElement("div");
    userMessage.className = "chat-message user";
    userMessage.innerText = question;
    chatContent.appendChild(userMessage);
    chatContent.scrollTop = chatContent.scrollHeight;

    // Создаем контейнер для ответа бота
    let botMessage = document.createElement("div");
    botMessage.className = "chat-message";
    chatContent.appendChild(botMessage);
    chatContent.scrollTop = chatContent.scrollHeight;

    // Разбиваем ответ на слова
    let words = answer.split(" ");
    let currentText = "";
    let wordIndex = 0;

    // Функция для имитации печати
    function typeAnswer() {
        if (wordIndex < words.length) {
            currentText += (wordIndex > 0 ? " " : "") + words[wordIndex];
            botMessage.innerText = currentText;
            chatContent.scrollTop = chatContent.scrollHeight;
            wordIndex++;
            setTimeout(typeAnswer, 166); // Задержка 100мс между словами
        }
    }

    // Начинаем "печатание" с задержкой 500мс после вопроса
    setTimeout(typeAnswer, 666);
}

// Загружаем вопросы при загрузке страницы
document.addEventListener("DOMContentLoaded", loadQuestions);