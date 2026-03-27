"""채팅 서비스 테스트 — 카테고리 감지, 스코어링, 포맷팅"""

import pytest
from modules.chat.service import (
    detect_category, calculate_scores, format_score_header,
    format_lucky_items, format_oheng_bar, format_interpretation,
)
from modules.calculator.core import calculate_saju
from modules.interpreter.base import SajuInterpreter


@pytest.fixture
def saju_data():
    result = calculate_saju(1990, 5, 15, 12, gender='male')
    return result.to_dict()


@pytest.fixture
def interpreter():
    return SajuInterpreter()


class TestCategoryDetection:
    def test_personality_keywords(self):
        assert detect_category('내 성격이 궁금해요') == 'personality'
        assert detect_category('기질을 알려줘') == 'personality'
        assert detect_category('타고난 성향은?') == 'personality'

    def test_career_keywords(self):
        assert detect_category('직업 적성을 알려주세요') == 'career'
        assert detect_category('이직해도 될까요?') == 'career'
        assert detect_category('창업 운은?') == 'career'

    def test_love_keywords(self):
        assert detect_category('연애운이 궁금해요') == 'love'
        assert detect_category('결혼 시기는?') == 'love'

    def test_wealth_keywords(self):
        assert detect_category('재물운을 봐주세요') == 'wealth'
        assert detect_category('돈이 언제 들어와요?') == 'wealth'
        assert detect_category('금전 운은?') == 'wealth'

    def test_health_keywords(self):
        assert detect_category('건강은 어떤가요?') == 'health'

    def test_fortune_keywords(self):
        assert detect_category('올해 운세를 알려주세요') == 'fortune'
        assert detect_category('총운을 봐주세요') == 'fortune'

    def test_monthly_keywords(self):
        assert detect_category('월별 운세를 알려주세요') == 'monthly'
        assert detect_category('12개월 운세') == 'monthly'
        assert detect_category('이번달 운세는?') == 'monthly'

    def test_supplement_keywords(self):
        assert detect_category('오행 보충법을 알려주세요') == 'supplement'
        assert detect_category('개운법을 알려주세요') == 'supplement'
        assert detect_category('부족한 색상은 뭐예요?') == 'supplement'

    def test_no_category(self):
        assert detect_category('안녕하세요') is None
        assert detect_category('감사합니다') is None


class TestScoring:
    def test_calculate_scores_returns_all_fields(self, saju_data):
        scores = calculate_scores(saju_data)
        assert 'career' in scores
        assert 'wealth' in scores
        assert 'love' in scores
        assert 'health' in scores
        assert 'study' in scores
        assert 'relations' in scores
        assert 'overall' in scores

    def test_scores_range_1_to_5(self, saju_data):
        scores = calculate_scores(saju_data)
        for key, val in scores.items():
            assert 1 <= val <= 5, f"{key}={val} out of range"

    def test_yongsin_match_bonus(self):
        """용신과 세운 오행 일치 시 보너스"""
        data = {
            'yearly_fortune': {'stem_sipsung': '정관', 'oheng': '금'},
            'yongsin': {'yongsin': '금'},
        }
        scores = calculate_scores(data)
        data_no_match = {
            'yearly_fortune': {'stem_sipsung': '정관', 'oheng': '목'},
            'yongsin': {'yongsin': '금'},
        }
        scores_no_match = calculate_scores(data_no_match)
        # 일치 시 모든 점수가 같거나 높아야 함
        for key in ['career', 'wealth', 'love']:
            assert scores[key] >= scores_no_match[key]


class TestScoreHeader:
    def test_format_score_header_contains_stars(self, saju_data):
        scores = calculate_scores(saju_data)
        header = format_score_header(scores, 2026)
        assert '★' in header
        assert '2026' in header
        assert '직업운' in header
        assert '재물운' in header


class TestLuckyItems:
    def test_lucky_items_for_each_yongsin(self):
        for elem in ['목', '화', '토', '금', '수']:
            data = {'yongsin': {'yongsin': elem}}
            result = format_lucky_items(data)
            assert '행운색' in result
            assert '행운숫자' in result
            assert '길방위' in result

    def test_no_yongsin_returns_empty(self):
        data = {'yongsin': {'yongsin': ''}}
        result = format_lucky_items(data)
        assert result == ''


class TestOhengBar:
    def test_oheng_bar_format(self, saju_data):
        result = format_oheng_bar(saju_data)
        assert '오행 비율' in result
        assert '█' in result or '░' in result


