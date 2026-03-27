"""오행 보충/사주 보완 해석 패턴 — 부족한 오행을 일상에서 채우는 방법"""

from modules.calculator.constants import OHENG_SANGSAENG

# Element supplement data: colors, directions, foods, activities, season, numbers, career_env, daily_tips
OHENG_SUPPLEMENT = {
    '목': {
        'colors': '초록색, 연두색, 청록색',
        'directions': '동쪽',
        'foods': '신맛 음식 (귤, 레몬, 식초, 매실), 푸른 채소 (시금치, 브로콜리, 샐러드)',
        'activities': '산책, 등산, 나무 심기, 원예, 숲 치유, 스트레칭, 요가',
        'season': '봄 (2~4월)에 에너지가 올라갑니다. 봄에 새로운 일을 시작하면 좋아요.',
        'numbers': '3, 8',
        'career_env': '식물이 있는 환경, 나무 소재 가구, 동쪽 방향 자리에서 일하면 도움이 됩니다.',
        'daily_tips': (
            '아침에 일어나면 창문을 열고 바깥 공기를 마셔보세요. '
            '집이나 사무실에 화분을 놓으면 목의 기운이 보충됩니다. '
            '초록색 소품(필통, 폰케이스, 머플러)을 가까이 두세요. '
            '산림욕은 목 기운 보충에 최고의 활동이에요.'
        ),
    },
    '화': {
        'colors': '빨간색, 자주색, 보라색, 주황색',
        'directions': '남쪽',
        'foods': '쓴맛 음식 (커피, 녹차, 고들빼기, 씀바귀), 빨간 과일 (딸기, 토마토, 석류)',
        'activities': '달리기, 유산소 운동, 캠프파이어, 명상 중 촛불 응시, 사우나',
        'season': '여름 (5~7월)에 활력이 넘칩니다. 여름에 적극적으로 활동하세요.',
        'numbers': '2, 7',
        'career_env': '밝은 조명, 남향 사무실, 따뜻한 색 인테리어 환경이 좋습니다.',
        'daily_tips': (
            '햇볕을 충분히 쐬세요. 하루 20분 이상의 일광욕이 화 기운을 채워줍니다. '
            '빨간색이나 보라색 옷을 즐겨 입어보세요. '
            '촛불 명상은 마음의 열정과 에너지를 되살리는 데 효과적이에요. '
            '따뜻한 차를 자주 마시는 것도 좋아요.'
        ),
    },
    '토': {
        'colors': '노란색, 갈색, 베이지, 황토색',
        'directions': '중앙 (또는 남서/북동)',
        'foods': '단맛 음식 (꿀, 고구마, 단호박, 대추), 곡물 (현미, 보리, 잡곡밥)',
        'activities': '텃밭 가꾸기, 도예, 맨발 걷기 (어싱), 요리, 명상',
        'season': '환절기 (3,6,9,12월)에 에너지가 안정됩니다. 계절이 바뀌는 시기를 잘 활용하세요.',
        'numbers': '5, 10',
        'career_env': '안정적인 환경, 흙과 가까운 공간, 도자기나 돌 소품이 있는 곳이 좋습니다.',
        'daily_tips': (
            '맨발로 땅을 밟는 어싱(접지)을 해보세요. 토의 기운이 직접 보충됩니다. '
            '노란색/갈색 계열의 옷이나 소품을 활용하세요. '
            '직접 요리하는 활동이 토 기운을 높여줍니다. '
            '규칙적인 식사와 충분한 수면이 가장 기본적인 토 기운 보충이에요.'
        ),
    },
    '금': {
        'colors': '흰색, 은색, 금색, 회색',
        'directions': '서쪽',
        'foods': '매운맛 음식 (마늘, 생강, 고추, 겨자), 견과류 (호두, 아몬드, 잣)',
        'activities': '악기 연주, 노래, 금속 공예, 정리정돈, 결단이 필요한 활동',
        'season': '가을 (8~10월)에 결실의 에너지가 옵니다. 가을에 정리하고 수확하세요.',
        'numbers': '4, 9',
        'career_env': '깔끔하고 체계적인 환경, 금속 소재 가구, 서쪽 방향이 좋습니다.',
        'daily_tips': (
            '주변 환경을 정리정돈하세요. 깔끔한 공간에서 금의 기운이 살아납니다. '
            '흰색 계열 옷을 입고, 금속 액세서리(시계, 반지)를 착용해보세요. '
            '악기를 배우거나 음악을 듣는 것이 금 기운 보충에 도움이 됩니다. '
            '매일 10분 명상으로 마음을 단단하게 다듬어보세요.'
        ),
    },
    '수': {
        'colors': '검정색, 남색, 진한 파란색',
        'directions': '북쪽',
        'foods': '짠맛 음식 (해조류, 미역, 김, 다시마), 수분이 많은 음식 (수박, 오이, 배)',
        'activities': '수영, 반신욕, 물가 산책, 독서, 명상, 일기 쓰기',
        'season': '겨울 (11~1월)에 내면의 지혜가 깊어집니다. 겨울에 자기 성찰을 하세요.',
        'numbers': '1, 6',
        'career_env': '물이 있는 환경(분수, 어항), 북쪽 방향, 차분한 분위기가 좋습니다.',
        'daily_tips': (
            '물을 충분히 마시세요. 하루 2리터 이상의 물이 수 기운을 보충합니다. '
            '검정색이나 남색 옷을 즐겨 입어보세요. '
            '수족관이나 작은 분수를 집에 두면 수 기운이 흐릅니다. '
            '반신욕이나 족욕으로 몸의 순환을 도우세요. '
            '일기를 쓰거나 명상하는 시간을 가지면 내면의 지혜가 깊어져요.'
        ),
    },
}

