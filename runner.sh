#!/bin/bash

# Переходим в каталог с проектом Directus
echo "Запуск Directus..."
cd /home/evn/Documents/web_college_site/directus-app

# Запускаем Directus в фоне
npx directus start &

# Переходим в каталог с проектом сервера
echo "Запуск сервера..."
cd /home/evn/Documents/web_college_site

# Запускаем сервер
node server.js &
