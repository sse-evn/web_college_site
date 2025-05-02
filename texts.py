START_MESSAGE = (
    "👋 Привет! Я бот для приема заявок на техническую помощь.\n"
    "👇 Выберите тип проблемы, с которой вы столкнулись:"
)
CANCEL_MESSAGE = "❌ Создание заявки отменено."
ACCESS_DENIED_ADMIN = "🔒 У вас нет прав администратора для выполнения этого действия."
ACCESS_DENIED_TEACHER = "⛔ У вас нет прав на создание заявок через этого бота. Пожалуйста, обратитесь к администратору."

REQUEST_TYPE_PROMPT = "❓ Выберите тип проблемы или нажмите 'Отмена':"
LOCATION_PROMPT = "📍 Укажите номер кабинета или местоположение:"
NAME_PROMPT = "👤 Укажите ваше имя или имя человека, с которым можно связаться по этой заявке:"
DESCRIPTION_PROMPT = "📝 Опишите проблему как можно подробнее:"

CONFIRMATION_TEXT_TEMPLATE = (
    "✅ Пожалуйста, проверьте данные перед отправкой:\n\n"
    "Тип проблемы: {request_type}\n"
    "Местоположение: {location}\n"
    "Контактное имя: {contact_name}\n"
    "Описание:\n{description}\n\n"
    "🤔 Все верно?"
)
REQUEST_ACCEPTED_MESSAGE = "✨ Ваша заявка принята! Мы скоро с вами свяжемся."

SPAM_PROTECTION_MESSAGE_TEMPLATE = (
    "✋ У вас уже есть {active_requests_count} активных заявок (в работе или открытых).\n"
    "🐢 Пожалуйста, дождитесь их выполнения или отмены ({max_active_requests} максимум), прежде чем создавать новые."
)

ADMIN_PANEL_MESSAGE = "🛠️ Админ-панель:"
ADMIN_NEW_REQUEST_NOTIFICATION_TEMPLATE = (
    "🚨 *Новая заявка №{request_id}!* 🚨\n\n"
    "От кого (Telegram): {teacher_fullname} (ID: {teacher_id}{username_mention})\n"
    "Контактное имя: {contact_name}\n"
    "Тип проблемы: {request_type}\n"
    "Местоположение: {location}\n"
    "Описание: {description}\n\n"
    "Создана: {created_at}"
)

ADMIN_NO_OPEN_REQUESTS = "✅ Нет открытых заявок."
ADMIN_OPEN_REQUESTS_LIST_TEMPLATE = "📋 Открытые заявки:\n\n"
ADMIN_REQUEST_NOT_FOUND = "🔎 Заявка не найдена."

ADMIN_REQUEST_DETAILS_TEMPLATE = (
    "📄 Детали заявки №{request_id}\n\n"
    "Статус: *{status_ru}*\n"
    "От кого (Telegram): {teacher_fullname} (ID: {teacher_id}{username_mention})\n"
    "Контактное имя: {contact_name}\n"
    "Тип проблемы: {request_type}\n"
    "Местоположение: {location}\n"
    "Описание:\n{description}\n\n"
    "Создана: {created_at}\n"
    "Завершено: {completed_at}\n"
)

ADMIN_STATUS_UPDATED_ANSWER_TEMPLATE = "👍 Статус заявки №{request_id} изменен на '{status_ru}'."

ADMIN_NOTIFY_TEACHER_STATUS_TEMPLATE = (
    "📊 Статус вашей заявки №{request_id} ('{request_type} в {location}') изменен на *'{status_ru}'*."
)

ADMIN_LIST_ADMINS_TEMPLATE = "🛠️ Список администраторов:\n\n"
ADMIN_ADMINS_NOT_FOUND = "😔 Администраторы не найдены."
ADMIN_ADMIN_INFO_TEMPLATE = "- {fullname} (ID: {user_id}{username_mention})"

ADMIN_ADD_ADMIN_PROMPT = "➕ Введите Telegram User ID пользователя, которого хотите сделать администратором:"
ADMIN_ADD_ADMIN_SUCCESS_TEMPLATE = "✨ Пользователь с ID {user_id} успешно добавлен в список администраторов."
ADMIN_ADD_ADMIN_ALREADY_ADMIN_TEMPLATE = "❗️ Пользователь с ID {user_id} уже является администратором."

ADMIN_REMOVE_ADMIN_PROMPT = "➖ Введите Telegram User ID пользователя, которого хотите удалить из списка администраторов:"
ADMIN_REMOVE_ADMIN_SELF = "🚫 Вы не можете удалить самого себя из списка администраторов!"
ADMIN_REMOVE_ADMIN_SUCCESS_TEMPLATE = "🗑️ Пользователь с ID {user_id} успешно удален из списка администраторов."
ADMIN_REMOVE_ADMIN_NOT_FOUND_TEMPLATE = "🔎 Пользователь с ID {user_id} не найден в списке администраторов."
ADMIN_REMOVE_ADMIN_LAST_ADMIN = "❌ Нельзя удалить последнего администратора!"

