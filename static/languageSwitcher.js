document.addEventListener("DOMContentLoaded", () => {
    const languageSelector = document.getElementById("language-select"); // Исправил ID на твой из HTML
    const elementsToTranslate = document.querySelectorAll("[data-translate]");

    // Функция установки языка
    const setLanguage = (lang) => {
        localStorage.setItem("selectedLanguage", lang); // Исправил ключ на твой из предыдущего кода
        elementsToTranslate.forEach(element => {
            const key = element.getAttribute("data-translate");
            element.textContent = translations[lang]?.[key] || `Missing translation: ${key}`; // Fallback для отсутствующих переводов
        });
    };

    // Получение сохранённого языка или "ru" по умолчанию
    const savedLanguage = localStorage.getItem("selectedLanguage") || "ru";
    setLanguage(savedLanguage);

    // Проверка и установка слушателя для переключателя
    if (languageSelector) {
        languageSelector.value = savedLanguage;
        languageSelector.addEventListener("change", (event) => setLanguage(event.target.value));
    } else {
        console.warn("Переключатель языка (#language-select) не найден на странице.");
    }
});