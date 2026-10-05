import json
import math
import sys
from datetime import datetime, timedelta, timezone
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


def main():
    # 컴퓨터의 시간대와 관계없이 서울 시간(UTC+9)으로 계산합니다.
    seoul_time = timezone(timedelta(hours=9))
    today = datetime.now(seoul_time).date().isoformat()

    # 서울 좌표와 조회할 날짜, 기온 단위를 지정합니다.
    params = {
        "latitude": 37.5665,
        "longitude": 126.9780,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "Asia/Seoul",
        "temperature_unit": "celsius",
        "start_date": today,
        "end_date": today,
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urlencode(params)

    try:
        # 응답을 최대 15초 동안 기다립니다.
        with urlopen(url, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

        if not isinstance(data, dict):
            raise ValueError("응답이 예상한 형식이 아닙니다.")

        if data.get("error"):
            raise ValueError(data.get("reason", "API가 오류를 반환했습니다."))

        daily = data["daily"]
        dates = daily["time"]

        if not isinstance(dates, list) or dates != [today]:
            raise ValueError("서울 시간 기준 오늘의 날짜가 없습니다.")

        temperatures = []
        for key in ("temperature_2m_max", "temperature_2m_min"):
            values = daily[key]
            if not isinstance(values, list) or len(values) != 1:
                raise ValueError("기온 자료가 없거나 형식이 잘못되었습니다.")

            value = values[0]
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError("유효한 기온 값이 없습니다.")

            if data["daily_units"][key] != "°C":
                raise ValueError("기온 단위가 섭씨가 아닙니다.")

            temperatures.append(value)

        highest, lowest = temperatures
        if highest < lowest:
            raise ValueError("최고기온이 최저기온보다 낮습니다.")

    except HTTPError as error:
        print(f"오류: 날씨 서버가 HTTP {error.code} 오류를 반환했습니다.",
              file=sys.stderr)
        return 1
    except (URLError, OSError, HTTPException) as error:
        print(f"오류: 날씨 정보를 받지 못했습니다. {error}", file=sys.stderr)
        return 1
    except (ValueError, KeyError, TypeError, IndexError) as error:
        print(f"오류: 날씨 정보를 읽지 못했습니다. {error}", file=sys.stderr)
        return 1

    # 모든 자료가 정상일 때만 결과를 표시합니다.
    print(f"서울 오늘의 기온 예보 — {today} (서울 시간)")
    print(f"최고기온: {highest:.1f} °C")
    print(f"최저기온: {lowest:.1f} °C")
    return 0


if __name__ == "__main__":
    sys.exit(main())
