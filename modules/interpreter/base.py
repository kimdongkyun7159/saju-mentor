"""사주 해석 엔진 — 규칙 기반 통합 해석"""

from .patterns.personality import interpret_personality
from .patterns.career import interpret_career
from .patterns.love import interpret_love
from .patterns.wealth import interpret_wealth
from .patterns.health import interpret_health
from .patterns.fortune import interpret_fortune
from .patterns.supplement import interpret_supplement


class SajuInterpreter:
    """모듈별 독립 해석 → 통합 결과"""

    def interpret_all(self, saju_result) -> dict:
        """전체 해석 수행 — 각 모듈 독립 실행"""
        data = saju_result.to_dict()
        return {
            'personality': interpret_personality(data),
            'career': interpret_career(data),
            'love': interpret_love(data),
            'wealth': interpret_wealth(data),
            'health': interpret_health(data),
            'fortune': interpret_fortune(data),
            'supplement': interpret_supplement(data),
        }

    def interpret_category(self, saju_result, category: str) -> dict:
        """특정 카테고리만 해석"""
        data = saju_result.to_dict()
        interpreters = {
            'personality': interpret_personality,
            'career': interpret_career,
            'love': interpret_love,
            'wealth': interpret_wealth,
            'health': interpret_health,
            'fortune': interpret_fortune,
            'supplement': interpret_supplement,
        }
        func = interpreters.get(category)
        if func:
            return func(data)
        return {'error': f'알 수 없는 카테고리: {category}'}

    def get_greeting(self, saju_result) -> str:
        """첫 인사 메시지 생성"""
        info = saju_result.birth_info
        summary = saju_result.summary
        ilgan = info['ilgan']
        oheng = info['ilgan_oheng']

        greeting_map = {
            '목': f'{ilgan}목(木) 일간이시군요! 나무처럼 성장하고 뻗어나가는 성향을 가지고 계세요.',
            '화': f'{ilgan}화(火) 일간이시군요! 불꽃처럼 열정적이고 밝은 에너지의 소유자세요.',
            '토': f'{ilgan}토(土) 일간이시군요! 대지처럼 든든하고 중심을 잡아주는 분이세요.',
            '금': f'{ilgan}금(金) 일간이시군요! 보석처럼 단단하고 결단력 있는 분이세요.',
            '수': f'{ilgan}수(水) 일간이시군요! 물처럼 지혜롭고 유연한 분이세요.',
        }

        return (
            f"안녕하세요! 사주멘토입니다.\n\n"
            f"📋 사주: {summary['saju']}\n"
            f"🔮 {greeting_map.get(oheng, '')}\n"
            f"⚖️ {summary['strength']} | {summary['geokguk']}\n"
            f"💎 용신: {summary['yongsin']}\n\n"
            f"어떤 부분이 궁금하세요? "
            f"성격, 직업, 연애, 재물, 건강, 올해운세 중 골라주세요!"
        )
