from aiogram.fsm.state import State, StatesGroup


class ReminderSaver(StatesGroup):
    reminder_text = State()
    reminder_time = State()
