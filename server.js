require('dotenv').config();
const express = require('express');
const path = require('path');
const session = require('express-session');
const bcrypt = require('bcrypt');
const sqlite3 = require('sqlite3').verbose();
const SQLiteStore = require('connect-sqlite3')(session);
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

const app = express();
const PORT = process.env.PORT || 3000;

// ==================== Инициализация базы данных ====================
const db = new sqlite3.Database('./db/auth.sqlite');

db.serialize(() => {
    // Создаем таблицу пользователей
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'admin',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )`);

    // Создаем администратора по умолчанию
    const adminPassword = process.env.ADMIN_PASSWORD || 'admin123';
    bcrypt.hash(adminPassword, 10, (err, hash) => {
        db.run(`INSERT OR IGNORE INTO users (username, password_hash, role) 
                VALUES (?, ?, ?)`, 
        ['admin', hash, 'admin']);
    });
});

// ==================== Конфигурация ====================
app.use(helmet());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Настройка сессии
app.use(session({
    store: new SQLiteStore({
        db: 'sessions.db',
        dir: './db'
    }),
    secret: process.env.SESSION_SECRET || 'your-secret-key',
    resave: false,
    saveUninitialized: false,
    cookie: {
        secure: process.env.NODE_ENV === 'production',
        httpOnly: true,
        maxAge: 24 * 60 * 60 * 1000 // 24 часа
    }
}));

// ==================== Middleware ====================
// Проверка аутентификации
const requireAuth = (req, res, next) => {
    if (req.session && req.session.user) {
        return next();
    }
    res.status(403).json({ 
        error: 'Требуется авторизация',
        loginUrl: '/login'
    });
};

// Проверка роли администратора
const requireAdmin = (req, res, next) => {
    if (req.session.user && req.session.user.role === 'admin') {
        return next();
    }
    res.status(403).json({ 
        error: 'Недостаточно прав',
        message: 'Требуются права администратора'
    });
};

// ==================== Маршруты аутентификации ====================
// Страница входа
app.get('/login', (req, res) => {
    if (req.session.user) {
        return res.redirect('/admin');
    }
    res.sendFile(path.join(__dirname, 'views', 'login.html'));
});

// Обработка входа
app.post('/login', (req, res) => {
    const { username, password } = req.body;

    if (!username || !password) {
        return res.status(400).json({ 
            error: 'Не указаны учетные данные' 
        });
    }

    db.get('SELECT * FROM users WHERE username = ?', [username], (err, user) => {
        if (err || !user) {
            return res.status(401).json({ 
                error: 'Неверные учетные данные' 
            });
        }

        bcrypt.compare(password, user.password_hash, (err, result) => {
            if (err || !result) {
                return res.status(401).json({ 
                    error: 'Неверные учетные данные' 
                });
            }

            req.session.user = {
                id: user.id,
                username: user.username,
                role: user.role
            };

            res.json({ 
                success: true,
                redirect: '/admin'
            });
        });
    });
});

// Выход
app.post('/logout', (req, res) => {
    req.session.destroy(err => {
        if (err) {
            return res.status(500).json({ 
                error: 'Ошибка при выходе' 
            });
        }
        res.clearCookie('connect.sid');
        res.json({ success: true });
    });
});

// ==================== Админ-панель ====================
// Главная страница админки
app.get('/admin', requireAuth, requireAdmin, (req, res) => {
    res.sendFile(path.join(__dirname, 'views', 'admin', 'dashboard.html'));
});

// API для админ-панели
app.get('/admin/api/users', requireAuth, requireAdmin, (req, res) => {
    db.all('SELECT id, username, role, created_at FROM users', (err, users) => {
        if (err) {
            return res.status(500).json({ 
                error: 'Ошибка базы данных' 
            });
        }
        res.json(users);
    });
});

// ==================== Статические файлы ====================
app.use('/static', express.static(path.join(__dirname, 'static')));
app.use(express.static('public'));

// ==================== Обработка ошибок ====================
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).send('Ошибка сервера');
});

// ==================== Запуск сервера ====================
app.listen(PORT, () => {
    console.log(`Сервер запущен на порту ${PORT}`);
    console.log(`Админ-панель: http://localhost:${PORT}/admin`);
    console.log(`Логин: admin / ${process.env.ADMIN_PASSWORD || 'admin123'}`);
});