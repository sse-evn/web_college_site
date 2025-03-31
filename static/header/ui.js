import { translatePage } from './localization.js';

// Инициализация переключателя языка
export function initLanguageSwitcher() {
    document.querySelectorAll('.language-option').forEach(option => {
        option.addEventListener('click', function() {
            const lang = this.getAttribute('data-lang');
            translatePage(lang);
            // Сохраняем выбор языка в localStorage
            localStorage.setItem('preferredLanguage', lang);
        });
    });
}

// Проверяем сохраненный язык при загрузке
export function checkSavedLanguage() {
    const savedLang = localStorage.getItem('preferredLanguage');
    if (savedLang && translations[savedLang]) {
        translatePage(savedLang);
    }
}