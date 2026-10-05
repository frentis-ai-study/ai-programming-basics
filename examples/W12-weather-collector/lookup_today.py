"""서울 하루 예보를 조회하고 화면에 표시하는 수업용 작은 예제."""
import argparse
import json
import math
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

API_URL = "https://api.open-meteo.com/v1/forecast"
CONDITIONS = {
    "latitude": 37.57,
    "longitude": 126.98,
    "daily": "temperature_2m_max,temperature_2m_min",
    "forecast_days": 1,
    "timezone": "Asia/Seoul",
}


def format_forecast(payload: dict) -> str:
    """응답의 날짜·최고·최저를 학생이 읽을 두 줄로 바꾼다."""
    if payload["timezone"] != "Asia/Seoul":
        raise ValueError("날짜의 시간대가 Asia/Seoul이 아닙니다")
    units = payload["daily_units"]
    if (units["temperature_2m_max"] != "°C"
            or units["temperature_2m_min"] != "°C"):
        raise ValueError("기온 단위가 °C가 아닙니다")
    daily = payload["daily"]
    if any(len(daily[key]) != 1 for key in (
        "time", "temperature_2m_max", "temperature_2m_min"
    )):
        raise ValueError("한 날짜의 예보만 표시할 수 있습니다")
    day = daily["time"][0]
    if not isinstance(day, str):
        raise ValueError("날짜는 YYYY-MM-DD 형식이어야 합니다")
    try:
        date.fromisoformat(day)
    except ValueError as error:
        raise ValueError("날짜는 YYYY-MM-DD 형식이어야 합니다") from error
    high = daily["temperature_2m_max"][0]
    low = daily["temperature_2m_min"][0]
    if any(not isinstance(value, (int, float)) or isinstance(value, bool)
           or not math.isfinite(value) for value in (high, low)):
        raise ValueError("최고·최저기온은 유한한 숫자여야 합니다")
    if high < low:
        raise ValueError("최고기온은 최저기온보다 낮을 수 없습니다")
    return f"서울 · {day}\n최고 {high}°C · 최저 {low}°C"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="서울 하루 예보를 화면에 표시")
    parser.add_argument("--fixture", type=Path, help="인터넷 없이 보는 보관된 응답 예시(JSON)")
    parser.add_argument("--endpoint", default=API_URL, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        if args.fixture:
            payload = json.loads(args.fixture.read_text(encoding="utf-8"))
        else:
            url = args.endpoint + "?" + urlencode(CONDITIONS)
            with urlopen(url, timeout=10) as response:
                payload = json.load(response)
        output = format_forecast(payload)
    except (OSError, ValueError, KeyError, IndexError, TypeError) as error:
        print(f"오류: 응답의 날짜와 기온을 읽거나 날씨 정보를 받지 못했습니다: {error}", file=sys.stderr)
        return 1
    if args.fixture:
        print("보관 응답 예시 · 현재 예보 아님")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
