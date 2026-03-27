"""오행(五行) 분석 — 천간/지지/지장간 오행 분포 계산"""

from .constants import (
    CHEONGAN_OHENG, JIJI_OHENG, JIJANGGAN,
    OHENG, CHEONGAN_UMYANG, JIJI_UMYANG,
    OHENG_SANGSAENG, OHENG_SANGGEUK,
)


def count_oheng(pillars: dict) -> dict[str, int]:
    """4기둥의 천간/지지에서 오행 개수 집계"""
    counts = {e: 0 for e in OHENG}
    for pos in ['year', 'month', 'day', 'hour']:
        stem = pillars[pos]['stem']
        branch = pillars[pos]['branch']
        counts[CHEONGAN_OHENG[stem]] += 1
        counts[JIJI_OHENG[branch]] += 1
    return counts


def count_oheng_with_jijanggan(pillars: dict) -> dict[str, float]:
    """지장간 포함 오행 분포 (가중치 적용)"""
    counts = {e: 0.0 for e in OHENG}
    # 천간 (가중치 1.0)
    for pos in ['year', 'month', 'day', 'hour']:
        stem = pillars[pos]['stem']
        counts[CHEONGAN_OHENG[stem]] += 1.0
    # 지지 본기 (가중치 1.0) + 지장간 (여기 0.3, 중기 0.5, 정기 1.0)
    weights = [0.3, 0.5, 1.0]  # 여기, 중기, 정기
    for pos in ['year', 'month', 'day', 'hour']:
        branch = pillars[pos]['branch']
        jijang = JIJANGGAN[branch]
        for i, gan in enumerate(jijang):
            if gan:
                counts[CHEONGAN_OHENG[gan]] += weights[i]
    return counts


def analyze_oheng_balance(pillars: dict) -> dict:
    """오행 균형 분석 — 과다/부족/균형 판단"""
    counts = count_oheng(pillars)
    total = sum(counts.values())
    avg = total / 5
    result = {}
    for element, count in counts.items():
        if count == 0:
            status = '무'
        elif count >= avg * 1.8:
            status = '과다'
        elif count >= avg * 1.3:
            status = '다'
        elif count <= avg * 0.5:
            status = '부족'
        else:
            status = '보통'
        result[element] = {'count': count, 'status': status}
    return result


def get_ilgan_strength(pillars: dict) -> dict:
    """일간 강약 판단 (억부법 기초)"""
    ilgan = pillars['day']['stem']
    ilgan_oheng = CHEONGAN_OHENG[ilgan]
    # 생하는 오행 (인성)
    saeng_oheng = [k for k, v in OHENG_SANGSAENG.items() if v == ilgan_oheng]
    saeng_element = saeng_oheng[0] if saeng_oheng else None
    # 득령: 월지가 일간을 돕는지
    wolji = pillars['month']['branch']
    wolji_oheng = JIJI_OHENG[wolji]
    deukryeong = wolji_oheng == ilgan_oheng or wolji_oheng == saeng_element
    # 전체 점수 계산
    score = 0
    helpful = {ilgan_oheng, saeng_element} - {None}
    harmful_elements = set()
    # 일간이 극하는 오행 (재성)
    harmful_elements.add(OHENG_SANGGEUK[ilgan_oheng])
    # 일간을 극하는 오행 (관성)
    for k, v in OHENG_SANGGEUK.items():
        if v == ilgan_oheng:
            harmful_elements.add(k)
    # 일간이 생하는 오행 (식상)
    harmful_elements.add(OHENG_SANGSAENG[ilgan_oheng])
    counts = count_oheng_with_jijanggan(pillars)
    for element in helpful:
        score += counts.get(element, 0)
    for element in harmful_elements:
        score -= counts.get(element, 0) * 0.7
    # 월지 가중치
    if deukryeong:
        score += 2
    else:
        score -= 1
    is_strong = score > 0
    return {
        'ilgan': ilgan,
        'ilgan_oheng': ilgan_oheng,
        'deukryeong': deukryeong,
        'score': round(score, 1),
        'is_strong': is_strong,
        'strength': '신강' if is_strong else '신약',
    }
