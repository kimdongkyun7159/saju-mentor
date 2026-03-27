"""채팅 서비스 — Gemini API 기반 사주 상담"""

import json
from modules.calculator.core import calculate_saju
from modules.interpreter.base import SajuInterpreter
from modules.memory.database import Database, DB_PATH
from modules.memory.user_profile import UserProfileManager
from modules.memory.chat_history import ChatHistoryManager
from modules.interpreter.gemini_client import generate as gemini_generate

interpreter = SajuInterpreter()
db = Database()
profile_mgr = UserProfileManager(DB_PATH)
history_mgr = ChatHistoryManager(DB_PATH)

# 카테고리 감지 키워드 (칩 버튼 매칭용)
CATEGORY_KEYWORDS = {
    'personality': ['성격', '기질', '성향', '나는', '내가', '특징', '장점', '단점', '타고난'],
    'career': ['직업', '적성', '취업', '이직', '사업', '진로', '직장', '커리어', '일', '승진', '창업'],
    'love': ['연애', '결혼', '이혼', '궁합', '썸', '사랑', '배우자', '남친', '여친', '애인', '짝'],
    'wealth': ['재물', '돈', '투자', '재테크', '부동산', '주식', '월급', '재산', '금전', '횡재'],
    'health': ['건강', '아프', '병', '운동', '다이어트', '스트레스', '잠', '수면', '체력', '장기'],
    'fortune': ['운세', '올해', '대운', '세운', '운', '미래', '내년', '언제', '시기', '타이밍', '총운', '종합'],
    'monthly': ['월별', '월운', '이번달', '다음달', '몇월', '12개월', '매월'],
    'supplement': ['보완', '보충', '부족', '오행', '색상', '용신 활용', '맞는 색', '개운', '행운'],
}


def detect_category(message: str) -> str | None:
    """우선순위 기반 카테고리 감지"""
    priority_order = [
        'monthly', 'supplement', 'personality', 'career', 'love',
        'wealth', 'health', 'fortune',
    ]
    for category in priority_order:
        keywords = CATEGORY_KEYWORDS.get(category, [])
        for kw in keywords:
            if kw in message:
                return category
    return None


# ── 스코어링 (사이드바/참고용으로 유지) ──

SIPSUNG_SCORES = {
    '정관': {'career': 5, 'wealth': 4, 'love': 4, 'health': 4, 'study': 5, 'relations': 4},
    '정재': {'career': 4, 'wealth': 5, 'love': 5, 'health': 4, 'study': 4, 'relations': 4},
    '식신': {'career': 4, 'wealth': 4, 'love': 4, 'health': 5, 'study': 4, 'relations': 5},
    '정인': {'career': 4, 'wealth': 3, 'love': 4, 'health': 4, 'study': 5, 'relations': 4},
    '편재': {'career': 4, 'wealth': 4, 'love': 3, 'health': 3, 'study': 3, 'relations': 5},
    '편관': {'career': 3, 'wealth': 3, 'love': 3, 'health': 2, 'study': 4, 'relations': 3},
    '상관': {'career': 4, 'wealth': 3, 'love': 3, 'health': 3, 'study': 4, 'relations': 2},
    '편인': {'career': 3, 'wealth': 3, 'love': 2, 'health': 3, 'study': 5, 'relations': 2},
    '비견': {'career': 3, 'wealth': 2, 'love': 3, 'health': 4, 'study': 3, 'relations': 3},
    '겁재': {'career': 3, 'wealth': 2, 'love': 2, 'health': 3, 'study': 3, 'relations': 2},
}


def calculate_scores(saju_data: dict) -> dict:
    """올해 세운 십성 기반 분야별 스코어 계산"""
    yearly = saju_data.get('yearly_fortune', {})
    yongsin = saju_data.get('yongsin', {}).get('yongsin', '')
    yearly_oheng = yearly.get('oheng', '')
    yearly_sipsung = yearly.get('stem_sipsung', '')

    base = SIPSUNG_SCORES.get(yearly_sipsung, {
        'career': 3, 'wealth': 3, 'love': 3, 'health': 3, 'study': 3, 'relations': 3
    }).copy()

    if yongsin == yearly_oheng:
        base = {k: min(5, v + 1) for k, v in base.items()}

    base['overall'] = round(sum(base.values()) / len(base))
    return base


