import os
import aiosqlite

from src.config import Config
from src.utils.logger import logger


class Database:

    async def init_db(self):

        db_dir = os.path.dirname(Config.DATABASE_PATH)

        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        async with aiosqlite.connect(Config.DATABASE_PATH) as db:

            await db.execute("""
            CREATE TABLE IF NOT EXISTS users(

                user_id INTEGER PRIMARY KEY,

                username TEXT,

                language TEXT DEFAULT 'uz',

                topik_level INTEGER DEFAULT 1,

                goal TEXT DEFAULT 'conversation',

                streak INTEGER DEFAULT 0,

                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

        logger.info("Database tayyorlandi.")


db_client = Database()
