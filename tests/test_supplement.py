"""오행 보충/사주 보완 해석 테스트 (Red → Green)"""

import pytest
from modules.calculator.core import calculate_saju
from modules.interpreter.base import SajuInterpreter
from modules.interpreter.patterns.supplement import interpret_supplement


@pytest.fixture
def saju_male():
    return calculate_saju(1995, 3, 15, 14, gender='male')


@pytest.fixture
def saju_female():
    return calculate_saju(1990, 8, 15, 6, gender='female')


@pytest.fixture
def interpreter():
    return SajuInterpreter()


class TestSupplementPattern:
    """오행 보충 패턴 모듈 직접 테스트"""

    def test_returns_category(self, saju_male):
        result = interpret_supplement(saju_male.to_dict())
        assert result['category'] == '오행보충'

    def test_has_overall_balance(self, saju_male):
        result = interpret_supplement(saju_male.to_dict())
        assert 'overall_balance' in result
        assert len(result['overall_balance']) > 50  # 충분히 길어야 함

    def test_has_supplement_list(self, saju_male):
        result = interpret_supplement(saju_male.to_dict())
        assert 'supplements' in result
        assert isinstance(result['supplements'], list)

    def test_supplement_has_required_fields(self, saju_male):
        result = interpret_supplement(saju_male.to_dict())
        if result['supplements']:
            s = result['supplements'][0]
            assert 'element' in s
            assert 'status' in s
            assert 'colors' in s
            assert 'directions' in s
            assert 'foods' in s
            assert 'activities' in s
            assert 'season' in s
            assert 'numbers' in s
            assert 'career_env' in s
            assert 'daily_tips' in s

    def test_has_yongsin_supplement(self, saju_male):
        result = interpret_supplement(saju_male.to_dict())
        assert 'yongsin_supplement' in result
        assert len(result['yongsin_supplement']) > 50

    def test_has_strength_advice(self, saju_male):
        result = interpret_supplement(saju_male.to_dict())
        assert 'strength_advice' in result
        assert len(result['strength_advice']) > 50

    def test_has_seasonal_guide(self, saju_male):
        result = interpret_supplement(saju_male.to_dict())
        assert 'seasonal_guide' in result
        assert len(result['seasonal_guide']) > 30

    def test_has_naming_advice(self, saju_male):
        result = interpret_supplement(saju_male.to_dict())
        assert 'naming_advice' in result

    def test_female_saju_also_works(self, saju_female):
        result = interpret_supplement(saju_female.to_dict())
        assert result['category'] == '오행보충'
        assert len(result['supplements']) >= 0  # 균형 잡힌 사주면 0일 수도


class TestSupplementViaInterpreter:
    """SajuInterpreter를 통한 supplement 카테고리 호출"""

    def test_interpret_category_supplement(self, interpreter, saju_male):
        result = interpreter.interpret_category(saju_male, 'supplement')
        assert result['category'] == '오행보충'
        assert 'supplements' in result

    def test_interpret_all_includes_supplement(self, interpreter, saju_male):
        result = interpreter.interpret_all(saju_male)
        assert 'supplement' in result
        assert result['supplement']['category'] == '오행보충'


class TestSupplementFormatting:
    """service.py의 format_interpretation에서 supplement 포맷 테스트"""

    def test_format_supplement_response(self, interpreter, saju_male):
        from modules.chat.service import format_interpretation
        result = interpreter.interpret_category(saju_male, 'supplement')
        formatted = format_interpretation('supplement', result)
        assert '보충' in formatted or '보완' in formatted
        assert len(formatted) > 200  # 충분히 긴 응답


class TestContextualResponse:
    """자유 대화에서 보완 질문 감지 테스트"""

    def test_detect_supplement_category(self):
        from modules.chat.service import detect_category
        assert detect_category('사주 보완하는 방법 알려줘') == 'supplement'
        assert detect_category('부족한 오행 보충하려면?') == 'supplement'
        assert detect_category('나한테 맞는 색상이 뭐야?') == 'supplement'
        assert detect_category('용신 활용법 알려줘') == 'supplement'

    def test_detect_existing_categories_unchanged(self):
        from modules.chat.service import detect_category
        assert detect_category('내 성격이 궁금해') == 'personality'
        assert detect_category('직업 적성은?') == 'career'
        assert detect_category('연애운 알려줘') == 'love'
