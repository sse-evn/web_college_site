const bcrypt = require('bcrypt');
const session = require('express-session');

// Настройка сессий
app.use(session({
    secret: 'your-secret-key',
    resave: false,
    saveUninitialized: true,
    cookie: { secure: false } // Для production установите secure: true
}));

// Маршруты для входа/выхода
app.get('/admin/login', (req, res) => {
    res.sendFile(path.join(__dirname, "views", "admin.login.html"));
});

app.post('/admin/login', async (req, res) => {
    const { username, password } = req.body;
    
    // Проверка учетных данных (в реальном приложении - проверка в БД)
    if (username === 'admin' && password === 'securepassword') {
        req.session.isAdmin = true;
        res.redirect('/admin');
    } else {
        res.status(401).send('Неверные учетные данные');
    }
});

app.get('/logout', (req, res) => {
    req.session.destroy();
    res.redirect('/');
});