"""음력/양력 변환 및 음력 사주 계산 테스트"""

import pytest
from modules.calculator.lunar import lunar_to_solar, InvalidLunarDateError
from modules.calculator.core import calculate_saju


class TestLunarToSolar:
    """음력 → 양력 변환 검증"""

    def test_basic_conversion(self):
        """음력 1990-05-15 → 양력 1990-06-07"""
        result = lunar_to_solar(1990, 5, 15)
        assert result == (1990, 6, 7)

    def test_new_year(self):
        """음력 2023-01-01 → 양력 2023-01-22"""
        result = lunar_to_solar(2023, 1, 1)
        assert result == (2023, 1, 22)

    def test_intercalary_month(self):
        """윤달: 음력 2023년 윤2월 1일 → 양력 2023-03-22"""
        result = lunar_to_solar(2023, 2, 1, is_intercalation=True)
        assert result == (2023, 3, 22)

    def test_non_intercalary_same_month(self):
        """비윤달: 음력 2023년 2월 1일 → 양력 2023-02-20"""
        result = lunar_to_solar(2023, 2, 1, is_intercalation=False)
        assert result == (2023, 2, 20)

    def test_year_boundary_cross(self):
        """음력 날짜가 양력으로는 다음 해에 해당하는 경우"""
        result = lunar_to_solar(2022, 12, 29)
        assert result[0] == 2023  # 양력은 2023년

    def test_invalid_date_raises(self):
        """존재하지 않는 음력 날짜 → 에러"""
        with pytest.raises(InvalidLunarDateError):
            lunar_to_solar(2023, 13, 1)

    def test_invalid_intercalation_raises(self):
        """윤달이 아닌 달에 윤달 지정 → 에러"""
        with pytest.raises(InvalidLunarDateError):
            lunar_to_solar(2023, 5, 1, is_intercalation=True)


class TestSajuWithLunar:
    """음력 입력 사주 계산 검증"""

    def test_lunar_saju_differs_from_solar(self):
        """같은 숫자여도 음력/양력이면 다른 사주"""
        solar = calculate_saju(1990, 5, 15, 10)
        lunar = calculate_saju(1990, 5, 15, 10, calendar_type='lunar')
        # 음력 5/15 = 양력 6/7 → 일주가 달라야 함
        assert solar.pillars['day'] != lunar.pillars['day']

    def test_lunar_saju_birth_info(self):
        """음력 사주의 birth_info에 음력 정보 포함"""
        result = calculate_saju(1990, 5, 15, 10, calendar_type='lunar')
        assert result.birth_info['calendar_type'] == '음력'
        assert result.birth_info['lunar_year'] == 1990
        assert result.birth_info['lunar_month'] == 5
        assert result.birth_info['lunar_day'] == 15

    def test_lunar_intercalary_saju(self):
        """윤달 입력 사주 계산"""
        result = calculate_saju(
            2023, 2, 1, 10,
            calendar_type='lunar', is_intercalation=True
        )
        assert result.birth_info['is_intercalation'] is True
        assert result.birth_info['calendar_type'] == '음력(윤달)'

    def test_solar_saju_unchanged(self):
        """양력 사주 계산은 기존과 동일"""
        result = calculate_saju(1990, 5, 15, 10, calendar_type='solar')
        assert result.birth_info['calendar_type'] == '양력'
        assert result.birth_info.get('lunar_year') is None
