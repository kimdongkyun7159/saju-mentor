"""절기(Solar Terms) 계산 — Jean Meeus 알고리즘 기반 태양 황경 계산"""

import math
from datetime import datetime, timedelta

# 12절기 → 월 경계 (절기명, 태양황경, 월인덱스 0=인월)
MONTH_BOUNDARIES = [
    ('입춘', 315, 0), ('경칩', 345, 1), ('청명', 15, 2), ('입하', 45, 3),
    ('망종', 75, 4), ('소서', 105, 5), ('입추', 135, 6), ('백로', 165, 7),
    ('한로', 195, 8), ('입동', 225, 9), ('대설', 255, 10), ('소한', 285, 11),
]


def _datetime_to_jd(dt: datetime) -> float:
    y, m = dt.year, dt.month
    d = dt.day + dt.hour / 24.0 + dt.minute / 1440.0 + dt.second / 86400.0
    if m <= 2:
        y -= 1
        m += 12
    a = int(y / 100)
    b = 2 - a + int(a / 4)
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + b - 1524.5


def _jd_to_datetime(jd: float) -> datetime:
    jd += 0.5
    z = int(jd)
    f = jd - z
    if z < 2299161:
        a = z
    else:
        alpha = int((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - int(alpha / 4)
    b = a + 1524
    c = int((b - 122.1) / 365.25)
    d = int(365.25 * c)
    e = int((b - d) / 30.6001)
    day_frac = b - d - int(30.6001 * e) + f
    day = int(day_frac)
    frac = day_frac - day
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715
    hours = frac * 24
    hour = int(hours)
    minutes = (hours - hour) * 60
    minute = int(minutes)
    second = int((minutes - minute) * 60)
    return datetime(year, month, day, hour, minute, second)


def solar_longitude(jd: float) -> float:
    """주어진 율리우스일의 태양 황경(도)"""
    T = (jd - 2451545.0) / 36525.0
    L0 = (280.46646 + 36000.76983 * T + 0.0003032 * T * T) % 360
    M = math.radians((357.52911 + 35999.05029 * T - 0.0001537 * T * T) % 360)
    C = ((1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(M)
         + (0.019993 - 0.000101 * T) * math.sin(2 * M)
         + 0.000289 * math.sin(3 * M))
    omega = math.radians(125.04 - 1934.136 * T)
    return (L0 + C - 0.00569 - 0.00478 * math.sin(omega)) % 360


def find_solar_term_date(year: int, target_longitude: float) -> datetime:
    """특정 연도에 태양이 주어진 황경에 도달하는 날짜 반환 (KST +9h 보정)"""
    # 춘분(0°) 기준 상대 각도 → 일수 환산 (180° 이상은 이전으로)
    adjusted = target_longitude if target_longitude <= 180 else target_longitude - 360
    days_from_equinox = adjusted / 360 * 365.25
    approx_jd = _datetime_to_jd(datetime(year, 3, 20)) + days_from_equinox
    jd_lo = approx_jd - 20
    jd_hi = approx_jd + 20
    for _ in range(60):
        jd_mid = (jd_lo + jd_hi) / 2
        lon = solar_longitude(jd_mid)
        diff = (lon - target_longitude + 540) % 360 - 180
        if abs(diff) < 0.0001:
            break
        if diff > 0:
            jd_hi = jd_mid
        else:
            jd_lo = jd_mid
    # UTC → KST (+9시간) 보정
    utc_dt = _jd_to_datetime(jd_mid)
    return utc_dt + timedelta(hours=9)


def get_ipchun_date(year: int) -> datetime:
    """해당 연도 입춘(立春) 날짜"""
    return find_solar_term_date(year, 315)


def get_month_boundaries(year: int) -> list[tuple[str, datetime, int]]:
    """해당 연도의 12절기 날짜 목록 [(절기명, datetime, 월인덱스), ...]"""
    boundaries = []
    for name, longitude, month_idx in MONTH_BOUNDARIES:
        dt = find_solar_term_date(year, longitude)
        boundaries.append((name, dt, month_idx))
    boundaries.sort(key=lambda x: x[1])
    return boundaries


def get_saju_month(dt: datetime) -> tuple[int, str]:
    """주어진 날짜가 속한 사주 월(인덱스 0=인월~11=축월)과 절기명 반환"""
    year = dt.year
    all_boundaries = []
    for y in [year - 1, year, year + 1]:
        for name, longitude, month_idx in MONTH_BOUNDARIES:
            d = find_solar_term_date(y, longitude)
            all_boundaries.append((name, d, month_idx))
    all_boundaries.sort(key=lambda x: x[1])
    result_idx = 11
    result_name = '소한'
    for i in range(len(all_boundaries)):
        if dt >= all_boundaries[i][1]:
            result_idx = all_boundaries[i][2]
            result_name = all_boundaries[i][0]
        else:
            break
    return result_idx, result_name
