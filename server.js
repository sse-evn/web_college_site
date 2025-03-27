const express = require("express");
const path = require("path");
const cors = require("cors");
const axios = require("axios");
const parser = require("xml2js");
const { networkInterfaces } = require("os");

const app = express();
const PORT = 3000;

// Включаем CORS для запросов
app.use(cors());

// Раздача статических файлов (CSS, JS, изображения)
app.use("/static", express.static(path.join(__dirname, "static")));
app.use(express.static("public"));

// Отдаём главную страницу
app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "views", "index.html"));
});

// API для получения текущего года
app.get("/api/year", (req, res) => {
    res.json({ year: new Date().getFullYear() });
});

// RSS-лента
const RSS_FEED_URL = "https://rss.app/feeds/ROqxpqxtrig12IhL.xml";

// Эндпоинт для получения новостей
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

// Прокси для загрузки изображений
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

// Запуск сервера
app.listen(PORT, "0.0.0.0", () => {
    console.log(`✅ Сервер доступен по локальной сети: http://${getLocalIP()}:${PORT}`);
});

// Функция для получения локального IP-адреса
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