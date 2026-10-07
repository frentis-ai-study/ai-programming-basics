"""서울의 오늘 최고기온과 최저기온 예보를 조회해서 CSV 파일에 기록합니다.

조회는 같은 폴더에 있는 lookup_today.py의 기능을 그대로 가져다 씁니다.

실행 방법: uv run record_forecast.py
"""

import csv
import os
import sys
import urllib.error

from lookup_today import fetch_forecast, get_today_in_seoul, read_temperatures

RECORD_FILE = "forecast_records.csv"
COLUMNS = ["date", "max", "min"]


def load_records():
    """기록 파일에 이미 있는 줄들을 리스트로 돌려줍니다. 파일이 없으면 빈 리스트입니다.

    파일의 열 이름이 예상과 다르면 ValueError를 일으킵니다.
    """
    if not os.path.exists(RECORD_FILE):
        return []

    with open(RECORD_FILE, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:  # 내용이 전혀 없는 빈 파일
            return []
        if reader.fieldnames != COLUMNS:
            raise ValueError("열 이름이 date, max, min이 아닙니다.")

        records = []
        for row in reader:
            # 칸이 모자라거나 남는 줄이 있으면 기록이 망가진 것입니다.
            if None in row or None in row.values():
                raise ValueError(str(reader.line_num) + "번째 줄의 칸 수가 맞지 않습니다.")
            records.append(row)
        return records


def update_records(records, today, highest, lowest):
    """같은 날짜의 기록이 있으면 새 예보로 바꾸고, 없으면 맨 뒤에 덧붙입니다."""
    new_row = {"date": today, "max": highest, "min": lowest}

    updated = []
    replaced = False
    for row in records:
        if row["date"] == today:
            if not replaced:  # 같은 날짜가 여러 줄 있어도 한 줄만 남깁니다.
                updated.append(new_row)
                replaced = True
        else:
            updated.append(row)

    if not replaced:
        updated.append(new_row)
    return updated


def save_records(records):
    """기록을 파일에 저장합니다.

    임시 파일에 먼저 다 쓴 다음 이름을 바꾸므로,
    쓰는 도중에 문제가 생겨도 기존 파일은 망가지지 않습니다.
    """
    temp_file = RECORD_FILE + ".tmp"
    with open(temp_file, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(records)
    os.replace(temp_file, RECORD_FILE)


def main():
    today = get_today_in_seoul()

    # 1단계: 조회. 여기서 실패하면 파일은 건드리지 않고 끝냅니다.
    try:
        data = fetch_forecast(today)
        highest, lowest = read_temperatures(data, today)
    except urllib.error.HTTPError as error:
        print("오류: 날씨 서버가 요청을 거절했습니다. (HTTP " + str(error.code) + ")", file=sys.stderr)
        print(RECORD_FILE + " 파일은 바꾸지 않았습니다.", file=sys.stderr)
        return 1
    except (urllib.error.URLError, OSError) as error:
        print("오류: 날씨 정보를 받지 못했습니다. 인터넷 연결을 확인해 주세요.", file=sys.stderr)
        print("(자세한 내용: " + str(error) + ")", file=sys.stderr)
        print(RECORD_FILE + " 파일은 바꾸지 않았습니다.", file=sys.stderr)
        return 1
    except ValueError as error:
        print("오류: 날씨 정보를 읽지 못했습니다. " + str(error), file=sys.stderr)
        print(RECORD_FILE + " 파일은 바꾸지 않았습니다.", file=sys.stderr)
        return 1

    # 2단계: 기록. 기존 기록을 읽고, 오늘 것을 넣거나 바꾼 뒤 저장합니다.
    try:
        records = load_records()
    except (ValueError, csv.Error) as error:
        # 기존 파일 내용이 이상하면 덮어쓰지 않고 그대로 둡니다.
        print("오류: 기존 " + RECORD_FILE + " 파일을 읽지 못했습니다. " + str(error), file=sys.stderr)
        print(RECORD_FILE + " 파일은 바꾸지 않았습니다.", file=sys.stderr)
        return 1
    except OSError as error:
        print("오류: 기존 " + RECORD_FILE + " 파일을 열지 못했습니다. " + str(error), file=sys.stderr)
        return 1

    records = update_records(records, today, highest, lowest)

    try:
        save_records(records)
    except OSError as error:
        print("오류: " + RECORD_FILE + " 파일에 저장하지 못했습니다. " + str(error), file=sys.stderr)
        return 1

    print("서울 오늘의 기온 예보 (Open-Meteo)")
    print("날짜: " + today)
    print("최고기온: " + str(highest) + " °C")
    print("최저기온: " + str(lowest) + " °C")
    print("저장한 파일: " + RECORD_FILE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
