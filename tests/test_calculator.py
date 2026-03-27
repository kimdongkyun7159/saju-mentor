"""만세력 계산 엔진 테스트"""

import pytest
from modules.calculator.pillars import calculate_pillars
from modules.calculator.core import calculate_saju
from modules.calculator.solar_terms import get_ipchun_date
from modules.calculator.elements import count_oheng, get_ilgan_strength
from modules.calculator.sipsung import get_sipsung, get_all_sipsung
from modules.calculator.gongmang import get_gongmang
from modules.calculator.twelve_stars import get_twelve_star


class TestPillars:
    """사주 기둥 계산 검증"""

    def test_year_pillar_after_ipchun(self):
        """입춘 이후 → 해당 연도 년주"""
        result = calculate_pillars(2000, 3, 15, 14)
        assert result['year']['stem'] == '경'
        assert result['year']['branch'] == '진'

    def test_year_pillar_before_ipchun(self):
        """입춘 이전 → 전년도 년주"""
        result = calculate_pillars(2000, 1, 15, 10)
        # 2000년 입춘 전 → 1999년(기묘년) 적용
        assert result['year']['stem'] == '기'
        assert result['year']['branch'] == '묘'

    def test_day_pillar_known_date(self):
        """알려진 일주 검증: 1900-01-01 = 갑술"""
        result = calculate_pillars(1900, 1, 1, 12)
        assert result['day']['stem'] == '갑'
        assert result['day']['branch'] == '술'

    def test_day_pillar_2000(self):
        """2000-01-01 = 무오일"""
        result = calculate_pillars(2000, 1, 1, 12)
        assert result['day']['stem'] == '무'
        assert result['day']['branch'] == '오'

    def test_hour_pillar(self):
        """시주 계산 — 14시 = 미시(未時)"""
        result = calculate_pillars(1995, 3, 15, 14)
        assert result['hour']['branch'] == '미'

    def test_yajasi_mode(self):
        """야자시: 23시 = 당일 자시"""
        result_ya = calculate_pillars(2000, 6, 15, 23, yajasi=True)
        result_jo = calculate_pillars(2000, 6, 15, 23, yajasi=False)
        # 야자시: 당일 일주 유지
        assert result_ya['day'] == calculate_pillars(2000, 6, 15, 12, yajasi=True)['day']
        # 조자시: 다음날 일주
        assert result_jo['hour']['branch'] == '자'

    def test_all_pillars_have_required_keys(self):
        """모든 기둥에 필수 키 존재"""
        result = calculate_pillars(1990, 5, 20, 8)
        for pos in ['year', 'month', 'day', 'hour']:
            assert 'stem' in result[pos]
            assert 'branch' in result[pos]
            assert 'pillar' in result[pos]


class TestSolarTerms:
    """절기 계산 검증"""

    def test_ipchun_2024(self):
        """2024년 입춘 ≈ 2월 4일"""
        dt = get_ipchun_date(2024)
        assert dt.month == 2
        assert 3 <= dt.day <= 5

    def test_ipchun_2000(self):
        """2000년 입춘 ≈ 2월 4일"""
        dt = get_ipchun_date(2000)
        assert dt.month == 2
        assert 3 <= dt.day <= 5


class TestSipsung:
    """십성 계산 검증"""

    def test_bigyeon(self):
        assert get_sipsung('갑', '갑') == '비견'

    def test_geopjae(self):
        assert get_sipsung('갑', '을') == '겁재'

    def test_siksin(self):
        assert get_sipsung('갑', '병') == '식신'

    def test_sanggwan(self):
        assert get_sipsung('갑', '정') == '상관'

    def test_pyeonjae(self):
        assert get_sipsung('갑', '무') == '편재'

    def test_jeongjae(self):
        assert get_sipsung('갑', '기') == '정재'

    def test_pyeongwan(self):
        assert get_sipsung('갑', '경') == '편관'

    def test_jeonggwan(self):
        assert get_sipsung('갑', '신') == '정관'

    def test_pyeonin(self):
        assert get_sipsung('갑', '임') == '편인'

    def test_jeongin(self):
        assert get_sipsung('갑', '계') == '정인'


class TestOheng:
    """오행 분석 검증"""

    def test_count_returns_all_five(self):
        pillars = calculate_pillars(1995, 3, 15, 14)
        counts = count_oheng(pillars)
        assert set(counts.keys()) == {'목', '화', '토', '금', '수'}
        assert sum(counts.values()) == 8  # 4 stems + 4 branches

    def test_ilgan_strength(self):
        pillars = calculate_pillars(1995, 3, 15, 14)
        strength = get_ilgan_strength(pillars)
        assert strength['strength'] in ('신강', '신약')
        assert 'ilgan' in strength


class TestGongmang:
    """공망 계산 검증"""

    def test_gongmang_returns_two(self):
        gm1, gm2 = get_gongmang('갑', '자')
        from modules.calculator.constants import JIJI
        assert gm1 in JIJI
        assert gm2 in JIJI
        assert gm1 != gm2

    def test_gongmang_gapja(self):
        """갑자순 → 술해가 공망"""
        gm1, gm2 = get_gongmang('갑', '자')
        assert set([gm1, gm2]) == {'술', '해'}


class TestTwelveStars:
    """십이운성 검증"""

    def test_gap_hae_jangsaeng(self):
        """갑목 해(亥)에서 장생"""
        assert get_twelve_star('갑', '해') == '장생'

    def test_gap_myo_jewang(self):
        """갑목 묘(卯)에서 제왕"""
        assert get_twelve_star('갑', '묘') == '제왕'


class TestIntegration:
    """통합 계산 검증"""

    def test_full_saju_calculation(self):
        result = calculate_saju(1995, 3, 15, 14, gender='male')
        assert result.pillars is not None
        assert result.oheng is not None
        assert result.sipsung is not None
        assert result.sinsal is not None
        assert result.yongsin is not None
        assert result.geokguk is not None
        assert result.daeun is not None
        assert result.summary is not None

    def test_saju_result_to_dict(self):
        result = calculate_saju(1990, 8, 15, 6, gender='female')
        d = result.to_dict()
        assert isinstance(d, dict)
        assert 'pillars' in d
        assert 'birth_info' in d
        assert d['birth_info']['gender'] == '여'

    def test_different_yajasi_modes(self):
        """야자시/조자시 결과가 다름을 검증"""
        ya = calculate_saju(1995, 6, 15, 23, yajasi=True)
        jo = calculate_saju(1995, 6, 15, 23, yajasi=False)
        assert ya.pillars['day'] != jo.pillars['day'] or ya.pillars['hour'] != jo.pillars['hour']