def format_score_header(scores: dict, year: int = 2026) -> str:
    """별점 스코어 헤더 생성"""
    stars = lambda n: '★' * n + '☆' * (5 - n)
    lines = [
        f"📊 **{year}년 운세 스코어**\n",
        f"  총운: {stars(scores.get('overall', 3))}",
        f"  💼 직업운: {stars(scores.get('career', 3))}",
        f"  💰 재물운: {stars(scores.get('wealth', 3))}",
        f"  💕 연애운: {stars(scores.get('love', 3))}",
        f"  🏥 건강운: {stars(scores.get('health', 3))}",
        f"  📚 학업운: {stars(scores.get('study', 3))}",
        f"  🤝 대인관계: {stars(scores.get('relations', 3))}",
    ]
    return '\n'.join(lines)


def format_lucky_items(saju_data: dict) -> str:
    """행운 아이템 (용신 기반)"""
    yongsin = saju_data.get('yongsin', {}).get('yongsin', '')
    LUCKY = {
        '목': {'color': '초록색, 연두색', 'number': '3, 8', 'direction': '동쪽', 'season': '봄', 'item': '나무 소품, 화분'},
        '화': {'color': '빨간색, 보라색', 'number': '2, 7', 'direction': '남쪽', 'season': '여름', 'item': '촛불, 빨간 소품'},
        '토': {'color': '노란색, 갈색', 'number': '5, 10', 'direction': '중앙', 'season': '환절기', 'item': '도자기, 흙 소품'},
        '금': {'color': '흰색, 금색', 'number': '4, 9', 'direction': '서쪽', 'season': '가을', 'item': '금속 액세서리'},
        '수': {'color': '검정색, 남색', 'number': '1, 6', 'direction': '북쪽', 'season': '겨울', 'item': '수정, 물 관련 소품'},
    }
    lucky = LUCKY.get(yongsin, {})
    if not lucky:
        return ''
    return (
        f"\n\n🍀 **나만의 행운 아이템**\n"
        f"  🎨 행운색: {lucky['color']}\n"
        f"  🔢 행운숫자: {lucky['number']}\n"
        f"  🧭 길방위: {lucky['direction']}\n"
        f"  🌸 행운 계절: {lucky['season']}\n"
        f"  ✨ 추천 아이템: {lucky['item']}"
    )


def format_oheng_bar(saju_data: dict) -> str:
    """오행 비율 시각 바"""
    balance = saju_data.get('oheng_balance', {})
    if not balance:
        return ''
    lines = ['\n📈 **오행 비율**']
    EMOJI = {'목': '🌿', '화': '🔥', '토': '🏔️', '금': '⚙️', '수': '💧'}
    for elem in ['목', '화', '토', '금', '수']:
        info = balance.get(elem, {})
        count = info.get('count', 0)
        bar = '█' * count + '░' * (8 - count)
        lines.append(f"  {EMOJI.get(elem, '')} {elem}: {bar} ({count}개, {info.get('status', '')})")
    return '\n'.join(lines)


# ── 규칙 기반 해석 포맷 (format_interpretation은 테스트용으로 유지) ──

FOLLOW_UP = {
    'personality': '\n\n---\n💬 **다음 추천**: 직업 적성 · 연애 스타일 · 올해 운세',
    'career': '\n\n---\n💬 **다음 추천**: 재물운 · 올해 운세 · 오행 보충',
    'love': '\n\n---\n💬 **다음 추천**: 성격 분석 · 올해 운세 · 건강운',
    'wealth': '\n\n---\n💬 **다음 추천**: 직업 적성 · 건강운 · 올해 운세',
    'health': '\n\n---\n💬 **다음 추천**: 올해 운세 · 재물운 · 오행 보충',
    'fortune': '\n\n---\n💬 **다음 추천**: 월별 운세 · 연애운 · 재물운 · 오행 보충',
    'monthly': '\n\n---\n💬 **다음 추천**: 올해 총운 · 성격 분석 · 직업 적성',
    'supplement': '\n\n---\n💬 **다음 추천**: 성격 분석 · 올해 운세 · 건강운',
}


