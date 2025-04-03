const express = require("express");
const path = require("path");
const cors = require("cors");
const axios = require("axios");
const parser = require("xml2js");
const { networkInterfaces } = require("os");
const fs = require("fs");
const { Sequelize } = require("sequelize");
const AdminJS = require("adminjs");
const AdminJSExpress = require("@adminjs/express");
const AdminJSSequelize = require("@adminjs/sequelize");

const app = express();
const PORT = 3000;

// ========================== Подключение к Sequelize ==========================
const sequelize = new Sequelize("database", "username", "password", {
    host: "localhost",
    dialect: "mysql", // или 'postgres', 'sqlite', 'mssql'
});

// ========================== Определение моделей ==========================
const User = sequelize.define("User", {
    name: {
        type: Sequelize.STRING,
        allowNull: false,
    },
    email: {
        type: Sequelize.STRING,
        allowNull: false,
        unique: true,
    },
});

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

// ========================== Настройка AdminJS ==========================
AdminJS.registerAdapter(AdminJSSequelize);
const admin = new AdminJS({
    databases: [sequelize],
    rootPath: "/admin",
});
const adminRouter = AdminJSExpress.buildRouter(admin);
app.use(admin.options.rootPath, adminRouter);

// ========================== Основные маршруты ==========================
app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "views", "index.html"));
});

// API: текущий год
app.get("/api/year", (req, res) => {
    res.json({ year: new Date().getFullYear() });
});

// Проксирование изображений
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

// Динамическая загрузка страниц
app.get("/*", (req, res) => {
    const pagePath = path.join(__dirname, "views/college", `${req.params[0]}.html`);
    if (fs.existsSync(pagePath)) {
        res.sendFile(pagePath);
    } else {
        res.status(404).send("404");
    }
});

// ========================== Запуск сервера ==========================
app.listen(PORT, "0.0.0.0", async () => {
    try {
        await sequelize.authenticate();
        console.log("✅ Подключение к базе данных установлено.");
        await sequelize.sync(); // Синхронизация моделей
        console.log("✅ База данных синхронизирована.");
    } catch (error) {
        console.error("❌ Ошибка подключения к базе данных:", error);
    }
    console.log(`✅ Сервер запущен: http://${getLocalIP()}:${PORT}`);
    console.log(`✅ AdminJS: http://${getLocalIP()}:${PORT}/admin`);
});

// Функция определения локального IP
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
