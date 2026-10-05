# record_forecast_checked.py
import csv
import json
import math
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


def save_forecast(filename, today, highest, lowest):
    fieldnames = ["date", "max", "min"]
    records = []

    # 현재 작업 폴더의 기존 기록을 읽습니다.
    try:
        with open(filename, "r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file, strict=True)
            if reader.fieldnames != fieldnames:
                raise ValueError("기록 파일의 열 이름이 date,max,min이 아닙니다.")

            for row in reader:
                if None in row or any(
                    row[key] is None or not row[key].strip()
                    for key in fieldnames
                ):
                    raise ValueError("기록 파일에 잘못된 행이 있습니다.")

                # 같은 날짜의 기존 기록은 제외하고 다른 날짜는 유지합니다.
                if row["date"] != today:
                    records.append(row)
    except FileNotFoundError:
        pass

    records.append({"date": today, "max": highest, "min": lowest})

    # 현재 작업 폴더에 임시 파일을 완성한 뒤 기존 파일을 교체합니다.
    # 읽기 또는 쓰기에 실패하면 기존 기록 파일을 그대로 유지합니다.
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=".",
            prefix=".forecast_records_",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = file.name
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
            file.flush()
            os.fsync(file.fileno())

        os.replace(temporary_path, filename)
        temporary_path = None
    finally:
        if temporary_path is not None:
            try:
                os.remove(temporary_path)
            except OSError:
                pass


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

        # 응답 시간대가 서울인지 확인한 뒤에만 자료를 사용합니다.
        if data.get("timezone") != "Asia/Seoul":
            raise ValueError(
                "응답 시간대가 Asia/Seoul이 아니거나 누락되었습니다. "
                "기존 기록 파일은 변경하지 않았습니다."
            )

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

    # 모든 자료가 정상일 때만 결과를 표시하고 기록을 저장합니다.
    print(f"서울 오늘의 기온 예보 — {today} (서울 시간)")
    print(f"최고기온: {highest:.1f} °C")
    print(f"최저기온: {lowest:.1f} °C")

    filename = "forecast_records.csv"
    try:
        save_forecast(filename, today, highest, lowest)
    except (OSError, ValueError, csv.Error) as error:
        print(
            f"오류: 예보를 저장하지 못했습니다. "
            f"기존 기록 파일은 변경하지 않았습니다. {error}",
            file=sys.stderr,
        )
        return 1

    print(f"저장한 파일: {filename}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
