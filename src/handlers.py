from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router, F
from src.middleware import DBMiddleware
from src.states import ReminderSaver
import datetime
import sqlite3
import time

router = Router()
HELP_MESSAGE = """Hello! This is a reminder bot. It has the following commands:
/start, /help - display this message.
/remind - add a reminder.
/cancel - cancel adding a reminder."""


@router.message(Command(commands=["start", "help"]), StateFilter(None))
async def help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(HELP_MESSAGE)


@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Canceled!")


@router.message(Command("remind"), StateFilter(None))
async def remind(message: Message, con: sqlite3.Connection, state: FSMContext):
    await message.answer("First, send me the text of your reminder.")
    await state.set_state(ReminderSaver.reminder_text)


@router.message(F.text, ReminderSaver.reminder_text)
async def get_reminder_text(message: Message, state: FSMContext):
    await state.update_data(reminder_text=message.md_text)
    await message.answer(
        "Fine. Now, send me the date, when I should remind you. It should be in ISO format."
    )
    await state.set_state(ReminderSaver.reminder_time)


@router.message(ReminderSaver.reminder_text)
async def wrong_reminder_text(message: Message):
    await message.answer(
        "Something is wrong! Please, try again. Perhaps, this is not a text."
    )


@router.message(F.text, ReminderSaver.reminder_time)
async def get_reminder_date(
    message: Message, state: FSMContext, con: sqlite3.Connection
):
    try:
        d = datetime.datetime.fromisoformat(message.text)
    except ValueError:
        await message.answer("Wrong date!")
    else:
        if d.timestamp() < time.time():
            await message.answer(
                "This has already happened! Try entering another date!"
            )
            return
        await message.answer(f"Good! I will remind you on {d}.")
        cur = con.cursor()
        user_data = await state.get_data()
        cur.execute(
            "INSERT INTO reminders VALUES(NULL, ?, ?, ?)",
            (message.from_user.id, user_data["reminder_text"], d.timestamp()),
        )
        con.commit()
        await state.clear()


@router.message(ReminderSaver.reminder_time)
async def wrong_reminder_date(message: Message, state: FSMContext):
    await message.answer(
        "Something is wrong! Please, try again. Perhaps, the date is incorrect."
    )


router.message.middleware(DBMiddleware())
