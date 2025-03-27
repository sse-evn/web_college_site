const express = require("express");
const path = require("path");
const cors = require("cors");
const axios = require("axios");
const parser = require("xml2js");
const { networkInterfaces } = require("os");
const fs = require("fs");

const app = express();
const PORT = 3000;

// ========================== Миддлвары и статические файлы ==========================
// Подключаем CORS (разрешает запросы с других доменов)
app.use(cors());

// Делаем папку "static" доступной по пути "/static" (для стилей, скриптов, изображений)
app.use("/static", express.static(path.join(__dirname, "static")));

// Делаем папку "public" доступной напрямую (например, файлы можно открыть в браузере)
app.use(express.static("public"));

// ========================== Основные маршруты ==========================

// Отдаём главную страницу при запросе к корню сайта ("/")
app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "views", "index.html"));
});

// Динамическое добавление HTML страниц из папки views
// Любой .html файл в "views" становится доступен по его названию в URL
// Пример: если есть файл "views/about.html", он будет доступен по адресу "http://localhost:3000/about"
app.get("/:page", (req, res) => {
    const pagePath = path.join(__dirname, "views", `${req.params.page}.html`);
    if (fs.existsSync(pagePath)) {
        res.sendFile(pagePath);
    } else {
        res.status(404).send("Страница не найдена. Проверьте, есть ли такой файл в папке views.");
    }
});

// ========================== API ==========================

// Простейшее API: выдаёт текущий год
// Запрос: GET http://localhost:3000/api/year
// Ответ: { "year": 2025 }
app.get("/api/year", (req, res) => {
    res.json({ year: new Date().getFullYear() });
});

// ========================== RSS-лента (новости) ==========================
const RSS_FEED_URL = "https://rss.app/feeds/ROqxpqxtrig12IhL.xml";

// Загружаем и парсим RSS-ленту новостей
// Запрос: GET http://localhost:3000/news
// Ответ: массив объектов с заголовком, ссылкой и изображением
app.get("/news", async(req, res) => {
    try {
        const response = await axios.get(RSS_FEED_URL);
        parser.parseString(response.data, (err, result) => {
            if (err) {
                return res.status(500).json({ error: "Ошибка обработки RSS" });
            }
            const items = result.rss.channel[0].item.map((item) => ({
                title: item.title[0],
                link: item.link[0],
                image: `/proxy-image?url=${encodeURIComponent(item["media:content"][0].$.url)}`
            }));
            res.json(items);
        });
    } catch (error) {
        res.status(500).json({ error: "Ошибка загрузки новостей" });
    }
});

// ========================== Проксирование изображений ==========================
// Позволяет загружать изображения по URL через наш сервер
// Нужно для обхода CORS-запретов при загрузке картинок с других сайтов
// Запрос: GET http://localhost:3000/proxy-image?url={ссылка_на_изображение}
app.get("/proxy-image", async(req, res) => {
    try {
        const imageUrl = decodeURIComponent(req.query.url);
        const response = await axios.get(imageUrl, { responseType: "arraybuffer" });
        res.setHeader("Content-Type", "image/jpeg");
        res.send(response.data);
    } catch (error) {
        res.status(500).json({ error: "Ошибка загрузки изображения" });
    }
});

// ========================== Запуск сервера ==========================
// Запускаем сервер на 0.0.0.0 (доступен из локальной сети) и порту 3000
app.listen(PORT, "0.0.0.0", () => {
    console.log(`✅ Сервер доступен по локальной сети: http://${getLocalIP()}:${PORT}`);
});

// ========================== Функция получения локального IP ==========================
// Определяет локальный IP-адрес компьютера для удобства доступа к серверу в сети
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