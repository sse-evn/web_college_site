#!/bin/bash

LOG_FILE="server.log"

# Функция записи логов
# log() {
#     echo "$(date +"%Y-%m-%d %H:%M:%S") - $1" | tee -a "$LOG_FILE"
# }

log "🚀 Запуск скрипта..."

# Активируем виртуальное окружение Python
if source venv/bin/activate; then
    log "✅ Виртуальное окружение активировано."
else
    log "❌ Ошибка активации виртуального окружения!"
    exit 1
fi

# Запускаем сервер на Node.js в фоне и логируем его вывод
log "🔵 Запуск server.js..."
node server.js >> "$LOG_FILE" 2>&1 &
NODE_PID=$!
sleep 2  # Даем время процессу запуститься

if ps -p $NODE_PID > /dev/null; then
    log "✅ server.js запущен (PID: $NODE_PID)."
else
    log "❌ Ошибка запуска server.js!"
    exit 1
fi

# Запускаем Python-бота и логируем его вывод
log "🤖 Запуск main.py..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
 >> "$LOG_FILE" 2>&1 &
PYTHON_PID=$!
sleep 2  # Даем время процессу запуститься

if ps -p $PYTHON_PID > /dev/null; then
    log "✅ main.py запущен (PID: $PYTHON_PID)."
else
    log "❌ Ошибка запуска main.py!"
    kill $NODE_PID
    exit 1
fi

# Ожидаем завершения Python-бота
wait $PYTHON_PID
log "❌ main.py завершился."

# Проверяем, запущен ли сервер, и останавливаем его
if ps -p $NODE_PID > /dev/null; then
    log "⏹️ Остановка server.js..."
    kill $NODE_PID
    log "✅ server.js остановлен."
else
    log "⚠️ server.js уже был остановлен."
fi

log "🚀 Скрипт завершён."
