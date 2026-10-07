"""forecast_records.csv에 기록된 기온 예보를 날짜순으로 보여 줍니다.

새 예보는 조회하지 않고, 파일에 있는 내용만 보여 줍니다.
파일을 읽는 기능은 같은 폴더에 있는 record_forecast.py에서 가져다 씁니다.

실행 방법: uv run show_records.py
"""

import csv
import os
import sys
from datetime import date

from record_forecast import RECORD_FILE, load_records


def get_date(row):
    """정렬할 때 기준으로 쓸 날짜를 돌려줍니다. 날짜 모양이 아니면 ValueError가 납니다."""
    try:
        return date.fromisoformat(row["date"])
    except ValueError:
        raise ValueError("날짜가 아닌 값이 들어 있습니다: " + row["date"])


def main():
    if not os.path.exists(RECORD_FILE):
        print("안내: " + RECORD_FILE + " 파일이 없습니다.", file=sys.stderr)
        print("먼저 uv run record_forecast.py 로 예보를 기록해 주세요.", file=sys.stderr)
        return 1

    try:
        records = load_records()
        records.sort(key=get_date)  # 날짜가 빠른 것부터 차례로 놓기
    except (ValueError, csv.Error) as error:
        # 열 이름이 다르거나, 칸 수가 안 맞거나, 글자가 깨졌거나, 날짜가 이상할 때
        print("오류: " + RECORD_FILE + " 파일을 읽을 수 없습니다. " + str(error), file=sys.stderr)
        return 1
    except OSError as error:
        print("오류: " + RECORD_FILE + " 파일을 열 수 없습니다. " + str(error), file=sys.stderr)
        return 1

    if not records:
        print(RECORD_FILE + " 파일에 기록이 아직 없습니다.")
        return 0

    print("서울 기온 예보 기록 (" + RECORD_FILE + ")")
    print("날짜         최고기온(°C)  최저기온(°C)")
    for row in records:
        print(row["date"].ljust(10) + row["max"].rjust(15) + row["min"].rjust(14))
    print("모두 " + str(len(records)) + "건")
    return 0


if __name__ == "__main__":
    sys.exit(main())
