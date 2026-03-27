"""격국(格局) 판별 — 월지 정기 투간 기준"""

from .constants import CHEONGAN, JIJANGGAN, CHEONGAN_OHENG
from .sipsung import get_sipsung


def determine_geokguk(pillars: dict) -> dict:
    """격국 판별: 월지 정기가 천간에 투간했는지 확인"""
    ilgan = pillars['day']['stem']
    wolji = pillars['month']['branch']
    jijang = JIJANGGAN[wolji]
    jeongi = jijang[2]  # 정기
    junggi = jijang[1]  # 중기
    yugi = jijang[0]    # 여기

    # 투간 확인: 월지 지장간이 년/월/시 천간에 나타나는지
    visible_stems = [
        pillars['year']['stem'],
        pillars['month']['stem'],
        pillars['hour']['stem'],
    ]

    geokguk = None
    source = None

    # 1순위: 정기 투간
    if jeongi and jeongi in visible_stems:
        geokguk = get_sipsung(ilgan, jeongi)
        source = f'{jeongi}({CHEONGAN_OHENG[jeongi]}) 정기 투간'

    # 2순위: 중기 투간
    elif junggi and junggi in visible_stems:
        geokguk = get_sipsung(ilgan, junggi)
        source = f'{junggi}({CHEONGAN_OHENG[junggi]}) 중기 투간'

    # 3순위: 여기 투간
    elif yugi and yugi in visible_stems:
        geokguk = get_sipsung(ilgan, yugi)
        source = f'{yugi}({CHEONGAN_OHENG[yugi]}) 여기 투간'

    # 투간 없으면 정기 자체를 격국으로
    else:
        if jeongi:
            geokguk = get_sipsung(ilgan, jeongi)
            source = f'{jeongi}({CHEONGAN_OHENG[jeongi]}) 정기 기준'

    # 비견/겁재격은 건록격/양인격으로 변환
    if geokguk == '비견':
        geokguk = '건록격'
    elif geokguk == '겁재':
        geokguk = '양인격'
    elif geokguk:
        geokguk += '격'

    return {
        'geokguk': geokguk or '미정',
        'source': source or '',
        'description': GEOKGUK_DESC.get(geokguk, ''),
    }


GEOKGUK_DESC = {
    '식신격': '온화하고 재능이 풍부. 식복, 표현력, 안정적 재물운',
    '상관격': '창의적이고 자유로운 영혼. 예술, 기술, 반골기질',
    '편재격': '사교적이고 활동적. 투자, 사업, 넓은 인맥',
    '정재격': '성실하고 꼼꼼. 저축, 안정적 직장, 가정적',
    '편관격': '카리스마와 추진력. 리더십, 군인/경찰, 개혁',
    '정관격': '품격과 책임감. 공직, 조직 관리, 명예',
    '편인격': '독창적 사고. 연구, 종교, 특수 학문',
    '정인격': '학문과 교육. 자격증, 교직, 어머니 덕',
    '건록격': '자수성가. 독립심, 직업 능력, 근면',
    '양인격': '강한 추진력. 결단력, 승부사, 리더',
}