def format_interpretation(category: str, result: dict, saju_data: dict = None) -> str:
    """해석 결과 포맷 (테스트 호환용 유지)"""
    lines = []

    if category == 'personality':
        lines.append(f"🌟 **{result.get('title', '')}**\n")
        lines.append(result.get('nature', ''))
        lines.append(f"\n{result.get('deep_traits', '')}")
        lines.append(f"\n💪 **강점**: {result.get('strengths', '')}")
        lines.append(f"⚠️ **약점**: {result.get('weaknesses', '')}")
        lines.append(f"\n{result.get('strength_note', '')}")
        if result.get('sipsung_note'):
            lines.append(result['sipsung_note'])
        lines.append(f"\n🙏 **멘토의 조언**\n{result.get('advice', '')}")
        for extra in result.get('extras', []):
            lines.append(f'\n{extra}')

    elif category == 'fortune':
        if saju_data:
            scores = calculate_scores(saju_data)
            yf = result.get('yearly_fortune', {})
            lines.append(format_score_header(scores, yf.get('year', 2026)))
            lines.append('')
        lines.append("🔮 **운세 심층 분석**\n")
        cd = result.get('current_daeun')
        if cd:
            lines.append(f"📅 **현재 대운: {cd['pillar']}** ({cd['start_age']}~{cd['end_age']}세)\n")
            lines.append(result.get('daeun_reading', ''))
        yf = result.get('yearly_fortune', {})
        if yf:
            lines.append(f"\n🗓️ **{yf.get('year', '')}년 세운: {yf.get('pillar', '')}**\n")
            lines.append(result.get('yearly_reading', ''))
        ycat = result.get('yearly_category', {})
        if ycat:
            lines.append(f"\n📋 **{yf.get('year', '')}년 분야별 상세 운세**\n")
            if ycat.get('career'):
                lines.append(f"💼 **직업/사업운**\n{ycat['career']}\n")
            if ycat.get('wealth'):
                lines.append(f"💰 **재물운**\n{ycat['wealth']}\n")
            if ycat.get('love'):
                lines.append(f"💕 **연애/결혼운**\n{ycat['love']}\n")
            if ycat.get('health'):
                lines.append(f"🏥 **건강운**\n{ycat['health']}\n")
        monthly_readings = result.get('monthly_readings', [])
        if monthly_readings:
            from datetime import datetime as _dt
            current_month = _dt.now().month
            lines.append(f"\n📆 **{yf.get('year', '')}년 12개월 월운 총정리**\n")
            for m in monthly_readings:
                is_now = '👉 ' if m['month'] == current_month else '   '
                lines.append(
                    f"{is_now}**{m['month']:2d}월** ({m['start']}~) {m['pillar']} "
                    f"[{m['sipsung']}] — {m['reading']}"
                )

    elif category == 'monthly':
        yf = saju_data.get('yearly_fortune', {}) if saju_data else {}
        monthly_readings = result.get('monthly_readings', [])
        if saju_data:
            scores = calculate_scores(saju_data)
            lines.append(format_score_header(scores, yf.get('year', 2026)))
            lines.append('')
        lines.append(f"📆 **{yf.get('year', 2026)}년 12개월 월별 운세 상세**\n")
        if monthly_readings:
            from datetime import datetime as _dt
            current_month = _dt.now().month
            for m in monthly_readings:
                is_now = '👉 ' if m['month'] == current_month else ''
                lines.append(
                    f"\n{is_now}**{m['month']}월** ({m['start']}~) | {m['pillar']} [{m.get('sipsung', '')}]"
                )
                lines.append(f"{m.get('reading', '')}")

    elif category == 'career':
        lines.append("💼 **직업/적성 심층 분석**\n")
        jobs = result.get('suitable_jobs', [])
        if jobs:
            lines.append(f"📌 **추천 적성 분야**: {', '.join(jobs)}\n")
        lines.append(result.get('ilgan_career_desc', ''))
        lines.append(f"\n{result.get('career_tendency', '')}")
        lines.append(f"\n⚖️ **신강/신약과 직업**\n{result.get('strength_career', '')}")
        lines.append(f"\n🏛️ **격국 특성**\n{result.get('geokguk_note', '')}")
        yj = result.get('yongsin_jobs', '')
        yd = result.get('yongsin_desc', '')
        if yj:
            lines.append(f"\n💎 **용신({result.get('yongsin', '')}) 추천 업종**: {yj}")
            lines.append(yd)
        for extra in result.get('extras', []):
            lines.append(f'\n{extra}')
        # 현재 운세와 연계한 직업 조언
        if saju_data:
            yf = saju_data.get('yearly_fortune', {})
            mf = saju_data.get('monthly_fortune', {})
            yf_sipsung = yf.get('stem_sipsung', '')
            lines.append(f"\n\n📅 **{yf.get('year', '')}년 직업운 전망**")
            if yf_sipsung in ['정관', '편관']:
                lines.append("올해는 조직 내에서 책임과 권한이 커지는 해입니다. 승진이나 새로운 직책을 맡을 기회가 있어요. 원칙을 지키며 꾸준히 성과를 쌓으세요.")
            elif yf_sipsung in ['정재', '편재']:
                lines.append("올해는 재물과 연결된 직업 기회가 많습니다. 이직이나 부업을 고려하기에 좋은 시기예요. 실질적인 수익을 올릴 수 있는 방향으로 움직여보세요.")
            elif yf_sipsung in ['식신', '상관']:
                lines.append("올해는 창의력과 표현력이 빛나는 해입니다. 새로운 프로젝트를 시작하거나 자기 재능을 발휘할 기회를 적극 찾으세요.")
            elif yf_sipsung in ['비견', '겁재']:
                lines.append("올해는 경쟁이 치열하지만 자기 주도적으로 움직이면 성과를 낼 수 있어요. 협력보다 독립적인 판단이 중요한 시기입니다.")
            elif yf_sipsung in ['정인', '편인']:
                lines.append("올해는 학습과 자격 취득에 유리한 해입니다. 커리어 전환을 위한 공부나 전문성 심화에 투자하면 장기적으로 큰 결실을 맺을 거예요.")

    elif category == 'love':
        lines.append("💕 **연애/궁합 심층 분석**\n")
        lines.append(result.get('love_style', ''))
        if result.get('spouse_type'):
            lines.append(f"\n👫 **배우자상 (일지 기준)**\n{result['spouse_type']}")
        for note in result.get('spouse_notes', []):
            lines.append(f'\n{note}')
        if result.get('ilji_sipsung'):
            lines.append(f"\n💍 **일지 십성**: {result['ilji_sipsung']}")
        for extra in result.get('extras', []):
            lines.append(f'\n{extra}')
        # 올해 연애운 전망
        if saju_data:
            yf = saju_data.get('yearly_fortune', {})
            yf_sipsung = yf.get('stem_sipsung', '')
            lines.append(f"\n\n📅 **{yf.get('year', '')}년 연애운 전망**")
            if yf_sipsung in ['정재', '편재']:
                lines.append("올해는 인연이 활발하게 들어오는 해입니다. 소개팅이나 자연스러운 만남에서 좋은 인연을 만날 확률이 높아요. 적극적으로 나서보세요.")
            elif yf_sipsung in ['정관', '편관']:
                lines.append("올해는 책임감 있는 관계를 맺기 좋은 해입니다. 진지한 교제나 결혼을 고려할 수 있어요. 다만 상대를 통제하려는 태도는 금물입니다.")
            elif yf_sipsung in ['식신', '상관']:
                lines.append("올해는 매력이 빛나고 표현력이 풍부해지는 해입니다. 자연스럽게 이성의 관심을 끌 수 있지만, 말실수로 관계가 틀어지지 않도록 조심하세요.")
            elif yf_sipsung in ['비견', '겁재']:
                lines.append("올해는 연애에서 경쟁이 생기거나 삼각관계에 휘말릴 수 있어요. 기존 연인과는 서로의 공간을 존중하고, 새로운 만남에서는 신중하게 판단하세요.")
            elif yf_sipsung in ['정인', '편인']:
                lines.append("올해는 정서적으로 안정된 연애가 가능한 해입니다. 깊은 대화와 공감을 통해 관계가 한층 깊어질 수 있어요. 조용하지만 따뜻한 사랑의 시기입니다.")

    elif category == 'wealth':
        lines.append("💰 **재물운 심층 분석**\n")
        lines.append(result.get('wealth_base', ''))
        lines.append(f"\n⚖️ **신강/신약과 재물**\n{result.get('strength_note', '')}")
        if result.get('siksang_note'):
            lines.append(f"\n🍽️ **식상과 재물**\n{result['siksang_note']}")
        if result.get('geokguk_wealth'):
            lines.append(f"\n🏛️ **격국과 재물**: {result['geokguk_wealth']}")
        lines.append(f"\n💎 **{result.get('yongsin_wealth', '')}**")
        # 정재/편재 개수에 따른 조언
        jj = result.get('jeongjae_count', 0)
        pj = result.get('pyeonjae_count', 0)
        if jj + pj > 0:
            lines.append(f"\n📊 **재성 분포**: 정재 {jj}개, 편재 {pj}개")
            if jj > pj:
                lines.append("정재가 많아 꾸준한 월급/저축형 재물에 강합니다. 안정적인 재테크와 장기 투자가 유리해요.")
            elif pj > jj:
                lines.append("편재가 많아 큰 돈을 벌 기회가 있지만 지출도 큰 편입니다. 투자나 사업에서 대박의 기회가 오지만 리스크 관리가 핵심이에요.")
            else:
                lines.append("정재와 편재가 균형을 이뤄 안정적 수입과 투자 수익을 동시에 노릴 수 있어요.")
        for extra in result.get('extras', []):
            lines.append(f'\n{extra}')
        # 올해 재물운
        if saju_data:
            yf = saju_data.get('yearly_fortune', {})
            yf_sipsung = yf.get('stem_sipsung', '')
            lines.append(f"\n\n📅 **{yf.get('year', '')}년 재물운 전망**")
            if yf_sipsung in ['정재', '편재']:
                lines.append("올해는 재물운이 직접적으로 들어오는 해입니다! 수입 증가, 보너스, 부수입 등 돈과 관련된 좋은 소식이 기대돼요. 단, 과소비에 주의하세요.")
            elif yf_sipsung in ['식신', '상관']:
                lines.append("올해는 재능으로 돈을 버는 해입니다. 아이디어나 기술을 통해 새로운 수입원을 만들 수 있어요. 부업이나 프리랜서 활동도 유리합니다.")
            elif yf_sipsung in ['정관', '편관']:
                lines.append("올해는 예상치 못한 지출이 발생할 수 있어요. 세금, 벌금, 의료비 등에 대비해 비상금을 넉넉히 확보해두세요. 하반기로 갈수록 안정됩니다.")
            elif yf_sipsung in ['비견', '겁재']:
                lines.append("올해는 돈을 쓸 일이 많고 경쟁으로 수입이 나뉠 수 있어요. 보증이나 동업은 피하고, 절약과 저축에 집중하는 것이 현명합니다.")
            elif yf_sipsung in ['정인', '편인']:
                lines.append("올해는 큰 돈보다 지식과 자격에 투자하는 것이 장기적으로 유리해요. 당장의 수입보다 미래 가치를 높이는 데 집중하세요.")

    elif category == 'health':
        lines.append("🏥 **건강 심층 분석**\n")
        lines.append(result.get('overall', ''))
        organs = result.get('base_organs', '')
        if organs:
            lines.append(f"\n🫀 **일간 기본 관련 장기**: {organs}")
            lines.append(f"🌿 **기본 관리법**: {result.get('base_advice', '')}")
        lines.append(f"\n⚖️ **체질 특성**\n{result.get('strength_health', '')}")
        for w in result.get('health_warnings', []):
            emoji = '⚠️' if w['type'] == '부족' else '🔴'
            lines.append(f"\n{emoji} **{w['element']} {w['type']}**")
            lines.append(f"  관련 장기: {w['organs']}")
            lines.append(f"  {w['risk']}")
            lines.append(f"  💊 **관리법**: {w['advice']}")
        # 부족/과다 오행 요약
        weak = result.get('weak_elements', [])
        excess = result.get('excess_elements', [])
        if weak or excess:
            lines.append("\n\n📋 **오행 건강 요약**")
            if weak:
                lines.append(f"  부족한 오행: {', '.join(weak)} → 해당 장기 기능 저하 주의")
            if excess:
                lines.append(f"  과다한 오행: {', '.join(excess)} → 해당 장기 과부하 주의")
        # 올해 건강운
        if saju_data:
            yf = saju_data.get('yearly_fortune', {})
            yf_sipsung = yf.get('stem_sipsung', '')
            lines.append(f"\n\n📅 **{yf.get('year', '')}년 건강운 전망**")
            if yf_sipsung in ['편관', '정관']:
                lines.append("올해는 스트레스성 질환에 주의해야 해요. 위장, 두통, 불면증, 혈압에 신경 쓰세요. 정기 검진을 꼭 받으시고, 무리한 야근과 과음은 삼가세요.")
            elif yf_sipsung in ['식신', '상관']:
                lines.append("올해는 전반적으로 건강 회복력이 좋은 해예요. 다만 과식과 체중 증가에 주의하고, 규칙적인 운동 습관을 들이면 체력이 크게 좋아질 거예요.")
            elif yf_sipsung in ['비견', '겁재']:
                lines.append("올해는 과로와 무리한 활동으로 체력이 소모되기 쉬워요. 충분한 수면과 휴식이 필수이며, 무리한 운동보다 꾸준한 걷기가 좋습니다.")
            elif yf_sipsung in ['정재', '편재']:
                lines.append("올해는 비교적 안정된 건강 상태를 유지할 수 있어요. 다만 업무 스트레스로 인한 긴장성 통증이 올 수 있으니, 스트레칭과 마사지로 관리하세요.")
            elif yf_sipsung in ['정인', '편인']:
                lines.append("올해는 정신 건강에 신경 쓸 필요가 있어요. 생각이 많아지고 걱정이 늘어날 수 있으니, 명상이나 취미 활동으로 마음의 여유를 찾으세요.")

    elif category == 'supplement':
        lines.append("🔄 **오행 보충/사주 보완 가이드**\n")
        if saju_data:
            lines.append(format_oheng_bar(saju_data))
            lines.append('')
        lines.append(f"📊 **오행 균형 분석**\n{result.get('overall_balance', '')}\n")
        for s in result.get('supplements', []):
            lines.append(f"\n🌿 **{s['element']}({s['status']}) 보충법**")
            lines.append(f"🎨 **추천 색상**: {s['colors']}")
            lines.append(f"🧭 **방향**: {s['directions']}")
            lines.append(f"🍽️ **음식**: {s['foods']}")
            lines.append(f"🏃 **활동**: {s['activities']}")
            lines.append(f"📅 **계절**: {s['season']}")
            lines.append(f"🔢 **숫자**: {s['numbers']}")
            lines.append(f"🏢 **직업 환경**: {s['career_env']}")
            lines.append(f"\n💡 **일상 팁**: {s['daily_tips']}")
        if result.get('yongsin_supplement'):
            lines.append(f"\n💎 **용신 활용법**\n{result['yongsin_supplement']}")
        if result.get('strength_advice'):
            lines.append(f"\n⚖️ **신강/신약 조언**\n{result['strength_advice']}")
        if result.get('seasonal_guide'):
            lines.append(f"\n🌸 **계절 가이드**\n{result['seasonal_guide']}")
        if result.get('naming_advice'):
            lines.append(f"\n✍️ **작명 참고**\n{result['naming_advice']}")

    else:
        return json.dumps(result, ensure_ascii=False, indent=2)

    if saju_data and category not in ('fortune', 'monthly', 'supplement'):
        lines.append(format_lucky_items(saju_data))

    lines.append(FOLLOW_UP.get(category, ''))
    return '\n'.join(lines)


