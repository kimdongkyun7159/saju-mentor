"""메모리(DB) 모듈 테스트"""

import os
import pytest
import asyncio
from modules.memory.database import Database
from modules.memory.user_profile import UserProfileManager
from modules.memory.chat_history import ChatHistoryManager

TEST_DB = os.path.join(os.path.dirname(__file__), 'test_sajumentor.db')


@pytest.fixture(autouse=True)
def cleanup_db():
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.fixture
def db():
    return Database(TEST_DB)


@pytest.fixture
def profile_mgr():
    return UserProfileManager(TEST_DB)


@pytest.fixture
def history_mgr():
    return ChatHistoryManager(TEST_DB)


class TestDatabase:

    def test_init_creates_db(self, db):
        asyncio.run(db.init())
        assert os.path.exists(TEST_DB)

    def test_init_idempotent(self, db):
        asyncio.run(db.init())
        asyncio.run(db.init())  # 두 번 호출해도 오류 없음
        assert os.path.exists(TEST_DB)


class TestUserProfile:

    def test_create_user(self, db, profile_mgr):
        asyncio.run(db.init())
        user = asyncio.run(profile_mgr.find_or_create(
            '테스트', 1995, 3, 15, 14, gender='male'
        ))
        assert user['nickname'] == '테스트'
        assert user['birth_year'] == 1995
        assert user['id'] is not None

    def test_find_existing_user(self, db, profile_mgr):
        asyncio.run(db.init())
        user1 = asyncio.run(profile_mgr.find_or_create('홍길동', 1990, 1, 1, 0))
        user2 = asyncio.run(profile_mgr.find_or_create('홍길동', 1990, 1, 1, 0))
        assert user1['id'] == user2['id']

    def test_different_users(self, db, profile_mgr):
        asyncio.run(db.init())
        user1 = asyncio.run(profile_mgr.find_or_create('유저A', 1990, 1, 1, 0))
        user2 = asyncio.run(profile_mgr.find_or_create('유저B', 1995, 6, 15, 12))
        assert user1['id'] != user2['id']

    def test_update_saju_data(self, db, profile_mgr):
        asyncio.run(db.init())
        user = asyncio.run(profile_mgr.find_or_create('테스트', 2000, 5, 5, 5))
        saju = {'test': 'data', 'pillars': {'year': {'stem': '경'}}}
        asyncio.run(profile_mgr.update_saju_data(user['id'], saju))
        loaded = asyncio.run(profile_mgr.get_saju_data(user['id']))
        assert loaded['test'] == 'data'


class TestChatHistory:

    def test_add_and_get_message(self, db, profile_mgr, history_mgr):
        asyncio.run(db.init())
        user = asyncio.run(profile_mgr.find_or_create('채팅유저', 1995, 3, 15, 14))
        asyncio.run(history_mgr.add_message(user['id'], 'user', '내 성격이 궁금해요'))
        asyncio.run(history_mgr.add_message(user['id'], 'assistant', '갑목 일간이시군요!'))
        history = asyncio.run(history_mgr.get_history(user['id']))
        assert len(history) == 2
        assert history[0]['role'] == 'user'
        assert history[1]['role'] == 'assistant'

    def test_message_count(self, db, profile_mgr, history_mgr):
        asyncio.run(db.init())
        user = asyncio.run(profile_mgr.find_or_create('카운트유저', 2000, 1, 1, 0))
        for i in range(5):
            asyncio.run(history_mgr.add_message(user['id'], 'user', f'메시지 {i}'))
        count = asyncio.run(history_mgr.get_message_count(user['id']))
        assert count == 5

    def test_recent_context(self, db, profile_mgr, history_mgr):
        asyncio.run(db.init())
        user = asyncio.run(profile_mgr.find_or_create('컨텍스트', 1990, 6, 15, 12))
        asyncio.run(history_mgr.add_message(user['id'], 'user', '안녕하세요'))
        asyncio.run(history_mgr.add_message(user['id'], 'assistant', '반갑습니다'))
        context = asyncio.run(history_mgr.get_recent_context(user['id']))
        assert '사용자: 안녕하세요' in context
        assert '사주멘토: 반갑습니다' in context

    def test_empty_history(self, db, profile_mgr, history_mgr):
        asyncio.run(db.init())
        user = asyncio.run(profile_mgr.find_or_create('빈유저', 2000, 12, 25, 8))
        history = asyncio.run(history_mgr.get_history(user['id']))
        assert len(history) == 0
