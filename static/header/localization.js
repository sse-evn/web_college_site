import { COUNTRIES } from './config.js';

// Локализации
export const translations = {
    ru: {
        "menu.college": "КОЛЛЕДЖ",
        "menu.about": "О НАС",
        "menu.admin": "АДМИНИСТРАЦИЯ",
        "menu.documents": "ДОКУМЕНТЫ",
        "menu.history": "ИСТОРИЯ",
        "menu.applicants": "АБИТУРИЕНТАМ",
        "menu.specialties": "СПЕЦИАЛЬНОСТИ",
        "menu.rules": "ПРАВИЛА ПРИЁМА",
        "menu.exams": "ЭКЗАМЕНЫ",
        "menu.students": "СТУДЕНТАМ",
        "menu.schedule": "РАСПИСАНИЕ",
        "menu.library": "БИБЛИОТЕКА",
        "menu.scholarship": "СТИПЕНДИЯ",
        "menu.news": "НОВОСТИ",
        "menu.contacts": "КОНТАКТЫ",
        "user.role": "ГОСТЬ",
        "location.loading": "Определение...",
        "location.unknown": "Местоположение неизвестно",
        "ip.loading": "Загрузка IP...",
        "logo.subtitle": "CYBERPUNK EDITION",
        "language": "RU"
    },
    kz: {
        "menu.college": "КОЛЛЕДЖ",
        "menu.about": "БІЗ ТУРАЛЫ",
        "menu.admin": "ӘКІМШІЛІК",
        "menu.documents": "ҚҰЖАТТАР",
        "menu.history": "ТАРИХ",
        "menu.applicants": "АБИТУРИЕНТТЕРГЕ",
        "menu.specialties": "МАМАНДЫҚТАР",
        "menu.rules": "ҚАБЫЛДАУ ЕРЕЖЕСІ",
        "menu.exams": "ЫЗДАНЫСТАР",
        "menu.students": "СТУДЕНТТЕРГЕ",
        "menu.schedule": "КЕСТЕ",
        "menu.library": "КІТАПХАНА",
        "menu.scholarship": "СТИПЕНДИЯ",
        "menu.news": "ЖАҢАЛЫҚТАР",
        "menu.contacts": "БАЙЛАНЫС",
        "user.role": "ҚОНАҚ",
        "location.loading": "Анықтау...",
        "location.unknown": "Орналасқан жері белгісіз",
        "ip.loading": "IP жүктелуде...",
        "logo.subtitle": "КИБЕРПАНК БАСЫЛЫМЫ",
        "language": "KZ"
    },
    en: {
        "menu.college": "COLLEGE",
        "menu.about": "ABOUT US",
        "menu.admin": "ADMINISTRATION",
        "menu.documents": "DOCUMENTS",
        "menu.history": "HISTORY",
        "menu.applicants": "APPLICANTS",
        "menu.specialties": "SPECIALTIES",
        "menu.rules": "ADMISSION RULES",
        "menu.exams": "EXAMS",
        "menu.students": "STUDENTS",
        "menu.schedule": "SCHEDULE",
        "menu.library": "LIBRARY",
        "menu.scholarship": "SCHOLARSHIP",
        "menu.news": "NEWS",
        "menu.contacts": "CONTACTS",
        "user.role": "GUEST",
        "location.loading": "Detecting...",
        "location.unknown": "Location unknown",
        "ip.loading": "Loading IP...",
        "logo.subtitle": "CYBERPUNK EDITION",
        "language": "EN"
    }
};

// Текущий язык (по умолчанию берем из атрибута lang у html)
export let currentLang = document.documentElement.lang || 'ru';

// Функция для получения названия страны
export function getCountryName(englishName, lang) {
    if (COUNTRIES[lang] && COUNTRIES[lang][englishName]) {
        return COUNTRIES[lang][englishName];
    }
    return englishName.toUpperCase();
}

// Функция перевода
export function translatePage(lang) {
    currentLang = lang;
    document.documentElement.lang = lang;
    
    // Обновляем язык в переключателе
    document.getElementById('current-language').textContent = translations[lang].language;
    
    // Переводим все элементы с data-key
    document.querySelectorAll('[data-key]').forEach(element => {
        const key = element.getAttribute('data-key');
        if (translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });
    
    // Обновляем статические тексты
    document.getElementById('user-role').textContent = translations[lang]['user.role'];
    document.getElementById('logo-subtitle').textContent = translations[lang]['logo.subtitle'];
    
    // Если местоположение еще не определено, обновляем текст
    const locationElement = document.getElementById('user-location');
    if (locationElement.textContent === translations['ru']['location.loading'] || 
        locationElement.textContent === translations['kz']['location.loading'] || 
        locationElement.textContent === translations['en']['location.loading']) {
        locationElement.textContent = translations[lang]['location.loading'];
    }
    
    // Если IP еще не загружен, обновляем текст
    const ipElement = document.getElementById('ip-address');
    if (ipElement.textContent === translations['ru']['ip.loading'] || 
        ipElement.textContent === translations['kz']['ip.loading'] || 
        ipElement.textContent === translations['en']['ip.loading']) {
        ipElement.textContent = translations[lang]['ip.loading'];
    }
}