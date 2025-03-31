import { initDateTime } from './datetime.js';
import { getExternalIP } from './network.js';
import { initLanguageSwitcher, checkSavedLanguage } from './ui.js';
import { currentLang } from './localization.js';

// Основная функция инициализации
function initApp() {
    // Инициализация даты и времени
    initDateTime();
    
    // Инициализация переключателя языка
    initLanguageSwitcher();
    checkSavedLanguage();
    
    // Получаем внешний IP
    getExternalIP();
}

// Запуск приложения после загрузки DOM
document.addEventListener('DOMContentLoaded', initApp);

// Экспорт текущего языка для возможного использования в других модулях
export { currentLang };