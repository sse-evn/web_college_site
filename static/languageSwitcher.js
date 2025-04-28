document.addEventListener("DOMContentLoaded", () => {
    const languageSelector = document.getElementById("language-select");
    const elementsToTranslate = document.querySelectorAll("[data-translate]"); // Элементы для перевода
    const rulesFrame = document.getElementById("rulesFrame"); // Наш iframe с правилами

    // Функция смены языка
    const setLanguage = (lang) => {
        localStorage.setItem("selectedLanguage", lang); // Сохраняем выбранный язык

        // Обновляем текст на странице (перевод элементов)
        elementsToTranslate.forEach(element => {
            const key = element.getAttribute("data-translate");
            element.textContent = translations[lang]?.[key] || `Missing translation: ${key}`; // Если нет перевода, показываем предупреждение
        });

        // Обновляем содержимое iframe
        let iframeSrc = "";
        if (lang === "kz") {
            iframeSrc = "kk.html";
        } else if (lang === "ru") {
            iframeSrc = "ru.html";
        } else if (lang === "en") {
            iframeSrc = "en.html"; // Указываем файл для английского языка
        }

        // Очищаем и перезагружаем iframe
        if (rulesFrame) {
            rulesFrame.src = ""; // Очищаем текущий src
            setTimeout(() => {
                rulesFrame.src = iframeSrc; // Устанавливаем новый src
            }, 100); // Задержка, чтобы iframe успел перезагрузиться
        }
    };

    // Загрузка сохранённого языка из localStorage или по умолчанию "kz"
    const savedLanguage = localStorage.getItem("selectedLanguage") || "kz";
    setLanguage(savedLanguage); // Устанавливаем язык на основе сохранённого значения

    // Устанавливаем значение в селекторе языка и добавляем слушатель для изменения
    if (languageSelector) {
        languageSelector.value = savedLanguage;
        languageSelector.addEventListener("change", (event) => setLanguage(event.target.value));
    } else {
        console.warn("Переключатель языка (#language-select) не найден на странице.");
    }
});
