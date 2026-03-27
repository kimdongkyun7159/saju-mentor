"""재물운 해석 패턴 — 상담형 풀이"""

YONGSIN_WEALTH = {
    '목': '교육, 출판, 환경, 건강식품 관련 투자가 유리합니다. 봄에 시작하는 일이 좋은 결실을 맺어요.',
    '화': '기술, IT, 에너지, 엔터테인먼트 분야에서 수익이 좋습니다. 여름에 재물운이 특히 강해요.',
    '토': '부동산, 건설, 토지, 중개업이 재물운의 핵심입니다. 환절기에 좋은 기회가 와요.',
    '금': '금융, 귀금속, 기계, 법률 관련 수익이 좋습니다. 가을에 투자하면 결실을 봐요.',
    '수': '무역, 유통, 물류, 음료 사업에서 기회가 옵니다. 겨울에 씨앗을 뿌린 일이 열매를 맺어요.',
}


def interpret_wealth(data: dict) -> dict:
    sipsung_summary = data['sipsung_summary']
    yongsin = data['yongsin']
    strength = data['strength']
    sinsal_names = [s['name'] for s in data['sinsal']]
    geokguk = data['geokguk']['geokguk']

    jeongjae = sipsung_summary.get('정재', 0)
    pyeonjae = sipsung_summary.get('편재', 0)
    total_jae = jeongjae + pyeonjae
    sikshin = sipsung_summary.get('식신', 0)
    sanggwan = sipsung_summary.get('상관', 0)

    if total_jae >= 3:
        wealth_base = (
            '재성이 풍부하여 **재물 인연이 매우 강한 사주**입니다! '
            '돈을 모으고 불리는 감각이 타고났어요. '
            '여러 곳에서 수입이 들어올 수 있고, 재테크에도 관심이 많은 편이에요.\n\n'
            '다만 재성이 너무 많으면 이것저것 손대다 분산될 수 있어요. '
            '한 가지에 집중하면 더 큰 부를 쌓을 수 있습니다.'
        )
    elif total_jae == 0:
        wealth_base = (
            '사주에 재성이 직접적으로 보이지 않지만, **걱정할 필요 없어요.** '
            '재성이 없다고 돈을 못 버는 게 아닙니다. '
            '대운에서 재성이 올 때 한꺼번에 큰 돈이 들어오는 구조예요.\n\n'
            '평소에는 실력과 인맥을 쌓아두세요. '
            '때가 되면 그동안 쌓아온 것들이 돈으로 바뀌는 순간이 옵니다.'
        )
    else:
        wealth_base = (
            '적절한 재성이 있어 **안정적인 재물운**입니다. '
            '급격하게 큰돈이 들어오기보다는, 꾸준히 쌓이는 형태의 재물운이에요. '
            '무리하지 않고 착실하게 모아가는 것이 당신에게 맞는 재테크입니다.\n\n'
            '한 방을 노리기보다 장기 투자, 적금, 연금 같은 안정형이 유리해요.'
        )

    if strength['is_strong']:
        strength_note = (
            '신강한 사주라 **재물을 감당할 힘이 충분**합니다. '
            '적극적으로 투자하고 사업을 벌여도 감당할 그릇이 있어요. '
            '남들이 "위험하다"고 할 때 과감하게 도전하면 큰 성과를 낼 수 있습니다.\n\n'
            '다만 과욕은 금물! 자신의 능력을 과신하지 말고, '
            '70%의 확신이 있을 때 움직이는 것이 현명합니다.'
        )
    else:
        strength_note = (
            '신약한 사주라 **무리한 투자는 피하는 것이 좋아요.** '
            '큰 돈을 한꺼번에 움직이기보다 분산 투자, 안전 자산 중심으로 운용하세요. '
            '부동산이나 주식을 할 때도 레버리지(빚투)는 피하는 게 좋습니다.\n\n'
            '💡 신약한 분의 재테크 비결: 좋은 파트너나 전문가의 조언을 구하세요. '
            '혼자 결정하기보다 함께 할 때 더 좋은 결과가 나옵니다.'
        )

    siksang_note = ''
    if (sikshin + sanggwan) >= 2 and total_jae >= 1:
        siksang_note = (
            '🔥 **식상생재(食傷生財)** 구조가 보입니다! 이것은 정말 좋은 구조예요. '
            '당신의 재능과 노력이 자연스럽게 돈으로 이어지는 흐름입니다. '
            '즉, **좋아하는 일을 하면서 돈도 버는** 이상적인 구조예요.\n\n'
            '자격증, 기술, 콘텐츠 같은 자신만의 능력을 키우면, '
            '그것이 곧 수입원이 됩니다. 하고 싶은 일을 포기하지 마세요!'
        )

    yongsin_element = yongsin['yongsin']
    yongsin_wealth = YONGSIN_WEALTH.get(yongsin_element, '')

    # 격국별 재물 조언
    geokguk_wealth = ''
    if '재' in geokguk:
        geokguk_wealth = f'{geokguk}이라 재물을 다루는 것 자체가 당신의 핵심 역량이에요. 금융, 사업, 투자에 강합니다.'
    elif '관' in geokguk:
        geokguk_wealth = f'{geokguk}이라 조직 안에서 승진으로 수입이 늘어나는 구조예요. 직장에서의 성과가 곧 재물입니다.'
    elif '인' in geokguk:
        geokguk_wealth = f'{geokguk}이라 공부와 자격증이 돈이 되는 구조예요. 전문성을 높이는 것이 최고의 투자입니다.'
    elif '식' in geokguk or '상' in geokguk:
        geokguk_wealth = f'{geokguk}이라 재능과 기술로 돈을 버는 구조예요. 창작, 기술직, 프리랜서에 유리합니다.'

    extras = []
    if '천을귀인' in sinsal_names:
        extras.append(
            '✨ **천을귀인** 덕분에 재물 위기가 와도 도움을 받아 넘길 수 있어요. '
            '투자 실패나 사업 위기가 와도 결국 회복하는 운이 있으니 너무 두려워하지 마세요.'
        )

    return {
        'category': '재물운',
        'wealth_base': wealth_base,
        'strength_note': strength_note,
        'siksang_note': siksang_note,
        'yongsin_wealth': f'용신({yongsin_element}) 관련: {yongsin_wealth}',
        'geokguk_wealth': geokguk_wealth,
        'jeongjae_count': jeongjae,
        'pyeonjae_count': pyeonjae,
        'extras': extras,
    }
