// const AdminBro = require('admin-bro');
// const AdminBroExpress = require('@admin-bro/express');
// const AdminBroSequelize = require('@admin-bro/sequelize');
// const sequelize = require('./models'); // Путь к твоим моделям Sequelize

// AdminBro.registerAdapter(AdminBroSequelize);

// const adminBro = new AdminBro({
//   databases: [sequelize],
//   rootPath: '/admin',
// });

// const router = AdminBroExpress.buildRouter(adminBro);

// // Подключение к Express
// const express = require('express');
// const app = express();

// app.use(adminBro.options.rootPath, router);
// app.listen(3000, () => console.log('AdminBro запущен на http://localhost:3000/admin'));