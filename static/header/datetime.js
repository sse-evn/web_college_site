import { MONTHS } from './config.js';
import { currentLang } from './localization.js';

// Обновление даты и времени с учетом языка
export function updateDateTime() {
    const now = new Date();
    
    const day = now.getDate();
    const month = MONTHS[currentLang][now.getMonth()];
    const year = now.getFullYear();
    
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    
    document.getElementById('current-date').textContent = `${day} ${month} ${year}`;
    document.getElementById('current-time').textContent = `${hours}:${minutes}:${seconds}`;
}

// Инициализация и обновление каждую секунду
export function initDateTime() {
    updateDateTime();
    setInterval(updateDateTime, 1000);
}