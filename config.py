import os

BOT_TOKEN = os.getenv('BOT_TOKEN', '7532615064:AAEJdQWA1XknjVgwEIgNu7fXMNQWoK1EJpk')

ADMIN_NOTIFICATION_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID', '5233316360'))
DISPLAY_TIMEZONE = "Asia/Almaty"
DATA_FILE = 'data.json'

INITIAL_ADMIN_IDS = [
    int(os.getenv('INITIAL_ADMIN_ID_1', '5233316360')),
]

INITIAL_ALLOWED_TEACHER_IDS = [
     int(os.getenv('INITIAL_TEACHER_ID_1', '5233316360')),
]

INITIAL_SUPPORT_STAFF_IDS = [
    # Добавьте ID начальных ИТ-специалистов, если нужно:
    # int(os.getenv('INITIAL_SUPPORT_STAFF_ID_1', 'ДРУГОЙ_ИТ_СПЕЦИАЛИСТ_ID')),
]

MAX_ACTIVE_REQUESTS_PER_USER = 3

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
