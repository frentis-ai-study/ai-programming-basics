"""Open-Meteo에서 서울의 오늘 최고기온과 최저기온 예보를 조회합니다.

실행 방법: uv run lookup_today.py
"""

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

# 서울의 위도와 경도
SEOUL_LATITUDE = 37.5665
SEOUL_LONGITUDE = 126.9780

# 서울 시간은 세계 표준시(UTC)보다 항상 9시간 빠릅니다. (서머타임 없음)
SEOUL_TIME = timezone(timedelta(hours=9))

API_URL = "https://api.open-meteo.com/v1/forecast"


def get_today_in_seoul():
    """서울 시간 기준 오늘 날짜를 '2026-10-07' 같은 글자로 돌려줍니다."""
    return datetime.now(SEOUL_TIME).strftime("%Y-%m-%d")


def fetch_forecast(today):
    """Open-Meteo에 오늘 하루치 예보를 요청하고, 받은 내용을 딕셔너리로 돌려줍니다."""
    params = {
        "latitude": SEOUL_LATITUDE,
        "longitude": SEOUL_LONGITUDE,
        "daily": "temperature_2m_max,temperature_2m_min",
        "temperature_unit": "celsius",
        "timezone": "Asia/Seoul",
        "start_date": today,
        "end_date": today,
    }
    url = API_URL + "?" + urllib.parse.urlencode(params)

    with urllib.request.urlopen(url, timeout=10) as response:
        text = response.read().decode("utf-8")
    return json.loads(text)


def read_temperatures(data, today):
    """받은 내용에서 오늘의 최고기온과 최저기온을 꺼냅니다.

    내용이 예상과 다르면 ValueError를 일으킵니다.
    """
    try:
        daily = data["daily"]
        dates = daily["time"]
        max_list = daily["temperature_2m_max"]
        min_list = daily["temperature_2m_min"]
        index = dates.index(today)  # 오늘 날짜가 몇 번째에 있는지 찾기
        highest = max_list[index]
        lowest = min_list[index]
    except (KeyError, IndexError, TypeError, ValueError, AttributeError):
        raise ValueError("받은 날씨 정보에 오늘(" + today + ") 기온이 들어 있지 않습니다.")

    for value in (highest, lowest):
        # True/False도 숫자로 취급되므로 따로 걸러 냅니다.
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("받은 날씨 정보의 기온 값이 숫자가 아닙니다.")

    return highest, lowest


def main():
    today = get_today_in_seoul()

    try:
        data = fetch_forecast(today)
        highest, lowest = read_temperatures(data, today)
    except urllib.error.HTTPError as error:
        print("오류: 날씨 서버가 요청을 거절했습니다. (HTTP " + str(error.code) + ")", file=sys.stderr)
        return 1
    except (urllib.error.URLError, OSError) as error:
        # 인터넷 연결이 없거나 서버 응답이 너무 늦을 때
        print("오류: 날씨 정보를 받지 못했습니다. 인터넷 연결을 확인해 주세요.", file=sys.stderr)
        print("(자세한 내용: " + str(error) + ")", file=sys.stderr)
        return 1
    except ValueError as error:
        # 받은 내용이 JSON이 아니거나, 필요한 값이 없을 때
        print("오류: 날씨 정보를 읽지 못했습니다. " + str(error), file=sys.stderr)
        return 1

    print("서울 오늘의 기온 예보 (Open-Meteo)")
    print("날짜: " + today)
    print("최고기온: " + str(highest) + " °C")
    print("최저기온: " + str(lowest) + " °C")
    return 0


if __name__ == "__main__":
    sys.exit(main())
