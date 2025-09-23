from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher
from src.handlers import router
import asyncio
import sqlite3
import os


async def start_reminders_polling(bot: Bot):
    con = sqlite3.connect("db.sqlite3")
    cur = con.cursor()
    while True:
        reminders = cur.execute(
            """SELECT user_id, reminder_text
            FROM reminders
            WHERE reminder_date <= unixepoch('now')"""
        ).fetchall()
        for user_id, text in reminders:
            await bot.send_message(
                user_id,
                f"Reminder:\n\n{text}",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        cur.execute(
            "DELETE FROM reminders WHERE reminder_date <= unixepoch('now')"
        )
        con.commit()
        await asyncio.sleep(60)


async def main():
    bot = Bot(os.getenv("TOKEN"))
    dp = Dispatcher()
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    async with asyncio.TaskGroup() as tg:
        tg.create_task(dp.start_polling(bot))
        tg.create_task(start_reminders_polling(bot))


if __name__ == "__main__":
    asyncio.run(main())
