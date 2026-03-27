"""사주팔자 기둥(柱) 계산 — 년주, 월주, 일주, 시주"""

from datetime import datetime, timedelta
from .constants import CHEONGAN, JIJI
from .solar_terms import get_ipchun_date, get_saju_month

# 일주 기준점: 1900-01-01 = 갑술일 (60갑자 인덱스 10)
_BASE_DATE = datetime(1900, 1, 1)
_BASE_DAY_INDEX = 10


def year_pillar(dt: datetime) -> tuple[str, str]:
    """년주 계산 — 입춘 기준으로 연도 결정"""
    year = dt.year
    ipchun = get_ipchun_date(year)
    if dt < ipchun:
        year -= 1
    stem_idx = (year - 4) % 10
    branch_idx = (year - 4) % 12
    return CHEONGAN[stem_idx], JIJI[branch_idx]


def month_pillar(dt: datetime) -> tuple[str, str]:
    """월주 계산 — 절기 기준 월 + 년간 오호법"""
    year = dt.year
    ipchun = get_ipchun_date(year)
    saju_year = year if dt >= ipchun else year - 1
    year_stem_idx = (saju_year - 4) % 10
    month_idx, _ = get_saju_month(dt)
    # 월지: 인(2)부터 시작, month_idx 0=인월
    branch_idx = (month_idx + 2) % 12
    # 년간 오호법으로 월간 결정
    month_stem_base = ((year_stem_idx % 5) * 2 + 2) % 10
    stem_idx = (month_stem_base + month_idx) % 10
    return CHEONGAN[stem_idx], JIJI[branch_idx]


def day_pillar(dt: datetime, yajasi: bool = True) -> tuple[str, str]:
    """일주 계산 — 자정 기준, 야자시 옵션

    Args:
        yajasi: True=야자시(23시 이후 당일), False=조자시(23시 이후 다음날)
    """
    target = dt
    if not yajasi and dt.hour >= 23:
        target = dt + timedelta(days=1)
    days_diff = (target.replace(hour=0, minute=0, second=0, microsecond=0) - _BASE_DATE).days
    day_idx = (days_diff + _BASE_DAY_INDEX) % 60
    stem_idx = day_idx % 10
    branch_idx = day_idx % 12
    return CHEONGAN[stem_idx], JIJI[branch_idx]


def hour_pillar(dt: datetime, day_stem: str, yajasi: bool = True) -> tuple[str, str]:
    """시주 계산 — 일간기시법 + 야자시/조자시 처리

    Args:
        day_stem: 일간 (야자시/조자시에 따라 다를 수 있음)
        yajasi: True=야자시(23시 당일 일간 사용), False=조자시(23시 다음날 일간 사용)
    """
    hour = dt.hour
    # 시지 결정 (2시간 단위)
    hour_branch_idx = ((hour + 1) % 24) // 2
    # 일간기시법: 일간으로 자시의 천간 결정
    day_stem_idx = CHEONGAN.index(day_stem)
    hour_stem_base = ((day_stem_idx % 5) * 2) % 10
    stem_idx = (hour_stem_base + hour_branch_idx) % 10
    return CHEONGAN[stem_idx], JIJI[hour_branch_idx]


def calculate_pillars(
    year: int, month: int, day: int,
    hour: int, minute: int = 0,
    yajasi: bool = True
) -> dict:
    """사주팔자 4기둥 계산

    Args:
        yajasi: True=야자시(기본, 한국 전통), False=조자시(중국식)

    Returns:
        dict with year/month/day/hour pillars
    """
    dt = datetime(year, month, day, hour, minute)
    y_stem, y_branch = year_pillar(dt)
    m_stem, m_branch = month_pillar(dt)
    d_stem, d_branch = day_pillar(dt, yajasi=yajasi)

    # 시주: 조자시면 23시 이후 다음날 일간 사용
    if not yajasi and hour >= 23:
        next_day = dt + timedelta(days=1)
        next_d_stem, _ = day_pillar(next_day, yajasi=False)
        h_stem, h_branch = hour_pillar(dt, next_d_stem, yajasi=False)
    else:
        h_stem, h_branch = hour_pillar(dt, d_stem, yajasi=yajasi)

    return {
        'year': {'stem': y_stem, 'branch': y_branch, 'pillar': y_stem + y_branch},
        'month': {'stem': m_stem, 'branch': m_branch, 'pillar': m_stem + m_branch},
        'day': {'stem': d_stem, 'branch': d_branch, 'pillar': d_stem + d_branch},
        'hour': {'stem': h_stem, 'branch': h_branch, 'pillar': h_stem + h_branch},
        'yajasi': yajasi,
    }
