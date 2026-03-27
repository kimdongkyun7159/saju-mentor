"""지지 관계(합충형파해) 분석"""

# 지지 육합 (六合)
YUKHAP = {
    frozenset({'자', '축'}): '토',
    frozenset({'인', '해'}): '목',
    frozenset({'묘', '술'}): '화',
    frozenset({'진', '유'}): '금',
    frozenset({'사', '신'}): '수',
    frozenset({'오', '미'}): '토',
}

# 지지 삼합 (三合)
SAMHAP = [
    ({'해', '묘', '미'}, '목'),
    ({'인', '오', '술'}, '화'),
    ({'사', '유', '축'}, '금'),
    ({'신', '자', '진'}, '수'),
]

# 지지 방합 (方合)
BANGHAP = [
    ({'인', '묘', '진'}, '목'),
    ({'사', '오', '미'}, '화'),
    ({'신', '유', '술'}, '금'),
    ({'해', '자', '축'}, '수'),
]

# 지지 충 (冲)
CHUNG = {
    frozenset({'자', '오'}), frozenset({'축', '미'}),
    frozenset({'인', '신'}), frozenset({'묘', '유'}),
    frozenset({'진', '술'}), frozenset({'사', '해'}),
}

# 지지 형 (刑)
HYUNG = [
    ({'인', '사', '신'}, '무은지형'),  # 삼형
    ({'축', '술', '미'}, '무례지형'),
    ({'자', '묘'}, '무례지형'),
    ({'진', '진'}, '자형'), ({'오', '오'}, '자형'),
    ({'유', '유'}, '자형'), ({'해', '해'}, '자형'),
]

# 지지 파 (破)
PA = {
    frozenset({'자', '유'}), frozenset({'축', '진'}),
    frozenset({'인', '해'}), frozenset({'묘', '오'}),
    frozenset({'사', '신'}), frozenset({'미', '술'}),
}

# 지지 해 (害)
HAE = {
    frozenset({'자', '미'}), frozenset({'축', '오'}),
    frozenset({'인', '사'}), frozenset({'묘', '진'}),
    frozenset({'신', '해'}), frozenset({'유', '술'}),
}

# 천간합 (天干合)
CHEONGAN_HAP = {
    frozenset({'갑', '기'}): '토',
    frozenset({'을', '경'}): '금',
    frozenset({'병', '신'}): '수',
    frozenset({'정', '임'}): '목',
    frozenset({'무', '계'}): '화',
}

# 천간충 (天干冲)
CHEONGAN_CHUNG = {
    frozenset({'갑', '경'}), frozenset({'을', '신'}),
    frozenset({'병', '임'}), frozenset({'정', '계'}),
}

RELATION_DESC = {
    '합': '조화, 결합, 융합의 기운. 관계가 좋음',
    '충': '충돌, 변화, 이동의 기운. 갈등 또는 변혁',
    '형': '형벌, 시련, 갈등. 고난 속 성장',
    '파': '파괴, 깨짐. 계획 변경, 이별 가능',
    '해': '해침, 방해. 은근한 갈등, 건강 주의',
}


def analyze_relations(pillars: dict) -> list[dict]:
    """4기둥 간의 합충형파해 분석"""
    branches = [(p, pillars[p]['branch']) for p in ['year', 'month', 'day', 'hour']]
    stems = [(p, pillars[p]['stem']) for p in ['year', 'month', 'day', 'hour']]
    results = []
    all_branch_set = {b for _, b in branches}

    # 지지 육합
    for i in range(len(branches)):
        for j in range(i + 1, len(branches)):
            pair = frozenset({branches[i][1], branches[j][1]})
            if pair in YUKHAP:
                results.append({
                    'type': '육합', 'category': '합',
                    'positions': [branches[i][0], branches[j][0]],
                    'elements': [branches[i][1], branches[j][1]],
                    'result_element': YUKHAP[pair],
                    'description': RELATION_DESC['합'],
                })

    # 지지 삼합
    for trio, element in SAMHAP:
        if trio.issubset(all_branch_set):
            results.append({
                'type': '삼합', 'category': '합',
                'elements': list(trio),
                'result_element': element,
                'description': f'{element}국 삼합. 강한 결합력',
            })

    # 지지 충
    for i in range(len(branches)):
        for j in range(i + 1, len(branches)):
            pair = frozenset({branches[i][1], branches[j][1]})
            if pair in CHUNG:
                results.append({
                    'type': '충', 'category': '충',
                    'positions': [branches[i][0], branches[j][0]],
                    'elements': [branches[i][1], branches[j][1]],
                    'description': RELATION_DESC['충'],
                })

    # 천간합
    for i in range(len(stems)):
        for j in range(i + 1, len(stems)):
            pair = frozenset({stems[i][1], stems[j][1]})
            if pair in CHEONGAN_HAP:
                results.append({
                    'type': '천간합', 'category': '합',
                    'positions': [stems[i][0], stems[j][0]],
                    'elements': [stems[i][1], stems[j][1]],
                    'result_element': CHEONGAN_HAP[pair],
                    'description': '천간의 합. 조화로운 관계',
                })

    # 천간충
    for i in range(len(stems)):
        for j in range(i + 1, len(stems)):
            pair = frozenset({stems[i][1], stems[j][1]})
            if pair in CHEONGAN_CHUNG:
                results.append({
                    'type': '천간충', 'category': '충',
                    'positions': [stems[i][0], stems[j][0]],
                    'elements': [stems[i][1], stems[j][1]],
                    'description': '천간의 충돌. 내적 갈등',
                })

    return results