# ── Gemini 시스템 프롬프트 (풍부한 사주 컨텍스트 포함) ──

def _build_system_prompt(nickname: str, saju_data: dict) -> str:
    """Gemini용 시스템 프롬프트 — 사주 데이터 전체 포함"""
    pillars = saju_data.get('pillars', {})
    ilgan = saju_data.get('birth_info', {}).get('ilgan', '알수없음')
    strength = saju_data.get('strength', {}).get('strength', '알수없음')
    yongsin = saju_data.get('yongsin', {}).get('yongsin', '알수없음')
    geokguk = saju_data.get('geokguk', {}).get('geokguk', '알수없음')
    cd = saju_data.get('current_daeun', {})
    yf = saju_data.get('yearly_fortune', {})
    mf = saju_data.get('monthly_fortune', {})

    # 사주 팔자
    p_year = pillars.get('year', {})
    p_month = pillars.get('month', {})
    p_day = pillars.get('day', {})
    p_hour = pillars.get('hour', {})
    saju_str = (
        f"년주: {p_year.get('stem','')}{p_year.get('branch','')}, "
        f"월주: {p_month.get('stem','')}{p_month.get('branch','')}, "
        f"일주: {p_day.get('stem','')}{p_day.get('branch','')}, "
        f"시주: {p_hour.get('stem','')}{p_hour.get('branch','')}"
    )

    # 십성
    sipsung = saju_data.get('sipsung', {})
    sipsung_str = ', '.join(
        f"{k}주: {v.get('stem_sipsung', '')}"
        for k, v in sipsung.items() if v.get('stem_sipsung')
    )

    # 오행 균형
    balance = saju_data.get('oheng_balance', {})
    oheng_str = ', '.join(
        f"{elem}: {info.get('count', 0)}개({info.get('status', '')})"
        for elem, info in balance.items()
    ) if balance else ''

    # 신살
    sinsal = saju_data.get('sinsal', [])
    sinsal_str = ', '.join(s.get('name', '') for s in sinsal) if sinsal else '없음'

    # 대운 목록
    daeun_list = saju_data.get('daeun', {}).get('daeun_list', [])
    daeun_str = ', '.join(
        f"{d['start_age']}~{d['end_age']}세: {d['pillar']}({d.get('stem_sipsung','')})"
        for d in daeun_list
    ) if daeun_list else ''

    # 월운 목록
    monthly_fortunes = saju_data.get('all_monthly_fortunes', [])
    monthly_str = '\n'.join(
        f"  {m['month']}월({m.get('start','')})~: {m['pillar']} [{m.get('sipsung','')}] — {m.get('reading','')}"
        for m in monthly_fortunes
    ) if monthly_fortunes else ''

    # 용신별 행운 아이템
    LUCKY = {
        '목': '행운색: 초록/연두, 숫자: 3·8, 방위: 동쪽, 계절: 봄, 아이템: 나무소품/화분',
        '화': '행운색: 빨강/보라, 숫자: 2·7, 방위: 남쪽, 계절: 여름, 아이템: 촛불/빨간소품',
        '토': '행운색: 노랑/갈색, 숫자: 5·10, 방위: 중앙, 계절: 환절기, 아이템: 도자기/흙소품',
        '금': '행운색: 흰색/금색, 숫자: 4·9, 방위: 서쪽, 계절: 가을, 아이템: 금속액세서리',
        '수': '행운색: 검정/남색, 숫자: 1·6, 방위: 북쪽, 계절: 겨울, 아이템: 수정/물관련소품',
    }
    lucky_str = LUCKY.get(yongsin, '')

    # 스코어
    scores = calculate_scores(saju_data)
    stars = lambda n: '★' * n + '☆' * (5 - n)
    score_str = (
        f"총운: {stars(scores.get('overall',3))}, "
        f"직업: {stars(scores.get('career',3))}, "
        f"재물: {stars(scores.get('wealth',3))}, "
        f"연애: {stars(scores.get('love',3))}, "
        f"건강: {stars(scores.get('health',3))}, "
        f"학업: {stars(scores.get('study',3))}, "
        f"대인: {stars(scores.get('relations',3))}"
    )

    return f"""당신은 사주명리학에 통달한 따뜻한 사주 상담사 '사주멘토'입니다.

## 상담 대상
이름: {nickname}님

## 사주 팔자
{saju_str}
일간: {ilgan}, 신강/신약: {strength}, 격국: {geokguk}, 용신: {yongsin}
십성: {sipsung_str}
오행 균형: {oheng_str}
신살: {sinsal_str}

## 현재 운세
대운(10년): {cd.get('pillar', '-')} ({cd.get('start_age', '')}~{cd.get('end_age', '')}세, {cd.get('stem_sipsung', '')})
{yf.get('year', '')}년 세운: {yf.get('pillar', '-')} ({yf.get('stem_sipsung', '')}, 오행: {yf.get('oheng', '')})
{mf.get('month', '')}월 월운: {mf.get('pillar', '-')} ({mf.get('stem_sipsung', '')})

## {yf.get('year', '')}년 운세 스코어
{score_str}

## 대운 흐름
{daeun_str}

## {yf.get('year', '')}년 12개월 월운
{monthly_str}

## 용신({yongsin}) 행운 아이템
{lucky_str}

## 상담 규칙
1. 항상 '{nickname}님'으로 다정하게 호칭
2. 위 사주 데이터에 근거한 전문적이면서 따뜻한 풀이
3. 사용자가 물은 것에 집중해서 답변 (불필요한 정보 나열 금지)
4. 구체적 예시와 시기를 포함해 실용적으로
5. 긍정 80% + 주의 20% (흉한 내용도 희망적으로 마무리)
6. 다정하고 친근한 말투 (존댓말)
7. 답변 마지막에 연관 주제 1~2개 추천
8. 마크다운 형식 사용 (**굵게**, 이모지 적절히)
9. 올해 운세를 물으면: 스코어 + 분야별 상세(직업/재물/연애/건강) + 핵심조언 위주로. 대운 흐름이나 행운 아이템은 별도로 물어볼 때만 제공
10. 월별 운세를 물으면: 12개월 각 월의 간지/십성/한줄 해석 + 현재 달 상세
11. 오행 보충을 물으면: 오행 균형 분석 + 부족 오행 보충법 + 행운 아이템
12. 대운/행운아이템/신살 등은 해당 질문이 들어올 때만 상세히 답변"""


