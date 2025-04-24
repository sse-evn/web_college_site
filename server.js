require('dotenv').config();
const express = require("express");
const path = require("path");
const cors = require("cors");
const axios = require("axios");
const { networkInterfaces } = require("os");
const fs = require("fs");
const morgan = require("morgan");

const app = express();
const PORT = process.env.PORT || 3000;

// ========================== Настройки Directus ==========================
const DIRECTUS_URL = process.env.DIRECTUS_URL || 'http://localhost:8055';
const DIRECTUS_API_KEY = process.env.DIRECTUS_API_KEY || 'NM_dTn_hkRBjZCAXazqaYVdoRBz6qoaL';

// ========================== Логирование ==========================
app.use(morgan('combined'));

// ========================== CORS ==========================
const allowedOrigins = [
    "http://web.aspc.kz",
    "http://localhost:8055",
    "http://localhost:3000",
    "http://web.aspc.kz:3000"
];

app.use(cors({
    origin: allowedOrigins,
    methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    credentials: true,
    allowedHeaders: ['Content-Type', 'Authorization']
}));

// ========================== Middleware ==========================
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true }));
app.use("/static", express.static(path.join(__dirname, "static")));
app.use(express.static("public"));

// ========================== Главная ==========================
app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "views", "index.html"));
});

// ========================== Прокси для всего Directus ==========================
app.use('/directus', async (req, res) => {
    try {
        const response = await axios({
            method: req.method,
            url: `${DIRECTUS_URL}${req.path.replace('/directus', '')}`,
            headers: {
                'Authorization': `Bearer ${DIRECTUS_API_KEY}`,
                'Content-Type': 'application/json'
            },
            data: req.body,
            params: req.query
        });
        res.json(response.data);
    } catch (error) {
        res.status(error.response?.status || 500).json({
            error: error.message
        });
    }
});

// ========================== Прокси изображений ==========================
app.get("/proxy-image", async (req, res) => {
    try {
        const imageUrl = decodeURIComponent(req.query.url);
        const response = await axios.get(imageUrl, { 
            responseType: "arraybuffer",
            maxContentLength: 10 * 1024 * 1024
        });
        
        const contentType = response.headers['content-type'] || 'image/jpeg';
        res.setHeader("Content-Type", contentType);
        res.send(response.data);
    } catch (error) {
        res.status(500).json({ error: "Ошибка загрузки изображения" });
    }
});

// ========================== API для новостей ==========================
app.get('/api/news', async (req, res) => {
    try {
        const response = await axios.get(`${DIRECTUS_URL}/items/news`, {
            params: {
                fields: 'id,title,content,date,image.*',
                sort: '-date'
            },
            headers: {
                'Authorization': `Bearer ${DIRECTUS_API_KEY}`
            }
        });
        res.json(response.data.data);
    } catch (error) {
        res.status(500).json({ error: 'Ошибка получения новостей' });
    }
});

// ========================== Универсальный роутер для всех HTML ==========================
app.get("/*", (req, res) => {
    const requestPath = req.params[0];
    const cleanPath = requestPath.replace(/\.html$/, '');
    
    const possiblePaths = [
        path.join(__dirname, `${cleanPath}.html`),
        path.join(__dirname, cleanPath, "index.html"),
        path.join(__dirname, cleanPath, "page1.html"),
    ];
    
    for (const filePath of possiblePaths) {
        if (fs.existsSync(filePath)) {
            return res.sendFile(filePath);
        }
    }
    
    res.status(404).sendFile(path.join(__dirname, "views", "404.html"));
});

// ========================== Запуск сервера ==========================
app.listen(PORT, "0.0.0.0", () => {
    console.log(`✅ Сервер запущен: http://${getLocalIP()}:${PORT}`);
    console.log(`Админ-панель Directus: ${DIRECTUS_URL}`);
    console.log(`Доступные домены: ${allowedOrigins.join(', ')}`);
});

// ========================== Вспомогательные функции ==========================
function getLocalIP() {
    const nets = networkInterfaces();
    for (const name of Object.keys(nets)) {
        for (const net of nets[name]) {
            if (net.family === "IPv4" && !net.internal) {
                return net.address;
            }
        }
    }
    return "localhost";
}

// ========================== Обработка ошибок ==========================
process.on("uncaughtException", (err) => {
    console.error("Необработанное исключение:", err);
});

process.on("unhandledRejection", (reason, promise) => {
    console.error("Необработанное отклонение промиса:", promise, "Причина:", reason);
});