from aiogram import BaseMiddleware
import sqlite3


class DBMiddleware(BaseMiddleware):
    def __init__(self, file_name: str = "db.sqlite3"):
        self.file_name = file_name
        self.con = sqlite3.connect(self.file_name)
        cur = self.con.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS
            reminders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            reminder_text TEXT,
            reminder_date INTEGER)"""
        )

    async def __call__(self, handler, event, data):
        data["con"] = self.con
        return await handler(event, data)
