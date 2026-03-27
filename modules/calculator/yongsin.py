"""용신(用神) 판별 — 억부법 + 조후 보정"""

from .constants import (
    CHEONGAN_OHENG, JIJI_OHENG, OHENG,
    OHENG_SANGSAENG, OHENG_SANGGEUK,
)
from .elements import get_ilgan_strength

# 조후 용신 테이블 (월지 기준)
JOHU_TABLE = {
    # 겨울생 (해자축월) → 화(火) 필요
    '해': '화', '자': '화', '축': '화',
    # 여름생 (사오미월) → 수(水) 필요
    '사': '수', '오': '수', '미': '수',
    # 봄/가을은 조후 영향 약함
    '인': None, '묘': None, '진': None,
    '신': None, '유': None, '술': None,
}

YONGSIN_DESC = {
    '목': '성장, 인자함, 배움을 추구하세요',
    '화': '열정, 표현, 밝은 에너지를 발휘하세요',
    '토': '안정, 신뢰, 중심을 잡으세요',
    '금': '결단, 정의, 원칙을 세우세요',
    '수': '지혜, 유연함, 흐름을 따르세요',
}


def determine_yongsin(pillars: dict) -> dict:
    """억부법 + 조후 보정으로 용신 판별"""
    strength = get_ilgan_strength(pillars)
    ilgan_oheng = strength['ilgan_oheng']
    is_strong = strength['is_strong']
    wolji = pillars['month']['branch']

    # 억부법: 신강이면 설기/극, 신약이면 생/부조
    if is_strong:
        # 신강 → 설기(식상), 재성, 관성이 용신
        primary = OHENG_SANGSAENG[ilgan_oheng]  # 식상 (내가 생하는)
        secondary = OHENG_SANGGEUK[ilgan_oheng]  # 재성 (내가 극하는)
        reason = '신강하여 기운을 빼주는 것이 좋습니다'
    else:
        # 신약 → 인성(나를 생하는), 비겁(같은 오행)이 용신
        for k, v in OHENG_SANGSAENG.items():
            if v == ilgan_oheng:
                primary = k  # 인성
                break
        secondary = ilgan_oheng  # 비겁
        reason = '신약하여 기운을 보충해주는 것이 좋습니다'

    # 조후 보정
    johu = JOHU_TABLE.get(wolji)
    johu_note = ''
    if johu:
        johu_note = f'계절 보정: {wolji}월생으로 {johu}(火/水)의 조후가 필요합니다'

    # 기신 (용신의 반대)
    if is_strong:
        for k, v in OHENG_SANGSAENG.items():
            if v == ilgan_oheng:
                gisin_primary = k
                break
        gisin_secondary = ilgan_oheng
    else:
        gisin_primary = OHENG_SANGSAENG[ilgan_oheng]
        gisin_secondary = OHENG_SANGGEUK[ilgan_oheng]

    return {
        'yongsin': primary,
        'yongsin_secondary': secondary,
        'gisin': gisin_primary,
        'gisin_secondary': gisin_secondary,
        'johu': johu,
        'reason': reason,
        'johu_note': johu_note,
        'strength': strength,
        'advice': YONGSIN_DESC.get(primary, ''),
    }
