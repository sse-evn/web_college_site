document.addEventListener("DOMContentLoaded", () => {
    const logo = document.querySelector(".logo");

    if (logo) {
        logo.addEventListener("click", function(e) {
            e.preventDefault(); // Отменяет стандартный переход по ссылке

            window.scrollTo({
                top: 0,
                behavior: "smooth" // Делаем прокрутку плавной
            });
        });
    }
    // Получаем контейнер для слайдов
    const majorsList = document.querySelector('.majors-list');
    const cards = document.querySelectorAll('.major-card');


    // Клонируем карточки для бесконечности
    cards.forEach(card => {
        const clonedCard = card.cloneNode(true);
        majorsList.appendChild(clonedCard);
    });

    // Анимация для секции "Мамандықтар"
    const majorCards = document.querySelectorAll(".major-card");

    majorCards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = "1";
            card.style.transform = "translateX(0)";
        }, index * 500);
    });

    // Слайдер для секции "Неге біз?"
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

    // partners 
    const track = document.querySelector(".partners-track");
    const slider = document.querySelector(".partners-slider");

    // Дублируем элементы для бесконечного эффекта
    const items = Array.from(track.children);
    items.forEach(item => {
        let clone = item.cloneNode(true);
        track.appendChild(clone);
    });

    let speed = 1; // Скорость движения
    let position = 0;

    function animate() {
        position -= speed;
        if (Math.abs(position) >= track.scrollWidth / 2) {
            position = 0; // Возвращаем позицию к началу
        }
        track.style.transform = `translateX(${position}px)`;
        requestAnimationFrame(animate);
    }

    animate();

    // --- Загрузка новостей из RSS ---
    const RSS_URL = "https://api.rss2json.com/v1/api.json?rss_url=https://rss.app/feeds/ROqxpqxtrig12IhL.xml";
    const newsSection = document.getElementById("news-section");

    async function loadRSS() {
        try {
            let response = await fetch(RSS_URL);
            let data = await response.json();
            newsSection.innerHTML = ""; // Очищаем контейнер

            data.items.slice(0, 6).forEach(item => { // 6 новостей
                let newsHTML = `
                 <div class="news-item">
                     <img src="${item.enclosure.link || 'default.jpg'}" alt="Новость">
                     <h3>${item.title}</h3>
                     <a href="${item.link}" target="_blank">Читать далее</a>
                 </div>
             `;
                newsSection.innerHTML += newsHTML;
            });
        } catch (error) {
            console.error("Ошибка загрузки новостей:", error);
        }
    }

    // --- Загрузка новостей из своего сервера ---
    async function loadLocalNews() {
        try {
            const response = await fetch("/news");
            const news = await response.json();
            const newsContainer = document.getElementById("news");
            newsContainer.innerHTML = "";

            news.slice(0, 8).forEach((item) => { // 8 новостей
                const newsItem = document.createElement("div");
                newsItem.className = "news-item";
                newsItem.innerHTML = `
                 <img src="${item.image}" alt="Новость">
                 <a href="${item.link}" target="_blank">${item.title}</a>
             `;
                newsContainer.appendChild(newsItem);
            });
        } catch (error) {
            console.error("Ошибка загрузки новостей:", error);
        }
    }

    // Запуск загрузки новостей
    loadRSS();
    loadLocalNews();

    function toggleMenu() {
        document.body.classList.toggle("menu-open");
    }

    // Прокрутка к секции "why-us"
    document.getElementById("scrollToWhyUs").addEventListener("click", function() {
        const section = document.querySelector(".why-us");
        if (section) {
            section.scrollIntoView({ behavior: "smooth" });
        }
    });

    // Открытие WhatsApp при нажатии на "Түсім келеді"
    document.getElementById("applyNow").addEventListener("click", function() {
        window.open("https://wa.me/77071710800?text=%D0%97%D0%B4%D1%80%D0%B0%D0%B2%D1%81%D1%82%D0%B2%D1%83%D0%B9%D1%82%D0%B5!%20%20%D0%A5%D0%BE%D1%82%D0%B5%D0%BB(%D0%B0)%20%D0%B1%D1%8B%20%D1%83%D0%B7%D0%BD%D0%B0%D1%82%D1%8C%20%D0%B8%D0%BD%D1%84%D0%BE%D1%80%D0%BC%D0%B0%D1%86%D0%B8%D1%8E%20%D0%BE%20%D0%BF%D0%BE%D1%81%D1%82%D1%83%D0%BF%D0%BB%D0%B5%D0%BD%D0%B8%D0%B8...", "_blank");
    });

});