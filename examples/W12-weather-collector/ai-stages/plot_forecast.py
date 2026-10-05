# plot_forecast.py
import csv
import math
import sys
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

# Agg에서도 한글과 음수 눈금이 올바르게 표시되도록 설정합니다.
plt.rcParams["font.family"] = ["AppleGothic"]
plt.rcParams["axes.unicode_minus"] = False


def read_records(path):
    records = []
    seen_dates = set()

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, strict=True)
        if reader.fieldnames != ["date", "max", "min"]:
            raise ValueError("CSV의 열 이름은 date,max,min이어야 합니다.")

        for row in reader:
            line_number = reader.line_num
            if None in row or any(
                row[key] is None or not row[key].strip()
                for key in ("date", "max", "min")
            ):
                raise ValueError(f"{line_number}행의 자료가 누락되었거나 잘못되었습니다.")

            date_text = row["date"].strip()
            try:
                day = datetime.strptime(date_text, "%Y-%m-%d").date()
                highest = float(row["max"])
                lowest = float(row["min"])
            except ValueError as error:
                raise ValueError(
                    f"{line_number}행의 날짜 또는 기온 형식이 잘못되었습니다."
                ) from error

            if day.isoformat() != date_text:
                raise ValueError(f"{line_number}행의 날짜는 YYYY-MM-DD 형식이어야 합니다.")
            if not all(math.isfinite(value) for value in (highest, lowest)):
                raise ValueError(f"{line_number}행에 유효하지 않은 기온이 있습니다.")
            if highest < lowest:
                raise ValueError(f"{line_number}행의 최고기온이 최저기온보다 낮습니다.")
            if day in seen_dates:
                raise ValueError(f"{line_number}행의 날짜가 중복되었습니다.")

            seen_dates.add(day)
            records.append((day, highest, lowest))

    if not records:
        raise ValueError("CSV에 그릴 예보 기록이 없습니다.")

    return sorted(records, key=lambda record: record[0])


def main():
    # 실행한 현재 작업 폴더의 파일만 사용합니다.
    csv_path = Path("forecast_records.csv")
    png_path = Path("forecast_records.png")

    # 읽기와 검증을 모두 마치기 전에는 PNG를 열거나 변경하지 않습니다.
    try:
        records = read_records(csv_path)
    except FileNotFoundError:
        print(
            "안내: 현재 작업 폴더에 forecast_records.csv가 없습니다. "
            "기존 PNG는 변경하지 않았습니다.",
            file=sys.stderr,
        )
        return 1
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        print(
            f"오류: 예보 기록을 읽지 못했습니다. {error}\n"
            "기존 PNG는 변경하지 않았습니다.",
            file=sys.stderr,
        )
        return 1

    dates, highs, lows = zip(*records)
    figure = None

    try:
        figure, ax = plt.subplots(figsize=(10, 5.5), layout="constrained")

        # 실제 날짜 좌표에 기록된 값만 표시합니다.
        # 점 사이를 연결하거나 없는 날짜의 기온을 채우지 않습니다.
        ax.scatter(
            dates, highs, color="tab:red", marker="o",
            s=55, label="최고기온", zorder=3,
        )
        ax.scatter(
            dates, lows, color="tab:blue", marker="v",
            s=55, label="최저기온", zorder=3,
        )

        ax.set_title("서울 예보 기록")
        ax.set_xlabel("날짜")
        ax.set_ylabel("기온 (°C)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
        ax.margins(y=0.15)

        span = (dates[-1] - dates[0]).days
        tick_interval = max(1, math.ceil((span + 2) / 8))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=tick_interval))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.set_xlim(
            dates[0] - timedelta(days=1),
            dates[-1] + timedelta(days=1),
        )
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

        # 렌더링까지 성공한 뒤 결과 파일을 저장합니다.
        with BytesIO() as buffer:
            figure.savefig(buffer, format="png", dpi=150)
            png_data = buffer.getvalue()

    except Exception as error:
        print(
            f"오류: 그래프를 만들지 못했습니다. {error}\n"
            "기존 PNG는 변경하지 않았습니다.",
            file=sys.stderr,
        )
        return 1
    finally:
        if figure is not None:
            plt.close(figure)

    try:
        png_path.write_bytes(png_data)
    except OSError as error:
        print(f"오류: PNG를 저장하지 못했습니다. {error}", file=sys.stderr)
        return 1

    print(f"저장한 파일: {png_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
