"""대화 기록 관리 — 사용자별 채팅 히스토리"""

import aiosqlite


class ChatHistoryManager:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def add_message(
        self, user_id: int, role: str, message: str, category: str = None
    ):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                '''INSERT INTO chat_history (user_id, role, message, category)
                   VALUES (?, ?, ?, ?)''',
                (user_id, role, message, category)
            )
            await db.commit()

    async def get_history(self, user_id: int, limit: int = 50) -> list[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                '''SELECT role, message, category, created_at
                   FROM chat_history
                   WHERE user_id=?
                   ORDER BY id DESC
                   LIMIT ?''',
                (user_id, limit)
            )
            rows = await cursor.fetchall()
            return [dict(r) for r in reversed(rows)]

    async def get_recent_context(self, user_id: int, limit: int = 10) -> str:
        history = await self.get_history(user_id, limit)
        if not history:
            return ''
        lines = []
        for msg in history:
            role = '사용자' if msg['role'] == 'user' else '사주멘토'
            lines.append(f'{role}: {msg["message"]}')
        return '\n'.join(lines)

    async def get_message_count(self, user_id: int) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT COUNT(*) FROM chat_history WHERE user_id=?',
                (user_id,)
            )
            row = await cursor.fetchone()
            return row[0] if row else 0
