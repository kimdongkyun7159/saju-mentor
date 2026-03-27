"""건강 해석 패턴 — 상담형 풀이"""

OHENG_HEALTH = {
    '목': {
        'organs': '간, 담, 눈, 근육, 신경계',
        'weak_desc': '간 기능이 약해지기 쉽고, 눈의 피로나 시력 저하가 올 수 있어요. 근육 경련, 손발 저림도 주의하세요.',
        'excess_desc': '목 기운이 과하면 화를 잘 내게 되고, 두통이나 어지러움이 올 수 있어요. 간에 열이 차서 눈이 충혈되기도 합니다.',
        'advice': '녹색 채소를 많이 드시고, 숲 산책이나 가벼운 등산이 좋아요. 눈의 피로를 자주 풀어주시고, 충분한 수면이 중요합니다.',
    },
    '화': {
        'organs': '심장, 소장, 혀, 혈액, 혈관',
        'weak_desc': '심장이 약해지기 쉽고, 혈압 관련 문제나 불면증이 올 수 있어요. 혈액순환에 신경 써야 합니다.',
        'excess_desc': '화 기운이 과하면 불안, 초조, 불면증이 심해질 수 있어요. 심장에 부담이 가고, 입안이 헐거나 혀에 문제가 생기기도 해요.',
        'advice': '유산소 운동과 명상으로 마음을 안정시키세요. 붉은 과일(석류, 토마토)이 좋고, 과도한 카페인은 피하세요.',
    },
    '토': {
        'organs': '비장, 위장, 입, 피부, 면역계',
        'weak_desc': '소화 기능이 약해지기 쉽고, 위염이나 장 관련 문제가 올 수 있어요. 피부 트러블도 주의하세요.',
        'excess_desc': '토 기운이 과하면 비만, 당뇨, 부종이 올 수 있어요. 단 것을 많이 먹게 되고, 몸이 무겁게 느껴질 수 있습니다.',
        'advice': '규칙적인 식사가 가장 중요해요! 호박, 고구마, 잡곡 같은 자연식을 드시고, 과식은 피하세요.',
    },
    '금': {
        'organs': '폐, 대장, 코, 피부, 호흡기',
        'weak_desc': '호흡기가 약해지기 쉽고, 감기에 잘 걸리거나 알레르기가 있을 수 있어요. 피부 건조나 아토피도 주의하세요.',
        'excess_desc': '금 기운이 과하면 피부 문제, 변비, 호흡기 과민이 올 수 있어요. 건조한 환경에 특히 약합니다.',
        'advice': '배, 무, 도라지 같은 흰 음식이 폐를 도와줘요. 호흡 운동(복식호흡, 요가)이 좋고, 실내 습도를 유지하세요.',
    },
    '수': {
        'organs': '신장, 방광, 귀, 뼈, 관절, 생식기',
        'weak_desc': '신장 기능이 약해지기 쉽고, 요통이나 관절 문제가 올 수 있어요. 귀 관련(이명, 난청)도 주의하세요.',
        'excess_desc': '수 기운이 과하면 냉증, 부종, 방광 관련 문제가 올 수 있어요. 몸이 차가워지기 쉽습니다.',
        'advice': '검은콩, 흑임자, 검은깨 같은 검은 음식이 신장을 도와줘요. 충분한 수분 섭취와 하체 운동이 중요합니다.',
    },
}


def interpret_health(data: dict) -> dict:
    oheng_balance = data['oheng_balance']
    ilgan_oheng = data['birth_info']['ilgan_oheng']
    strength = data['strength']
    ilgan = data['birth_info']['ilgan']

    weak_elements = []
    excess_elements = []
    for element, info in oheng_balance.items():
        if info['status'] in ('무', '부족'):
            weak_elements.append(element)
        elif info['status'] in ('과다', '다'):
            excess_elements.append(element)

    health_warnings = []
    for elem in weak_elements:
        health = OHENG_HEALTH.get(elem, {})
        health_warnings.append({
            'element': elem,
            'type': '부족',
            'organs': health.get('organs', ''),
            'risk': health.get('weak_desc', ''),
            'advice': health.get('advice', ''),
        })

    for elem in excess_elements:
        health = OHENG_HEALTH.get(elem, {})
        health_warnings.append({
            'element': elem,
            'type': '과다',
            'organs': health.get('organs', ''),
            'risk': health.get('excess_desc', ''),
            'advice': health.get('advice', ''),
        })

    base_health = OHENG_HEALTH.get(ilgan_oheng, {})

    if strength['is_strong']:
        strength_health = (
            '신강한 사주라 **기본 체력이 좋은 편**이에요. 웬만한 병은 금방 회복합니다. '
            '다만 체력을 과신해서 무리하는 경향이 있어요. '
            '"나는 괜찮아"라고 버티다가 한꺼번에 무너질 수 있으니, '
            '정기적인 건강검진과 충분한 휴식을 꼭 챙기세요.\n\n'
            '특히 스트레스를 잘 풀지 않으면 갑자기 큰 병으로 올 수 있어요. '
            '운동과 취미활동으로 에너지를 건강하게 소모하는 것이 좋습니다.'
        )
    else:
        strength_health = (
            '신약한 사주라 **체력 관리가 특히 중요**해요. '
            '면역력이 상대적으로 약한 편이라, 환절기마다 컨디션이 떨어질 수 있습니다. '
            '규칙적인 생활 습관과 충분한 수면이 건강의 기본이에요.\n\n'
            '무리한 다이어트나 과도한 야근은 피하세요. '
            '당신의 몸은 쉬어야 충전되는 타입입니다. '
            '가벼운 운동(산책, 요가, 수영)을 꾸준히 하면 체력이 크게 좋아져요.'
        )

    # 전체 건강 요약
    overall = ''
    if not health_warnings:
        overall = (
            '오행이 비교적 균형 잡혀있어 **전반적으로 건강운이 좋은 편**이에요. '
            '기본적인 생활 관리만 잘 하면 큰 문제 없이 건강하게 지낼 수 있습니다.'
        )
    elif len(weak_elements) > len(excess_elements):
        overall = (
            f'사주에서 **{", ".join(weak_elements)}** 기운이 부족한 편이에요. '
            f'해당 장기에 관련된 건강 관리를 특히 신경 쓰면 좋겠습니다.'
        )
    else:
        overall = (
            f'사주에서 **{", ".join(excess_elements)}** 기운이 과한 편이에요. '
            f'해당 장기에 과부하가 올 수 있으니, 적절한 관리가 필요합니다.'
        )

    return {
        'category': '건강',
        'base_organs': base_health.get('organs', ''),
        'base_advice': base_health.get('advice', ''),
        'health_warnings': health_warnings,
        'strength_health': strength_health,
        'overall': overall,
        'weak_elements': weak_elements,
        'excess_elements': excess_elements,
    }
