particlesJS("particle-background", {
    particles: {
        number: {
            value: 60, // Уменьшил количество частиц для более "воздушного" эффекта
            density: { enable: true, value_area: 1200 } // Меньшая плотность для элегантности
        },
        color: {
            value: ["#ffccdd", "#ccffdd", "#ddccff", "#ffffff"] // Мягкие пастельные цвета: розовый, мятный, лавандовый, белый
        },
        shape: {
            type: "circle", // Оставляем круги для мягкости
            stroke: { width: 0, color: "#ffffff" } // Без обводки
        },
        opacity: {
            value: 0.6, // Более прозрачные частицы для "сияющего" эффекта
            random: true, // Разная прозрачность для глубины
            anim: {
                enable: true,
                speed: 0.8, // Плавная анимация прозрачности
                opacity_min: 0.2, // Минимальная прозрачность
                sync: false // Асинхронная анимация
            }
        },
        size: {
            value: 5, // Средний размер частиц
            random: true, // Разный размер для естественности
            anim: {
                enable: true,
                speed: 1.5, // Плавная анимация размера
                size_min: 1, // Минимальный размер
                sync: false // Асинхронная анимация
            }
        },
        line_linked: {
            enable: true,
            distance: 180, // Увеличил дистанцию для более "связного" эффекта
            color: "#ffffff", // Белые линии для контраста
            opacity: 0.3, // Полупрозрачные линии для мягкости
            width: 1 // Тонкие линии
        },
        move: {
            enable: true,
            speed: 1.5, // Медленное движение для "парящего" эффекта
            direction: "none", // Случайное движение
            random: true, // Разные направления
            straight: false, // Не прямолинейное движение
            out_mode: "out", // Частицы исчезают за границами
            bounce: false, // Без отскока
            attract: {
                enable: true, // Легкое притяжение частиц друг к другу
                rotateX: 600,
                rotateY: 1200
            }
        }
    },
    interactivity: {
        detect_on: "canvas",
        events: {
            onhover: {
                enable: true,
                mode: "grab" // Эффект "захвата" при наведении
            },
            onclick: {
                enable: true,
                mode: "repulse" // Эффект отталкивания при клике
            },
            resize: true // Адаптация при изменении размера окна
        },
        modes: {
            grab: {
                distance: 250, // Увеличил дистанцию для более заметного эффекта
                line_linked: { opacity: 0.8 } // Линии при наведении чуть ярче
            },
            repulse: {
                distance: 200, // Дистанция отталкивания
                duration: 0.4 // Длительность эффекта
            }
        }
    },
    retina_detect: true // Поддержка Retina-экранов
});