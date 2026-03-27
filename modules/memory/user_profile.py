"""사용자 프로필 관리 — 닉네임 + 생년월일시로 식별"""

import json
import aiosqlite


class UserProfileManager:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def find_or_create(
        self, nickname: str, birth_year: int, birth_month: int,
        birth_day: int, birth_hour: int, birth_minute: int = 0,
        gender: str = 'male'
    ) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                '''SELECT * FROM users
                   WHERE nickname=? AND birth_year=? AND birth_month=?
                   AND birth_day=? AND birth_hour=?''',
                (nickname, birth_year, birth_month, birth_day, birth_hour)
            )
            row = await cursor.fetchone()
            if row:
                return dict(row)
            await db.execute(
                '''INSERT INTO users (nickname, birth_year, birth_month, birth_day,
                   birth_hour, birth_minute, gender)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (nickname, birth_year, birth_month, birth_day,
                 birth_hour, birth_minute, gender)
            )
            await db.commit()
            cursor = await db.execute(
                'SELECT * FROM users WHERE id=last_insert_rowid()'
            )
            row = await cursor.fetchone()
            return dict(row)

    async def update_saju_data(self, user_id: int, saju_data: dict):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'UPDATE users SET saju_data=? WHERE id=?',
                (json.dumps(saju_data, ensure_ascii=False), user_id)
            )
            await db.commit()

    async def get_user(self, user_id: int) -> dict | None:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('SELECT * FROM users WHERE id=?', (user_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_saju_data(self, user_id: int) -> dict | None:
        user = await self.get_user(user_id)
        if user and user.get('saju_data'):
            return json.loads(user['saju_data'])
        return None
