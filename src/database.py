import aiosqlite
import os
from src.config import Config
from src.utils.logger import logger

class Database:
    def __init__(self):
        db_dir = os.path.dirname(Config.DATABASE_PATH)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    async def init_db(self):
        async with aiosqlite.connect(Config.DATABASE_PATH) as db:
            # Kelajakdagi funksiyalar (XP, topshiriqlar) uchun maydonlar qo'shildi
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    topik_level INTEGER DEFAULT 1,
                    daily_streak INTEGER DEFAULT 0,
                    language TEXT DEFAULT 'ko',
                    xp INTEGER DEFAULT 0,
                    mission_completed INTEGER DEFAULT 0,
                    last_seen TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    role TEXT,
                    message TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
        logger.info("Kengaytirilgan SQLite ma'lumotlar bazasi tayyor.")

    async def add_user(self, user_id: int, username: str):
        async with aiosqlite.connect(Config.DATABASE_PATH) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
                (user_id, username)
            )
            await db.commit()

    async def save_message(self, user_id: int, role: str, message: str):
        async with aiosqlite.connect(Config.DATABASE_PATH) as db:
            await db.execute(
                "INSERT INTO history (user_id, role, message) VALUES (?, ?, ?)",
                (user_id, role, message)
            )
            await db.commit()

    async def get_history(self, user_id: int, limit: int = 20) -> list:
        async with aiosqlite.connect(Config.DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT role, message FROM history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit)
            )
            rows = await cursor.fetchall()
            # Tarixni to'g'ri xronologik tartibga keltirish
            history = [{"role": row["role"], "text": row["message"]} for row in reversed(rows)]
            return history

db_client = Database()
          
