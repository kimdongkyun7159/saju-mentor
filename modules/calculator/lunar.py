"""음력 ↔ 양력 변환 — korean-lunar-calendar 기반"""

from korean_lunar_calendar import KoreanLunarCalendar


class InvalidLunarDateError(ValueError):
    """유효하지 않은 음력 날짜"""
    pass


def lunar_to_solar(
    year: int, month: int, day: int,
    is_intercalation: bool = False,
) -> tuple[int, int, int]:
    """음력 날짜를 양력으로 변환

    Args:
        year, month, day: 음력 년월일
        is_intercalation: True=윤달

    Returns:
        (양력_year, 양력_month, 양력_day)

    Raises:
        InvalidLunarDateError: 유효하지 않은 음력 날짜
    """
    cal = KoreanLunarCalendar()
    if not cal.setLunarDate(year, month, day, is_intercalation):
        raise InvalidLunarDateError(
            f"유효하지 않은 음력 날짜: {year}-{month}-{day}"
            f"{' (윤달)' if is_intercalation else ''}"
        )
    # 윤달 검증: 변환 후 역변환하여 윤달이 실제 존재하는지 확인
    if is_intercalation:
        verify = KoreanLunarCalendar()
        verify.setSolarDate(cal.solarYear, cal.solarMonth, cal.solarDay)
        if not verify.isIntercalation:
            raise InvalidLunarDateError(
                f"{year}년 {month}월은 윤달이 아닙니다"
            )
    return cal.solarYear, cal.solarMonth, cal.solarDay