# Yongsin supplement advice per element
YONGSIN_SUPPLEMENT_MAP = {
    '목': (
        '용신이 목(木)입니다. 나무의 기운을 적극 활용하세요. '
        '초록색 옷을 입고, 동쪽을 향해 생활하며, 식물을 가까이 두세요. '
        '봄에 새로운 일을 시작하면 용신의 힘이 더해집니다. '
        '나무 소재 가구, 원목 책상을 쓰면 일의 효율이 올라가요.'
    ),
    '화': (
        '용신이 화(火)입니다. 불의 기운을 적극 활용하세요. '
        '빨간색/보라색 소품을 쓰고, 남쪽을 향해 생활하세요. '
        '햇볕을 자주 쐬고, 사람들과 적극 교류하면 운이 트입니다. '
        '열정을 표현하는 활동 — 발표, 공연, 운동 — 이 용신을 돕습니다.'
    ),
    '토': (
        '용신이 토(土)입니다. 땅의 기운을 적극 활용하세요. '
        '노란색/갈색 계열을 가까이 하고, 규칙적인 생활을 하세요. '
        '텃밭 가꾸기, 요리, 도예 같은 활동이 운을 높여줍니다. '
        '안정적인 환경에서 꾸준히 노력할 때 용신의 힘이 발휘돼요.'
    ),
    '금': (
        '용신이 금(金)입니다. 금속의 기운을 적극 활용하세요. '
        '흰색/은색 소품, 금속 액세서리를 착용하고, 서쪽 방향이 좋습니다. '
        '정리정돈을 습관화하고, 결단력 있게 행동하면 운이 열립니다. '
        '악기 연주나 음악 감상도 금 기운을 높이는 데 효과적이에요.'
    ),
    '수': (
        '용신이 수(水)입니다. 물의 기운을 적극 활용하세요. '
        '검정색/남색 옷을 자주 입고, 북쪽 방향으로 생활하세요. '
        '물을 많이 마시고, 수영이나 물가 산책을 즐기면 운이 좋아집니다. '
        '조용한 독서, 명상, 공부에 시간을 투자하면 용신의 도움을 받아요.'
    ),
}

# Strength-specific advice
STRENGTH_SUPPLEMENT = {
    '신강': (
        '신강한 사주는 에너지가 넘치는 구조예요. '
        '넘치는 기운을 발산하는 것이 핵심입니다. '
        '봉사활동, 재능 나눔, 운동 등으로 에너지를 건강하게 쏟아보세요. '
        '자기 기운을 빼주는 오행(식상·재성)에 해당하는 활동이 균형을 잡아줍니다. '
        '지나치게 혼자 결정하기보다, 주변 사람의 의견을 수용하는 연습이 필요해요.'
    ),
    '신약': (
        '신약한 사주는 에너지를 보충하는 것이 핵심이에요. '
        '나를 도와주는 오행(인성·비겁)을 적극 활용하세요. '
        '충분한 수면, 규칙적인 식사, 적당한 운동으로 체력을 관리하세요. '
        '좋은 사람들과 함께하면 기운이 보충되고, 혼자 무리하지 않는 것이 중요합니다. '
        '자존감을 높이는 활동(취미, 학습, 자격증)이 사주의 약한 부분을 채워줍니다.'
    ),
}

# Seasonal guide based on month branch
SEASON_GUIDE = {
    '봄': '봄은 목(木)의 계절입니다. 새로운 시작, 성장, 학습에 최적의 시기예요.',
    '여름': '여름은 화(火)의 계절입니다. 활발한 활동, 표현, 사교에 에너지를 쏟으세요.',
    '가을': '가을은 금(金)의 계절입니다. 정리, 수확, 결단을 내리기 좋은 시기예요.',
    '겨울': '겨울은 수(水)의 계절입니다. 내면의 성찰, 공부, 계획 수립에 집중하세요.',
}

WOLJI_SEASON = {
    '인': '봄', '묘': '봄', '진': '봄',
    '사': '여름', '오': '여름', '미': '여름',
    '신': '가을', '유': '가을', '술': '가을',
    '해': '겨울', '자': '겨울', '축': '겨울',
}


