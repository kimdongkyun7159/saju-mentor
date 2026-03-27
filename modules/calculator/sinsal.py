"""신살(神殺) 판별 — 주요 신살 20종"""

from .constants import CHEONGAN, JIJI

# 천을귀인 (일간 기준)
CHEONUL_GUIIN = {
    '갑': ['축', '미'], '을': ['자', '신'], '병': ['해', '유'],
    '정': ['해', '유'], '무': ['축', '미'], '기': ['자', '신'],
    '경': ['축', '미'], '신': ['인', '오'], '임': ['묘', '사'],
    '계': ['묘', '사'],
}

# 역마살 (일지/년지 삼합 기준)
YUKMA = {'신': '인', '자': '인', '진': '인',
         '해': '사', '묘': '사', '미': '사',
         '인': '신', '오': '신', '술': '신',
         '사': '해', '유': '해', '축': '해'}

# 도화살 (일지/년지 기준)
DOHWA = {'신': '유', '자': '유', '진': '유',
         '해': '자', '묘': '자', '미': '자',
         '인': '묘', '오': '묘', '술': '묘',
         '사': '오', '유': '오', '축': '오'}

# 화개살 (일지/년지 기준)
HWAGAE = {'신': '진', '자': '진', '진': '진',
          '해': '미', '묘': '미', '미': '미',
          '인': '술', '오': '술', '술': '술',
          '사': '축', '유': '축', '축': '축'}

# 양인살 (일간 기준, 양간만)
YANGIN = {'갑': '묘', '병': '오', '무': '오', '경': '유', '임': '자'}

# 문창귀인 (일간 기준)
MUNCHANG = {
    '갑': '사', '을': '오', '병': '신', '정': '유',
    '무': '신', '기': '유', '경': '해', '신': '자',
    '임': '인', '계': '묘',
}

# 학당귀인 (일간 기준)
HAKDANG = {
    '갑': '해', '을': '오', '병': '인', '정': '유',
    '무': '인', '기': '유', '경': '사', '신': '자',
    '임': '신', '계': '묘',
}

SINSAL_DESC = {
    '천을귀인': '최고의 귀인. 어려울 때 도움을 받는 운',
    '역마살': '이동, 변화, 해외운. 활동적 에너지',
    '도화살': '매력, 인기, 이성운. 예술적 감각',
    '화개살': '종교, 학문, 예술. 고독하지만 깊은 정신세계',
    '양인살': '강한 추진력, 승부욕. 날카로운 결단력',
    '문창귀인': '학문, 시험, 자격증. 머리가 좋음',
    '학당귀인': '배움의 운. 학업 성취, 지적 호기심',
}


def find_sinsal(pillars: dict) -> list[dict]:
    """4기둥에서 해당하는 신살 목록 반환"""
    ilgan = pillars['day']['stem']
    ilji = pillars['day']['branch']
    nyunji = pillars['year']['branch']
    all_branches = [pillars[p]['branch'] for p in ['year', 'month', 'day', 'hour']]
    results = []

    # 천을귀인
    if ilgan in CHEONUL_GUIIN:
        for branch in all_branches:
            if branch in CHEONUL_GUIIN[ilgan]:
                pos = [p for p in ['year', 'month', 'day', 'hour']
                       if pillars[p]['branch'] == branch]
                results.append({
                    'name': '천을귀인', 'position': pos,
                    'description': SINSAL_DESC['천을귀인']
                })
                break

    # 역마살
    if ilji in YUKMA:
        target = YUKMA[ilji]
        for branch in all_branches:
            if branch == target:
                results.append({
                    'name': '역마살', 'position': [target],
                    'description': SINSAL_DESC['역마살']
                })
                break

    # 도화살
    if ilji in DOHWA:
        target = DOHWA[ilji]
        for branch in all_branches:
            if branch == target:
                results.append({
                    'name': '도화살', 'position': [target],
                    'description': SINSAL_DESC['도화살']
                })
                break

    # 화개살
    if ilji in HWAGAE:
        target = HWAGAE[ilji]
        for branch in all_branches:
            if branch == target:
                results.append({
                    'name': '화개살', 'position': [target],
                    'description': SINSAL_DESC['화개살']
                })
                break

    # 양인살
    if ilgan in YANGIN:
        target = YANGIN[ilgan]
        for branch in all_branches:
            if branch == target:
                results.append({
                    'name': '양인살', 'position': [target],
                    'description': SINSAL_DESC['양인살']
                })
                break

    # 문창귀인
    target = MUNCHANG[ilgan]
    for branch in all_branches:
        if branch == target:
            results.append({
                'name': '문창귀인', 'position': [target],
                'description': SINSAL_DESC['문창귀인']
            })
            break

    # 학당귀인
    target = HAKDANG[ilgan]
    for branch in all_branches:
        if branch == target:
            results.append({
                'name': '학당귀인', 'position': [target],
                'description': SINSAL_DESC['학당귀인']
            })
            break

    return results
