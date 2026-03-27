"""십이운성(十二運星) 계산 — 일간 기준 지지별 운성 판별"""

from .constants import (
    CHEONGAN, JIJI, CHEONGAN_UMYANG,
    TWELVE_STARS, TWELVE_STARS_BASE,
)

TWELVE_STARS_DESC = {
    '장생': '시작, 탄생, 새로운 출발의 기운',
    '목욕': '불안정, 감성, 유혹, 변화',
    '관대': '성장, 활력, 자신감 상승',
    '건록': '전성기, 독립, 안정적 수입',
    '제왕': '절정, 최고 권위, 정점',
    '쇠': '하강, 원숙, 지혜 축적',
    '병': '쇠약, 내면 성찰, 건강 주의',
    '사': '끝남, 정리, 포기와 새 시작',
    '묘': '잠복, 숨겨진 재능, 보이지 않는 힘',
    '절': '단절, 새 시작 직전, 전환점',
    '태': '잉태, 새로운 가능성, 준비',
    '양': '양육, 보호 받음, 성장 전 단계',
}


def get_twelve_star(ilgan: str, jiji: str) -> str:
    """일간 기준으로 지지의 십이운성 반환"""
    is_yang = CHEONGAN_UMYANG[ilgan]
    base = TWELVE_STARS_BASE[ilgan]
    jiji_idx = JIJI.index(jiji)
    if is_yang:
        # 양간: 순행
        star_idx = (jiji_idx - base) % 12
    else:
        # 음간: 역행
        star_idx = (base - jiji_idx) % 12
    return TWELVE_STARS[star_idx]


def get_all_twelve_stars(pillars: dict) -> dict:
    """4기둥 전체의 십이운성 배치"""
    ilgan = pillars['day']['stem']
    result = {}
    for pos in ['year', 'month', 'day', 'hour']:
        branch = pillars[pos]['branch']
        star = get_twelve_star(ilgan, branch)
        result[pos] = {
            'star': star,
            'description': TWELVE_STARS_DESC[star],
        }
    return result
