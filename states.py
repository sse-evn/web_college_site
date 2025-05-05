from aiogram.fsm.state import State, StatesGroup

class RequestStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_location = State()
    waiting_for_name = State()
    waiting_for_description = State()
    confirm_request = State()

class AdminStates(StatesGroup):
    waiting_for_admin_id_to_add = State()
    waiting_for_admin_id_to_remove = State()
    waiting_for_teacher_id_to_add = State()
    waiting_for_teacher_id_to_remove = State()
    waiting_for_clear_history_confirmation = State()
    waiting_for_manual_status_selection = State()
    waiting_for_support_staff_id_to_add = State()
    waiting_for_support_staff_id_to_remove = State()


class SupportStaffStates(StatesGroup):
    waiting_for_request_selection = State()

class TeacherRatingState(StatesGroup):
    waiting_for_rating = State()