class TestFormatInterpretation:
    def test_fortune_includes_scores(self, saju_data, interpreter):
        saju_obj = type('R', (), {'to_dict': lambda self: saju_data})()
        from datetime import datetime
        from modules.calculator.daeun import get_current_fortune, get_yearly_monthly_fortunes
        now = datetime.now()
        cf = get_current_fortune(saju_data['pillars'], now)
        saju_data['yearly_fortune'] = cf['yearly']
        saju_data['monthly_fortune'] = cf['monthly']
        saju_data['all_monthly_fortunes'] = get_yearly_monthly_fortunes(
            saju_data['pillars'], now.year
        )
        interp = interpreter.interpret_category(saju_obj, 'fortune')
        result = format_interpretation('fortune', interp, saju_data)
        assert '★' in result
        assert '운세 스코어' in result

    def test_fortune_includes_monthly_readings(self, saju_data, interpreter):
        saju_obj = type('R', (), {'to_dict': lambda self: saju_data})()
        from datetime import datetime
        from modules.calculator.daeun import get_current_fortune, get_yearly_monthly_fortunes
        now = datetime.now()
        cf = get_current_fortune(saju_data['pillars'], now)
        saju_data['yearly_fortune'] = cf['yearly']
        saju_data['monthly_fortune'] = cf['monthly']
        saju_data['all_monthly_fortunes'] = get_yearly_monthly_fortunes(
            saju_data['pillars'], now.year
        )
        interp = interpreter.interpret_category(saju_obj, 'fortune')
        result = format_interpretation('fortune', interp, saju_data)
        assert '12개월' in result
        # 최소 6개월 이상 표시되어야 함
        month_count = sum(1 for m in range(1, 13) if f'**{m:2d}월**' in result or f'**{m}월**' in result)
        assert month_count >= 6, f"Only {month_count} months shown"

    def test_fortune_includes_yearly_categories(self, saju_data, interpreter):
        saju_obj = type('R', (), {'to_dict': lambda self: saju_data})()
        from datetime import datetime
        from modules.calculator.daeun import get_current_fortune, get_yearly_monthly_fortunes
        now = datetime.now()
        cf = get_current_fortune(saju_data['pillars'], now)
        saju_data['yearly_fortune'] = cf['yearly']
        saju_data['monthly_fortune'] = cf['monthly']
        saju_data['all_monthly_fortunes'] = get_yearly_monthly_fortunes(
            saju_data['pillars'], now.year
        )
        interp = interpreter.interpret_category(saju_obj, 'fortune')
        result = format_interpretation('fortune', interp, saju_data)
        assert '직업/사업운' in result
        assert '재물운' in result
        assert '연애/결혼운' in result
        assert '건강운' in result

    def test_fortune_includes_yearly_score(self, saju_data, interpreter):
        saju_obj = type('R', (), {'to_dict': lambda self: saju_data})()
        from datetime import datetime
        from modules.calculator.daeun import get_current_fortune, get_yearly_monthly_fortunes
        now = datetime.now()
        cf = get_current_fortune(saju_data['pillars'], now)
        saju_data['yearly_fortune'] = cf['yearly']
        saju_data['monthly_fortune'] = cf['monthly']
        saju_data['all_monthly_fortunes'] = get_yearly_monthly_fortunes(
            saju_data['pillars'], now.year
        )
        interp = interpreter.interpret_category(saju_obj, 'fortune')
        result = format_interpretation('fortune', interp, saju_data)
        assert '운세 스코어' in result
        assert '★' in result

    def test_monthly_category_shows_all_months(self, saju_data, interpreter):
        saju_obj = type('R', (), {'to_dict': lambda self: saju_data})()
        from datetime import datetime
        from modules.calculator.daeun import get_current_fortune, get_yearly_monthly_fortunes
        now = datetime.now()
        cf = get_current_fortune(saju_data['pillars'], now)
        saju_data['yearly_fortune'] = cf['yearly']
        saju_data['monthly_fortune'] = cf['monthly']
        saju_data['all_monthly_fortunes'] = get_yearly_monthly_fortunes(
            saju_data['pillars'], now.year
        )
        interp = interpreter.interpret_category(saju_obj, 'fortune')
        result = format_interpretation('monthly', interp, saju_data)
        assert '12개월' in result or '월별 운세' in result

    def test_personality_includes_lucky_items(self, saju_data, interpreter):
        saju_obj = type('R', (), {'to_dict': lambda self: saju_data})()
        interp = interpreter.interpret_category(saju_obj, 'personality')
        result = format_interpretation('personality', interp, saju_data)
        assert '행운 아이템' in result

    def test_supplement_includes_oheng_bar(self, saju_data, interpreter):
        saju_obj = type('R', (), {'to_dict': lambda self: saju_data})()
        interp = interpreter.interpret_category(saju_obj, 'supplement')
        result = format_interpretation('supplement', interp, saju_data)
        assert '오행 비율' in result
