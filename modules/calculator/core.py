"""만세력 통합 엔진 — 모든 계산 모듈 통합"""

from dataclasses import dataclass, field
from .pillars import calculate_pillars
from .elements import count_oheng, analyze_oheng_balance, get_ilgan_strength
from .sipsung import get_all_sipsung, get_sipsung_summary
from .twelve_stars import get_all_twelve_stars
from .sinsal import find_sinsal
from .relations import analyze_relations
from .gongmang import check_gongmang
from .yongsin import determine_yongsin
from .geokguk import determine_geokguk
from .daeun import calculate_daeun, get_current_daeun, get_yearly_fortune
from .constants import CHEONGAN_OHENG, CHEONGAN_UMYANG


@dataclass
class SajuResult:
    """사주 분석 결과 전체"""
    pillars: dict
    oheng: dict
    oheng_balance: dict
    strength: dict
    sipsung: dict
    sipsung_summary: dict
    twelve_stars: dict
    sinsal: list
    relations: list
    gongmang: dict
    yongsin: dict
    geokguk: dict
    daeun: dict
    current_daeun: dict | None
    yearly_fortune: dict
    birth_info: dict
    monthly_fortune: dict = field(default_factory=dict)
    summary: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'pillars': self.pillars,
            'oheng': self.oheng,
            'oheng_balance': self.oheng_balance,
            'strength': self.strength,
            'sipsung': self.sipsung,
            'sipsung_summary': self.sipsung_summary,
            'twelve_stars': self.twelve_stars,
            'sinsal': self.sinsal,
            'relations': self.relations,
            'gongmang': self.gongmang,
            'yongsin': self.yongsin,
            'geokguk': self.geokguk,
            'daeun': self.daeun,
            'current_daeun': self.current_daeun,
            'yearly_fortune': self.yearly_fortune,
            'monthly_fortune': self.monthly_fortune,
            'birth_info': self.birth_info,
            'summary': self.summary,
        }


def calculate_saju(
    year: int, month: int, day: int,
    hour: int, minute: int = 0,
    gender: str = 'male',
    yajasi: bool = True,
    current_year: int = 2026,
    calendar_type: str = 'solar',
    is_intercalation: bool = False,
) -> SajuResult:
    """사주 전체 계산

    Args:
        year, month, day, hour, minute: 생년월일시
        gender: 'male' or 'female'
        yajasi: True=야자시(한국 전통), False=조자시(중국식)
        current_year: 현재 연도 (대운/세운 계산용)
        calendar_type: 'solar'(양력) or 'lunar'(음력)
        is_intercalation: 음력 윤달 여부
    """
    # 음력 → 양력 변환
    lunar_info = None
    if calendar_type == 'lunar':
        from .lunar import lunar_to_solar
        lunar_info = {
            'lunar_year': year, 'lunar_month': month,
            'lunar_day': day, 'is_intercalation': is_intercalation,
        }
        year, month, day = lunar_to_solar(year, month, day, is_intercalation)

    pillars = calculate_pillars(year, month, day, hour, minute, yajasi)
    oheng = count_oheng(pillars)
    oheng_balance = analyze_oheng_balance(pillars)
    strength = get_ilgan_strength(pillars)
    sipsung = get_all_sipsung(pillars)
    sipsung_summary = get_sipsung_summary(pillars)
    twelve_stars = get_all_twelve_stars(pillars)
    sinsal = find_sinsal(pillars)
    relations = analyze_relations(pillars)
    gongmang = check_gongmang(pillars)
    yongsin = determine_yongsin(pillars)
    geokguk = determine_geokguk(pillars)
    daeun = calculate_daeun(pillars, year, month, day, hour, gender)
    current_daeun = get_current_daeun(daeun, current_year, year)
    
    from datetime import datetime
    try:
        now = datetime(current_year, datetime.now().month, datetime.now().day, datetime.now().hour)
    except:
        now = datetime(current_year, 7, 1)

    from .daeun import get_current_fortune
    cf = get_current_fortune(pillars, now)
    yearly_fortune = cf['yearly']
    monthly_fortune = cf['monthly']

    ilgan = pillars['day']['stem']
    if calendar_type == 'lunar' and is_intercalation:
        cal_label = '음력(윤달)'
    elif calendar_type == 'lunar':
        cal_label = '음력'
    else:
        cal_label = '양력'

    birth_info = {
        'year': year, 'month': month, 'day': day,
        'hour': hour, 'minute': minute,
        'gender': '남' if gender == 'male' else '여',
        'yajasi': yajasi,
        'calendar_type': cal_label,
        'ilgan': ilgan,
        'ilgan_oheng': CHEONGAN_OHENG[ilgan],
        'ilgan_umyang': '양' if CHEONGAN_UMYANG[ilgan] else '음',
    }
    if lunar_info:
        birth_info.update(lunar_info)

    summary = {
        'saju': (f"{pillars['year']['pillar']}년 {pillars['month']['pillar']}월 "
                 f"{pillars['day']['pillar']}일 {pillars['hour']['pillar']}시"),
        'ilgan_desc': f"{birth_info['ilgan_umyang']}{birth_info['ilgan_oheng']}({ilgan})",
        'strength': strength['strength'],
        'geokguk': geokguk['geokguk'],
        'yongsin': yongsin['yongsin'],
    }

    return SajuResult(
        pillars=pillars, oheng=oheng, oheng_balance=oheng_balance,
        strength=strength, sipsung=sipsung, sipsung_summary=sipsung_summary,
        twelve_stars=twelve_stars, sinsal=sinsal, relations=relations,
        gongmang=gongmang, yongsin=yongsin, geokguk=geokguk,
        daeun=daeun, current_daeun=current_daeun,
        yearly_fortune=yearly_fortune, monthly_fortune=monthly_fortune,
        birth_info=birth_info, summary=summary,
    )