def interpret_supplement(data: dict) -> dict:
    """Analyze missing elements and provide practical supplement advice.

    Args:
        data: Full saju analysis data dictionary

    Returns:
        Dictionary with supplement category, balance overview,
        element-specific advice, and lifestyle tips
    """
    oheng_balance = data.get('oheng_balance', {})
    yongsin_data = data.get('yongsin', {})
    strength_data = data.get('strength', {})
    pillars = data.get('pillars', {})

    yongsin = yongsin_data.get('yongsin', '')
    strength = strength_data.get('strength', '신강')
    wolji = pillars.get('month', {}).get('branch', '')

    # Build overall balance description
    balance_parts = []
    for element in ['목', '화', '토', '금', '수']:
        info = oheng_balance.get(element, {})
        count = info.get('count', 0)
        status = info.get('status', '보통')
        balance_parts.append(f'{element}({count}개, {status})')

    overall_balance = (
        f'당신의 오행 분포를 살펴볼게요. '
        f'{", ".join(balance_parts)}입니다. '
    )

    # Identify deficient elements
    deficient = []
    excess = []
    for element in ['목', '화', '토', '금', '수']:
        info = oheng_balance.get(element, {})
        status = info.get('status', '보통')
        if status in ('부족', '무'):
            deficient.append(element)
        elif status in ('과다', '다'):
            excess.append(element)

    if deficient:
        overall_balance += (
            f'부족한 오행은 **{", ".join(deficient)}**이에요. '
            f'이 기운을 일상에서 보충하면 삶의 균형이 더 좋아집니다.'
        )
    else:
        overall_balance += (
            '특별히 심하게 부족한 오행은 없어요. '
            '전체적으로 균형이 괜찮은 편입니다. '
            '그래도 용신의 기운을 활용하면 더 좋아져요.'
        )

    if excess:
        overall_balance += (
            f' 반면 **{", ".join(excess)}**은 다소 과한 편이니, '
            f'해당 기운은 적당히 조절해주세요.'
        )

    # Build supplements list for deficient elements
    supplements = []
    for element in deficient:
        sup = OHENG_SUPPLEMENT.get(element, {})
        supplements.append({
            'element': element,
            'status': oheng_balance.get(element, {}).get('status', '부족'),
            'colors': sup.get('colors', ''),
            'directions': sup.get('directions', ''),
            'foods': sup.get('foods', ''),
            'activities': sup.get('activities', ''),
            'season': sup.get('season', ''),
            'numbers': sup.get('numbers', ''),
            'career_env': sup.get('career_env', ''),
            'daily_tips': sup.get('daily_tips', ''),
        })

    # If no deficient elements, supplement with yongsin element
    if not supplements and yongsin:
        sup = OHENG_SUPPLEMENT.get(yongsin, {})
        supplements.append({
            'element': yongsin,
            'status': '용신 보충',
            'colors': sup.get('colors', ''),
            'directions': sup.get('directions', ''),
            'foods': sup.get('foods', ''),
            'activities': sup.get('activities', ''),
            'season': sup.get('season', ''),
            'numbers': sup.get('numbers', ''),
            'career_env': sup.get('career_env', ''),
            'daily_tips': sup.get('daily_tips', ''),
        })

    # Yongsin supplement advice
    yongsin_supplement = YONGSIN_SUPPLEMENT_MAP.get(yongsin, f'용신 {yongsin}의 기운을 일상에서 적극 활용하세요.')

    # Strength advice
    strength_advice = STRENGTH_SUPPLEMENT.get(strength, '')

    # Seasonal guide
    season = WOLJI_SEASON.get(wolji, '봄')
    seasonal_guide = SEASON_GUIDE.get(season, '')

    # Naming advice based on yongsin
    naming_map = {
        '목': '이름에 나무 목(木) 관련 한자가 들어가면 좋습니다 (예: 林, 森, 松, 柏, 榮, 彬).',
        '화': '이름에 불 화(火) 관련 한자가 들어가면 좋습니다 (예: 炫, 燦, 熙, 煥, 照, 暉).',
        '토': '이름에 흙 토(土) 관련 한자가 들어가면 좋습니다 (예: 均, 坤, 培, 城, 垠, 堅).',
        '금': '이름에 쇠 금(金) 관련 한자가 들어가면 좋습니다 (예: 鑫, 鎭, 錫, 銀, 鉉, 鋼).',
        '수': '이름에 물 수(水) 관련 한자가 들어가면 좋습니다 (예: 浩, 泳, 洙, 淳, 潤, 澤).',
    }
    naming_advice = naming_map.get(yongsin, '')

    return {
        'category': '오행보충',
        'overall_balance': overall_balance,
        'supplements': supplements,
        'yongsin_supplement': yongsin_supplement,
        'strength_advice': strength_advice,
        'seasonal_guide': seasonal_guide,
        'naming_advice': naming_advice,
        'deficient': deficient,
        'excess': excess,
    }
