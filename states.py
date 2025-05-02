from aiogram.fsm.state import State, StatesGroup

# --- Состояния для FSM пользователя (создание заявки) ---
class RequestStates(StatesGroup):
    """Состояния для процесса создания заявки пользователем."""
    waiting_for_type = State()
    waiting_for_location = State()
    waiting_for_name = State()
    waiting_for_description = State()
    confirm_request = State()

# --- Состояния для FSM админа (управление админами/учителями) ---
class AdminStates(StatesGroup):
    """Состояния для процессов управления администраторами и учителями."""
    # Состояния для управления админами
    waiting_for_admin_id_to_add = State()
    waiting_for_admin_id_to_remove = State()
    # Состояния для управления учителями
    waiting_for_teacher_id_to_add = State() # <-- Новое состояние
    waiting_for_teacher_id_to_remove = State() # <-- Новое состояние
