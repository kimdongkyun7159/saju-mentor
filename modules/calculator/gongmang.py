"""공망(空亡) 계산 — 일주 기준 공망 지지 판별"""

from .constants import CHEONGAN, JIJI, GANJI_60


def get_gongmang(day_stem: str, day_branch: str) -> tuple[str, str]:
    """일주의 공망 지지 2개 반환

    60갑자에서 천간 10개가 지지 12개와 짝을 이루면 2개가 남음 → 공망
    """
    stem_idx = CHEONGAN.index(day_stem)
    branch_idx = JIJI.index(day_branch)
    # 해당 순(旬)의 시작 간지 찾기
    # 갑(0)으로 시작하는 순 → 갑자, 갑술, 갑신, 갑오, 갑진, 갑인
    ganji_idx = 0
    for i in range(60):
        s, b = GANJI_60[i]
        if s == day_stem and b == day_branch:
            ganji_idx = i
            break
    # 순(旬)의 시작점 (갑으로 시작)
    sun_start = ganji_idx - stem_idx
    if sun_start < 0:
        sun_start += 60
    # 이 순에서 사용된 지지 인덱스
    used_branch_indices = set()
    for offset in range(10):
        idx = (sun_start + offset) % 60
        _, branch = GANJI_60[idx]
        used_branch_indices.add(JIJI.index(branch))
    # 사용되지 않은 2개가 공망
    all_indices = set(range(12))
    empty = sorted(all_indices - used_branch_indices)
    return JIJI[empty[0]], JIJI[empty[1]]


def check_gongmang(pillars: dict) -> dict:
    """4기둥에서 공망 해당 여부 확인"""
    d_stem = pillars['day']['stem']
    d_branch = pillars['day']['branch']
    gm1, gm2 = get_gongmang(d_stem, d_branch)
    gongmang_set = {gm1, gm2}
    result = {
        'gongmang': [gm1, gm2],
        'affected': {},
    }
    for pos in ['year', 'month', 'hour']:
        branch = pillars[pos]['branch']
        if branch in gongmang_set:
            result['affected'][pos] = branch
    return result
