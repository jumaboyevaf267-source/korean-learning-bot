import os
import aiosqlite

from src.config import Config
from src.utils.logger import logger


class Database:

    async def init_db(self):

        os.makedirs("src/database", exist_ok=True)

        async with aiosqlite.connect(Config.DATABASE_PATH) as db:

            await db.execute("""
            CREATE TABLE IF NOT EXISTS users(
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                language TEXT DEFAULT 'uz',
                goal TEXT DEFAULT '',
                premium INTEGER DEFAULT 0,
                streak INTEGER DEFAULT 0
            )
            """)

            await db.execute("""
            CREATE TABLE IF NOT EXISTS history(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                role TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            await db.commit()

        logger.info("Database tayyor.")


    async def add_user(self, user_id, username):

        async with aiosqlite.connect(Config.DATABASE_PATH) as db:

            await db.execute(
                """
                INSERT OR IGNORE INTO users(user_id,username)
                VALUES(?,?)
                """,
                (user_id, username)
            )

            await db.commit()


    async def save_message(self,user_id,role,message):

        async with aiosqlite.connect(Config.DATABASE_PATH) as db:

            await db.execute(
                """
                INSERT INTO history(user_id,role,message)
                VALUES(?,?,?)
                """,
                (user_id,role,message)
            )

            await db.commit()


    async def get_history(self,user_id,limit=15):

        async with aiosqlite.connect(Config.DATABASE_PATH) as db:

            cursor=await db.execute(
                """
                SELECT role,message
                FROM history
                WHERE user_id=?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id,limit)
            )

            rows=await cursor.fetchall()

        rows.reverse()

        return [
            {
                "role":r[0],
                "text":r[1]
            }
            for r in rows
        ]


db_client=Database()
