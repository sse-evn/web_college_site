const majorsList = document.querySelector('.majors-list');
const cards = document.querySelectorAll('.major-card');
const majorsContainer = document.querySelector('.majors-container');

// Определяем ширину контейнера и карточки
const containerWidth = majorsContainer.offsetWidth;
const cardWidth = 300 + 20; // Ширина карточки (300px) + gap (20px)
const cardsToShow = Math.ceil(containerWidth / cardWidth) + 1; // Сколько карточек нужно для заполнения + запас

// Динамическое клонирование карточек для заполнения контейнера
let clonedCardsCount = 0;
while (clonedCardsCount < cardsToShow) {
    cards.forEach(card => {
        const clonedCard = card.cloneNode(true);
        majorsList.appendChild(clonedCard);
    });
    clonedCardsCount += cards.length;
}

// Обновляем ширину .majors-list после клонирования
const majorCards = document.querySelectorAll('.major-card');
majorsList.style.width = `${cardWidth * majorCards.length}px`;

// Анимация появления карточек
majorCards.forEach((card, index) => {
    setTimeout(() => {
        card.classList.add('visible');
    }, index * 300); // Задержка 300 мс для последовательного появления
});


const cardsContainer = document.querySelector(".cards-container");
const dotsContainer = document.querySelector(".slider-dots");
const cardsPerPage = 3;
let currentIndex = 0;
let allCards = Array.from(document.querySelectorAll(".card"));
let totalSlides = Math.ceil(allCards.length / cardsPerPage);
let isPaused = false; // Флаг для паузы

// Создаем точки на основе количества слайдов
dotsContainer.innerHTML = "";
for (let i = 0; i < totalSlides; i++) {
    let dot = document.createElement("span");
    dot.classList.add("dot");
    if (i === 0) dot.classList.add("active");
    dot.addEventListener("click", () => {
        currentIndex = i * cardsPerPage;
        updateSlider();
    });
    dotsContainer.appendChild(dot);
}

const dots = document.querySelectorAll(".dot");

function updateSlider() {
    cardsContainer.innerHTML = "";
    for (let i = currentIndex; i < currentIndex + cardsPerPage; i++) {
        let cardIndex = i % allCards.length;
        cardsContainer.appendChild(allCards[cardIndex].cloneNode(true));
    }
    dots.forEach((dot, index) => {
        dot.classList.toggle("active", index === Math.floor(currentIndex / cardsPerPage));
    });
}

// Останавливаем автоскролл при наведении
cardsContainer.addEventListener("mouseenter", () => {
    isPaused = true;
});

cardsContainer.addEventListener("mouseleave", () => {
    isPaused = false;
});

// Функция для автоматического перелистывания
function nextSlide() {
    if (!isPaused) {
        currentIndex = (currentIndex + cardsPerPage) % (totalSlides * cardsPerPage);
        updateSlider();
    }
}

updateSlider();
setInterval(nextSlide, 3000);