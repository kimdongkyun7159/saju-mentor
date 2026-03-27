"""해석 모듈 테스트"""

import pytest
from modules.calculator.core import calculate_saju
from modules.interpreter.base import SajuInterpreter


@pytest.fixture
def saju_male():
    return calculate_saju(1995, 3, 15, 14, gender='male')


@pytest.fixture
def saju_female():
    return calculate_saju(1990, 8, 15, 6, gender='female')


@pytest.fixture
def interpreter():
    return SajuInterpreter()


class TestInterpreter:

    def test_interpret_all_returns_seven_categories(self, interpreter, saju_male):
        result = interpreter.interpret_all(saju_male)
        assert set(result.keys()) == {'personality', 'career', 'love', 'wealth', 'health', 'fortune', 'supplement'}

    def test_personality_has_title(self, interpreter, saju_male):
        result = interpreter.interpret_category(saju_male, 'personality')
        assert 'title' in result
        assert len(result['title']) > 0

    def test_career_has_suitable_jobs(self, interpreter, saju_male):
        result = interpreter.interpret_category(saju_male, 'career')
        assert 'suitable_jobs' in result
        assert len(result['suitable_jobs']) > 0

    def test_love_has_love_style(self, interpreter, saju_female):
        result = interpreter.interpret_category(saju_female, 'love')
        assert 'love_style' in result
        assert len(result['love_style']) > 0

    def test_wealth_has_wealth_base(self, interpreter, saju_male):
        result = interpreter.interpret_category(saju_male, 'wealth')
        assert 'wealth_base' in result

    def test_health_has_warnings(self, interpreter, saju_male):
        result = interpreter.interpret_category(saju_male, 'health')
        assert 'health_warnings' in result
        assert isinstance(result['health_warnings'], list)

    def test_fortune_has_daeun(self, interpreter, saju_male):
        result = interpreter.interpret_category(saju_male, 'fortune')
        assert 'daeun_flow' in result
        assert len(result['daeun_flow']) > 0

    def test_greeting_message(self, interpreter, saju_male):
        greeting = interpreter.get_greeting(saju_male)
        assert '사주멘토' in greeting
        assert '용신' in greeting

    def test_invalid_category(self, interpreter, saju_male):
        result = interpreter.interpret_category(saju_male, 'nonexistent')
        assert 'error' in result
