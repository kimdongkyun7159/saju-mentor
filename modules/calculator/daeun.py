"""대운(大運)/세운(歲運) 계산"""

from datetime import datetime, timedelta
from .constants import CHEONGAN, JIJI, CHEONGAN_UMYANG, CHEONGAN_OHENG
from .solar_terms import find_solar_term_date, MONTH_BOUNDARIES
from .sipsung import get_sipsung


def calculate_daeun(
    pillars: dict, year: int, month: int, day: int,
    hour: int, gender: str
) -> dict:
    """대운 계산

    Args:
        gender: 'male' or 'female'
    """
    birth_dt = datetime(year, month, day, hour)
    year_stem = pillars['year']['stem']
    month_stem = pillars['month']['stem']
    month_branch = pillars['month']['branch']

    year_stem_yang = CHEONGAN_UMYANG[year_stem]
    is_male = gender == 'male'

    # 순행/역행 결정
    # 양남음녀 = 순행, 음남양녀 = 역행
    forward = (year_stem_yang and is_male) or (not year_stem_yang and not is_male)

    # 대운수 계산 (생일~다음/이전 절기까지 일수 ÷ 3)
    birth_year = birth_dt.year
    all_boundaries = []
    for y in [birth_year - 1, birth_year, birth_year + 1]:
        for name, longitude, _ in MONTH_BOUNDARIES:
            dt = find_solar_term_date(y, longitude)
            all_boundaries.append(dt)
    all_boundaries.sort()

    if forward:
        # 순행: 다음 절기까지
        next_jeolgi = None
        for bd in all_boundaries:
            if bd > birth_dt:
                next_jeolgi = bd
                break
        days_to_jeolgi = (next_jeolgi - birth_dt).total_seconds() / 86400 if next_jeolgi else 30
    else:
        # 역행: 이전 절기까지
        prev_jeolgi = None
        for bd in reversed(all_boundaries):
            if bd < birth_dt:
                prev_jeolgi = bd
                break
        days_to_jeolgi = (birth_dt - prev_jeolgi).total_seconds() / 86400 if prev_jeolgi else 30

    # 3일 = 1년, 1일 = 4개월
    daeun_start_age = round(days_to_jeolgi / 3)
    if daeun_start_age < 1:
        daeun_start_age = 1

    # 대운 간지 나열 (10개)
    month_stem_idx = CHEONGAN.index(month_stem)
    month_branch_idx = JIJI.index(month_branch)
    ilgan = pillars['day']['stem']

    daeun_list = []
    for i in range(1, 11):
        if forward:
            s_idx = (month_stem_idx + i) % 10
            b_idx = (month_branch_idx + i) % 12
        else:
            s_idx = (month_stem_idx - i) % 10
            b_idx = (month_branch_idx - i) % 12
        stem = CHEONGAN[s_idx]
        branch = JIJI[b_idx]
        start_age = daeun_start_age + (i - 1) * 10
        end_age = start_age + 9
        start_year = year + start_age

        daeun_list.append({
            'stem': stem,
            'branch': branch,
            'pillar': stem + branch,
            'start_age': start_age,
            'end_age': end_age,
            'start_year': start_year,
            'end_year': start_year + 9,
            'stem_sipsung': get_sipsung(ilgan, stem),
            'oheng': CHEONGAN_OHENG[stem],
        })

    return {
        'direction': '순행' if forward else '역행',
        'start_age': daeun_start_age,
        'daeun_list': daeun_list,
    }


def get_current_daeun(daeun_data: dict, current_year: int, birth_year: int) -> dict | None:
    """현재 대운 반환"""
    age = current_year - birth_year + 1  # 한국 나이
    for d in daeun_data['daeun_list']:
        if d['start_age'] <= age <= d['end_age']:
            return d
    return None