ADMIN_LIST_TEACHERS_TEMPLATE = "👩‍🏫 Список разрешенных учителей:\n\n"
ADMIN_TEACHERS_NOT_FOUND = "😔 Разрешенные учителя не найдены."
ADMIN_TEACHER_INFO_TEMPLATE = "- {user_id}"

ADMIN_ADD_TEACHER_PROMPT = "➕ Введите Telegram User ID пользователя, которого хотите добавить в список разрешенных учителей:"
ADMIN_ADD_TEACHER_SUCCESS_TEMPLATE = "✨ Пользователь с ID {user_id} успешно добавлен в список разрешенных учителей."
ADMIN_ADD_TEACHER_ALREADY_ALLOWED_TEMPLATE = "❗️ Пользователь с ID {user_id} уже находится в списке разрешенных учителей или является администратором."

ADMIN_REMOVE_TEACHER_PROMPT = "➖ Введите Telegram User ID пользователя, которого хотите удалить из списка разрешенных учителей:"
ADMIN_REMOVE_TEACHER_SUCCESS_TEMPLATE = "🗑️ Пользователь с ID {user_id} успешно удален из списка разрешенных учителей."
ADMIN_REMOVE_TEACHER_NOT_FOUND_TEMPLATE = "🔎 Пользователь с ID {user_id} не найден в списке разрешенных учителей."

ADMIN_INVALID_ID = "🔢❌ Некорректный User ID. Пожалуйста, введите только числовой ID."
ADMIN_ACTION_ERROR = "⚠️ Произошла ошибка при выполнении действия."

STATUS_MAP_RU = {
    'open': 'Открыта',
    'in_progress': 'В работе',
    'completed': 'Завершена',
    'cancelled': 'Отменена'
}

ADMIN_NO_COMPLETED_REQUESTS = "✅ Нет завершенных заявок."
ADMIN_COMPLETED_REQUESTS_LIST_TEMPLATE = "📋 Завершенные заявки:\n\n"

ADMIN_NO_REQUESTS_HISTORY = "😔 История заявок пуста."
ADMIN_ALL_REQUESTS_LIST_TEMPLATE = "📊 История всех заявок:\n\n"
ADMIN_HISTORY_ITEM_TEMPLATE = (
    "№{request_id} - {request_type} в {location}\n"
    "От: {teacher_fullname} (ID: {teacher_id}{username_mention})\n"
    "Статус: *{status_ru}*\n"
    "Создана: {created_at}\n"
    "Завершена: {completed_at_formatted}\n"
)

ADMIN_CLEAR_HISTORY_CONFIRM_PROMPT = "⚠️ Вы уверены, что хотите полностью очистить историю всех заявок? Это действие необратимо."
ADMIN_CLEAR_HISTORY_SUCCESS = "🗑️ История заявок успешно очищена."
ADMIN_CLEAR_HISTORY_CANCELLED = "✅ Очистка истории отменена."
ADMIN_CLEAR_HISTORY_NO_DATA = "🤷‍♀️ Нет заявок для очистки."

ADMIN_EXPORT_HISTORY_MESSAGE = "📥 Подготавливаю и отправляю историю заявок..."
ADMIN_EXPORT_HISTORY_NO_DATA = "🤷‍♀️ Нет истории для экспорта."
ADMIN_EXPORT_HISTORY_FILE_TITLE = "История_заявок"

TEACHER_RATING_REQUEST_TEMPLATE = (
    "✅ Ваша заявка №{request_id} ('{request_type} в {location}') завершена.\n\n"
    "Будем благодарны, если вы оцените качество выполненных работ по шкале от 1 до 10:"
)
TEACHER_RATING_THANK_YOU = "✨ Спасибо за вашу оценку!"
TEACHER_RATING_ALREADY_RATED = "❗️ Вы уже оценили эту заявку."
TEACHER_RATING_INVALID_REQUEST = "❌ Не удалось оценить заявку. Возможно, она не найдена или не завершена."

TEACHER_NO_ACTIVE_REQUESTS = "У вас нет активных заявок."
TEACHER_ACTIVE_REQUESTS_LIST_TEMPLATE = "📊 Ваши активные заявки:\n\n"

ADMIN_TAKEN_BY_TEMPLATE = "Взял в работу: {admin_fullname} (ID: {admin_id}{username_mention})\n"

ADMIN_MANUAL_STATUS_PROMPT = "🔧 Выберите новый статус для заявки №{request_id}:"
ADMIN_MANUAL_STATUS_SUCCESS_TEMPLATE = "👍 Статус заявки №{request_id} вручную изменен на '{status_ru}'."
ADMIN_MANUAL_STATUS_CANCELLED = "✅ Изменение статуса вручную отменено."
ADMIN_MANUAL_STATUS_REQUEST_NOT_FOUND = "🔎 Заявка №{request_id} не найдена для ручного изменения статуса."
