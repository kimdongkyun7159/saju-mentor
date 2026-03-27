"""십성(十星/十神) 계산 — 일간 기준 각 천간/지지의 십성 판별"""

from .constants import (
    CHEONGAN, CHEONGAN_OHENG, CHEONGAN_UMYANG,
    JIJANGGAN, OHENG_SANGSAENG, OHENG_SANGGEUK,
)

SIPSUNG_MAP = {
    '비견': '나와 같은 기운. 독립심, 자존심, 경쟁심',
    '겁재': '나를 빼앗는 기운. 추진력, 욕심, 승부욕',
    '식신': '내가 낳는 기운. 재능, 표현력, 식복',
    '상관': '내가 쏟아내는 기운. 창의성, 반항, 날카로움',
    '편재': '내가 취하는 재물. 투자, 사교성, 유동자산',
    '정재': '내가 모으는 재물. 저축, 안정, 고정자산',
    '편관': '나를 제어하는 힘. 권위, 압박, 카리스마',
    '정관': '나를 이끄는 법. 명예, 책임감, 조직력',
    '편인': '나를 키우는 지식. 창의적 학문, 직감, 고독',
    '정인': '나를 돌보는 사랑. 학문, 자격증, 어머니',
}


def get_sipsung(ilgan: str, target_gan: str) -> str:
    """일간 기준으로 대상 천간의 십성 판별"""
    if ilgan == target_gan:
        return '비견'
    il_oheng = CHEONGAN_OHENG[ilgan]
    tg_oheng = CHEONGAN_OHENG[target_gan]
    il_yang = CHEONGAN_UMYANG[ilgan]
    tg_yang = CHEONGAN_UMYANG[target_gan]
    same_umyang = il_yang == tg_yang
    if il_oheng == tg_oheng:
        return '비견' if same_umyang else '겁재'
    if OHENG_SANGSAENG[il_oheng] == tg_oheng:
        return '식신' if same_umyang else '상관'
    if OHENG_SANGGEUK[il_oheng] == tg_oheng:
        return '편재' if same_umyang else '정재'
    for k, v in OHENG_SANGGEUK.items():
        if v == il_oheng and k == tg_oheng:
            return '편관' if same_umyang else '정관'
    for k, v in OHENG_SANGSAENG.items():
        if v == il_oheng and k == tg_oheng:
            return '편인' if same_umyang else '정인'
    return '비견'


def get_all_sipsung(pillars: dict) -> dict:
    """4기둥 전체의 십성 배치 반환"""
    ilgan = pillars['day']['stem']
    result = {}
    for pos in ['year', 'month', 'day', 'hour']:
        stem = pillars[pos]['stem']
        branch = pillars[pos]['branch']
        stem_sipsung = get_sipsung(ilgan, stem) if pos != 'day' else '일간'
        # 지지 → 정기의 십성
        jijang = JIJANGGAN[branch]
        jeongi = jijang[2]  # 정기
        branch_sipsung = get_sipsung(ilgan, jeongi) if jeongi else ''
        result[pos] = {
            'stem_sipsung': stem_sipsung,
            'branch_sipsung': branch_sipsung,
        }
    return result


def get_sipsung_summary(pillars: dict) -> dict[str, int]:
    """십성 분포 요약 (몇 개씩 있는지)"""
    counts = {}
    ilgan = pillars['day']['stem']
    for pos in ['year', 'month', 'day', 'hour']:
        stem = pillars[pos]['stem']
        if pos != 'day':
            ss = get_sipsung(ilgan, stem)
            counts[ss] = counts.get(ss, 0) + 1
        branch = pillars[pos]['branch']
        for gan in JIJANGGAN[branch]:
            if gan:
                ss = get_sipsung(ilgan, gan)
                counts[ss] = counts.get(ss, 0) + 1
    return counts
