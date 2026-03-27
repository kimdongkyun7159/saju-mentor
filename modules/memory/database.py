"""SQLite 데이터베이스 관리"""

import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'sajumentor.db')


class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    async def init(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nickname TEXT NOT NULL,
                    birth_year INTEGER NOT NULL,
                    birth_month INTEGER NOT NULL,
                    birth_day INTEGER NOT NULL,
                    birth_hour INTEGER NOT NULL,
                    birth_minute INTEGER DEFAULT 0,
                    gender TEXT NOT NULL DEFAULT 'male',
                    saju_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(nickname, birth_year, birth_month, birth_day, birth_hour)
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            await db.execute('''
                CREATE INDEX IF NOT EXISTS idx_chat_user
                ON chat_history(user_id, created_at DESC)
            ''')
            await db.commit()

    async def get_connection(self):
        return await aiosqlite.connect(self.db_path)