def get_yearly_fortune(pillars: dict, target_year: int) -> dict:
    """세운(歲運) 계산 (단순 연도 기준 - 하위 호환성 유지)"""
    ilgan = pillars['day']['stem']
    stem_idx = (target_year - 4) % 10
    branch_idx = (target_year - 4) % 12
    stem = CHEONGAN[stem_idx]
    branch = JIJI[branch_idx]
    return {
        'year': target_year,
        'stem': stem,
        'branch': branch,
        'pillar': stem + branch,
        'stem_sipsung': get_sipsung(ilgan, stem),
        'oheng': CHEONGAN_OHENG[stem],
    }


def get_current_fortune(user_pillars: dict, target_date: datetime) -> dict:
    """타겟 날짜의 정밀 세운(Yearly) 및 월운(Monthly) 계산 (입춘/절기 기준)"""
    from .pillars import calculate_pillars
    target_pillars = calculate_pillars(
        target_date.year, target_date.month, target_date.day, target_date.hour, target_date.minute, True
    )

    ilgan = user_pillars['day']['stem']

    # 세운 (Yearly)
    year_stem = target_pillars['year']['stem']
    year_branch = target_pillars['year']['branch']
    yearly = {
        'year': target_date.year,
        'stem': year_stem,
        'branch': year_branch,
        'pillar': target_pillars['year']['pillar'],
        'stem_sipsung': get_sipsung(ilgan, year_stem),
        'oheng': CHEONGAN_OHENG[year_stem],
    }

    # 월운 (Monthly) — 현재 달
    month_stem = target_pillars['month']['stem']
    month_branch = target_pillars['month']['branch']
    monthly = {
        'month': target_date.month,
        'stem': month_stem,
        'branch': month_branch,
        'pillar': target_pillars['month']['pillar'],
        'stem_sipsung': get_sipsung(ilgan, month_stem),
        'oheng': CHEONGAN_OHENG[month_stem],
    }

    return {'yearly': yearly, 'monthly': monthly}


def get_yearly_monthly_fortunes(user_pillars: dict, year: int) -> list[dict]:
    """해당 연도 12개월 월운 전체 계산 (절기 기준 중간일 사용)"""
    from .pillars import calculate_pillars
    from .solar_terms import get_month_boundaries

    ilgan = user_pillars['day']['stem']

    # 절기 경계 수집 (전년도 소한 ~ 내년 입춘 커버)
    boundaries_prev = get_month_boundaries(year - 1)
    boundaries_curr = get_month_boundaries(year)
    boundaries_next = get_month_boundaries(year + 1)
    all_bounds = boundaries_prev + boundaries_curr + boundaries_next
    all_bounds.sort(key=lambda x: x[1])

    # 절기명 → 월 번호 매핑 (인월=1월 아닌, 양력 기준 근사 월)
    JEOLGI_TO_MONTH = {
        '소한': 1, '입춘': 2, '경칩': 3, '청명': 4,
        '입하': 5, '망종': 6, '소서': 7, '입추': 8,
        '백로': 9, '한로': 10, '입동': 11, '대설': 12,
    }

    results = []
    seen_months = set()

    for i in range(len(all_bounds) - 1):
        name, start_dt, _ = all_bounds[i]
        _, end_dt, _ = all_bounds[i + 1]

        approx_month = JEOLGI_TO_MONTH.get(name)
        if approx_month is None:
            continue

        # 해당 연도 범위 필터
        mid_dt = start_dt + (end_dt - start_dt) / 2
        if mid_dt.year != year:
            continue
        if approx_month in seen_months:
            continue
        seen_months.add(approx_month)

        # 중간일 기준 월주 계산
        mid_pillars = calculate_pillars(
            mid_dt.year, mid_dt.month, mid_dt.day, 12, 0, True
        )
        m_stem = mid_pillars['month']['stem']
        m_branch = mid_pillars['month']['branch']

        results.append({
            'month': approx_month,
            'jeolgi': name,
            'start': start_dt.strftime('%m/%d'),
            'stem': m_stem,
            'branch': m_branch,
            'pillar': mid_pillars['month']['pillar'],
            'stem_sipsung': get_sipsung(ilgan, m_stem),
            'oheng': CHEONGAN_OHENG[m_stem],
        })

    results.sort(key=lambda x: x['month'])
    return results