class ChatService:
    async def init_db(self):
        await db.init()

    async def login(
        self, nickname: str, birth_year: int, birth_month: int,
        birth_day: int, birth_hour: int, birth_minute: int = 0,
        gender: str = 'male', calendar_type: str = 'solar',
        is_intercalation: bool = False,
    ) -> dict:
        user = await profile_mgr.find_or_create(
            nickname, birth_year, birth_month, birth_day,
            birth_hour, birth_minute, gender
        )
        saju_result = calculate_saju(
            birth_year, birth_month, birth_day,
            birth_hour, birth_minute, gender,
            calendar_type=calendar_type,
            is_intercalation=is_intercalation,
        )
        await profile_mgr.update_saju_data(user['id'], saju_result.to_dict())
        greeting = interpreter.get_greeting(saju_result)
        await history_mgr.add_message(user['id'], 'assistant', greeting)
        msg_count = await history_mgr.get_message_count(user['id'])
        is_returning = msg_count > 1
        if is_returning:
            greeting = f"다시 오셨군요, {nickname}님! 반갑습니다 😊\n\n" + greeting
        return {
            'user_id': user['id'],
            'nickname': nickname,
            'greeting': greeting,
            'saju': saju_result.to_dict(),
            'is_returning': is_returning,
        }

    async def chat(self, user_id: int, message: str) -> dict:
        await history_mgr.add_message(user_id, 'user', message)
        saju_data = await profile_mgr.get_saju_data(user_id)
        user_info = await profile_mgr.get_user(user_id)
        nickname = user_info.get('nickname', '사용자') if user_info else '사용자'

        if not saju_data:
            return {'response': f'{nickname}님, 먼저 생년월일시를 입력해주세요.', 'category': None}

        from datetime import datetime
        from modules.calculator.daeun import get_current_fortune, get_yearly_monthly_fortunes
        now = datetime.now()
        cf = get_current_fortune(saju_data['pillars'], now)
        saju_data['yearly_fortune'] = cf['yearly']
        saju_data['monthly_fortune'] = cf['monthly']
        saju_data['all_monthly_fortunes'] = get_yearly_monthly_fortunes(
            saju_data['pillars'], now.year
        )

        category = detect_category(message)

        # 모든 대화를 Gemini API로 전송
        try:
            system_prompt = _build_system_prompt(nickname, saju_data)
            raw_history = await history_mgr.get_history(user_id, limit=6)
            if raw_history and raw_history[-1]['role'] == 'user' and raw_history[-1]['message'] == message:
                raw_history = raw_history[:-1]
            response = await gemini_generate(system_prompt, message, raw_history)

            # 후속 질문 추천이 없으면 추가
            if "추천" not in response and "궁금" not in response:
                default_followup = "\n\n---\n💬 **다음 추천**: 성격 · 직업 · 연애 · 재물 · 건강 · 올해 운세 · 월별 운세 · 오행 보충"
                response += default_followup

        except Exception as e:
            print(f"[Gemini Error] {e}")
            # Gemini 실패 시 규칙 기반 폴백
            response = self._fallback_response(nickname, saju_data, message, category)

        await history_mgr.add_message(user_id, 'assistant', response, category)
        return {'response': response, 'category': category}

    def _fallback_response(self, nickname: str, saju_data: dict, message: str, category: str | None) -> str:
        """Gemini 실패 시 규칙 기반 폴백"""
        if category:
            saju_result = type('SajuResult', (), {'to_dict': lambda self: saju_data})()
            interp_category = 'fortune' if category == 'monthly' else category
            interp = interpreter.interpret_category(saju_result, interp_category)
            return format_interpretation(category, interp, saju_data)

        ilgan = saju_data.get('birth_info', {}).get('ilgan', '')
        strength = saju_data.get('strength', {}).get('strength', '')
        yongsin = saju_data.get('yongsin', {}).get('yongsin', '')
        cd = saju_data.get('current_daeun', {})
        yf = saju_data.get('yearly_fortune', {})
        mf = saju_data.get('monthly_fortune', {})

        return (
            f"{nickname}님, 말씀하신 부분에 대해 답변드릴게요.\n\n"
            f"{nickname}님은 **{ilgan}일간**({strength})이며, "
            f"용신은 **{yongsin}**입니다.\n"
            f"현재 **{cd.get('pillar', '')} 대운**, "
            f"**{yf.get('pillar', '')}년 세운**, "
            f"**{mf.get('pillar', '')}월 월운**을 지나고 있어요.\n\n"
            f"더 구체적인 분석을 원하시면 아래 주제를 말씀해주세요!\n\n"
            f"🔮 **성격** · **직업** · **연애** · **재물** · **건강** · **올해 운세** · **월별 운세** · **오행보충**"
        )
