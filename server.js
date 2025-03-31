const express = require("express");
const path = require("path");
const cors = require("cors");
const axios = require("axios");
const parser = require("xml2js");
const { networkInterfaces } = require("os");
const fs = require("fs");

const app = express();
const PORT = 3000;

// ========================== Настройки CORS ==========================
const allowedOrigins = [
    "http://web.aspc.kz",
    "http://10.40.0.23:9000",
    "http://localhost:3000",
];

app.use(cors({
    origin: allowedOrigins,
    methods: ["GET", "POST"],
}));

// ========================== Статические файлы ==========================
app.use("/static", express.static(path.join(__dirname, "static")));
app.use(express.static("public"));

// ========================== Основные маршруты ==========================

// Главная страница
app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "views", "index.html"));
});

// ========================== API ==========================
// API: текущий год (Current year)
app.get("/api/year", (req, res) => {
    res.json({ year: new Date().getFullYear() }); // e.g., {"year": 2025}
});

// ========================== Проксирование изображений ==========================
app.get("/proxy-image", async (req, res) => {
    try {
        const imageUrl = decodeURIComponent(req.query.url);
        const response = await axios.get(imageUrl, { responseType: "arraybuffer" });
        res.setHeader("Content-Type", "image/jpeg");
        res.send(response.data);
    } catch (error) {
        res.status(500).json({ error: "Ошибка загрузки изображения" });
    }
});

// ========================== Динамическая загрузка страниц ==========================
// This must come AFTER specific routes like /api/year
app.get("/*", (req, res) => {
    const pagePath = path.join(__dirname, "views/college", `${req.params[0]}.html`);
    if (fs.existsSync(pagePath)) {
        res.sendFile(pagePath);
    } else {
        res.status(404).send("404");
    }
});

// ========================== Запуск сервера ==========================
app.listen(PORT, "0.0.0.0", () => {
    console.log(`✅ Сервер запущен: http://${getLocalIP()}:${PORT}`);
});

// ========================== Функция определения локального IP ==========================
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