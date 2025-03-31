// const express = require("express");
// const router = express.Router();
// const fs = require("fs").promises;
// const path = require("path");
// const multer = require("multer");

// const DATA_DIR = path.join(__dirname, "..", "data", "news"); // Папка для хранения новостей
// const DATA_FILE = path.join(DATA_DIR, "news.json");
// const UPLOADS_DIR = path.join(__dirname, "..", "uploads");

// // 📌 Создание папки, если она не существует
// const ensureDirExists = async (dir) => {
//     try {
//         await fs.mkdir(dir, { recursive: true });
//         console.log(`Папка ${dir} проверена/создана`);
//     } catch (error) {
//         console.error(`Ошибка создания папки ${dir}:`, error);
//     }
// };

// // 📌 Инициализация папок при старте
// ensureDirExists(DATA_DIR);
// ensureDirExists(UPLOADS_DIR);

// // Настройка хранения файлов
// const storage = multer.diskStorage({
//     destination: (req, file, cb) => {
//         cb(null, UPLOADS_DIR);
//     },
//     filename: (req, file, cb) => {
//         const uniqueSuffix = Date.now() + "-" + Math.round(Math.random() * 1e9);
//         cb(null, `${uniqueSuffix}-${file.originalname}`);
//     }
// });
// const upload = multer({ storage });

// // Функция загрузки новостей
// const loadNews = async () => {
//     try {
//         await fs.access(DATA_FILE);
//         const data = await fs.readFile(DATA_FILE, "utf-8");
//         return JSON.parse(data);
//     } catch (error) {
//         return [];
//     }
// };

// // Функция сохранения новостей
// const saveNews = async (newsList) => {
//     await ensureDirExists(DATA_DIR); // Проверяем, что папка есть
//     await fs.writeFile(DATA_FILE, JSON.stringify(newsList, null, 2), "utf-8");
// };

// // 📌 Получить список новостей
// router.get("/", async (req, res) => {
//     try {
//         const news = await loadNews();
//         res.json(news);
//     } catch (error) {
//         res.status(500).json({ error: "Ошибка загрузки новостей" });
//     }
// });

// // 📌 Добавить новость с файлом
// router.post("/", upload.single("image"), async (req, res) => {
//     const { text } = req.body;
//     if (!text) {
//         return res.status(400).json({ error: "Текст новости обязателен" });
//     }

//     const news = await loadNews();
//     const imagePath = req.file ? `/uploads/${req.file.filename}` : null;
//     const newNews = { id: Date.now(), text, image: imagePath };
//     news.push(newNews);
//     await saveNews(news);

//     res.status(201).json(newNews);
// });

// // 📌 Удалить новость по индексу
// router.delete("/index/:index", async (req, res) => {
//     let news = await loadNews();
//     const index = parseInt(req.params.index);

//     if (index < 0 || index >= news.length) {
//         return res.status(404).json({ error: "Новость не найдена" });
//     }

//     // Получаем удаляемую новость
//     const newsItem = news[index];

//     // Удаляем изображение, если оно есть
//     if (newsItem.image) {
//         const imagePath = path.join(__dirname, "..", newsItem.image);
//         try {
//             await fs.unlink(imagePath);
//             console.log(`Файл ${imagePath} удален`);
//         } catch (error) {
//             console.error("Ошибка удаления файла:", error);
//         }
//     }

//     // Удаляем новость по индексу
//     news.splice(index, 1);
//     await saveNews(news);

//     res.sendStatus(204);
// });

// // 📌 Удалить все новости и их файлы
// router.delete("/", async (req, res) => {
//     try {
//         const news = await loadNews();
//         for (const item of news) {
//             if (item.image) {
//                 const imagePath = path.join(__dirname, "..", item.image);
//                 await fs.unlink(imagePath).catch(err => console.error("Ошибка удаления файла:", err));
//             }
//         }
//         await saveNews([]);
//         res.json({ message: "Все новости удалены" });
//     } catch (error) {
//         res.status(500).json({ error: "Ошибка удаления новостей" });
//     }
// });

// module.exports = router;
