import pytest
from datetime import datetime
from modules.calculator.core import calculate_saju
from modules.calculator.daeun import get_current_fortune

def test_monthly_fortune_calculation():
    # 기준 사주: 1990년 5월 15일 12:00 (양력, 남자)
    # 경오(년), 신사(월), 기유(일), 경오(시)
    saju = calculate_saju(
        year=1990, month=5, day=15, hour=12, minute=0, gender='male', calendar_type='solar'
    )
    
    # 2026년 3월 27일 기준 (입춘 지남, 경칩 지남)
    # 2026 (병오년), 3월 (신묘월)
    target_date = datetime(2026, 3, 27)
    
    # get_current_fortune 함수 테스트
    cf = get_current_fortune(saju.pillars, target_date)
    
    yearly = cf['yearly']
    monthly = cf['monthly']
    
    # 세운(Yearly) 검증: 2026년은 병오(丙午)년
    assert yearly['stem'] == '병'
    assert yearly['branch'] == '오'
    assert yearly['pillar'] == '병오'
    
    # 월운(Monthly) 검증: 2026년 3월(경칩 이후)은 신묘(辛卯)월
    assert monthly['stem'] == '신'
    assert monthly['branch'] == '묘'
    assert monthly['pillar'] == '신묘'

def test_saju_result_contains_monthly_fortune():
    saju = calculate_saju(
        year=1990, month=5, day=15, hour=12, minute=0, gender='male', calendar_type='solar'
    )
    
    # SajuResult 객체와 그 딕셔너리에 monthly_fortune 키가 존재하는지
    assert hasattr(saju, 'monthly_fortune')
    assert 'monthly_fortune' in saju.to_dict()
    
    monthly = saju.to_dict()['monthly_fortune']
    assert isinstance(monthly, dict)
    assert 'stem' in monthly
    assert 'branch' in monthly
