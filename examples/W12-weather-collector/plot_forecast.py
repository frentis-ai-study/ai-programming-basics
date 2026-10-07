# /// script
# requires-python = ">=3.9"
# dependencies = ["matplotlib"]
# ///
# ↑ 위 네 줄은 uv에게 "이 프로그램은 matplotlib이 필요하다"고 알려 주는 표시입니다.
#   지우지 마세요. uv run 으로 실행하면 uv가 알아서 matplotlib을 준비합니다.
"""forecast_records.csv의 기록으로 그래프를 그려 forecast_records.png로 저장합니다.

새 예보는 조회하지 않고, 파일에 있는 기록만 그립니다.
파일을 읽는 기능은 같은 폴더에 있는 record_forecast.py에서 가져다 씁니다.

실행 방법: uv run plot_forecast.py
"""

import csv
import os
import sys
from datetime import date, timedelta

import matplotlib

matplotlib.use("Agg")  # 화면에 창을 띄우지 않고 그림 파일만 만들기

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib import font_manager

from record_forecast import RECORD_FILE, load_records

GRAPH_FILE = "forecast_records.png"
GRAPH_TITLE = "서울 예보 기록"

# 한글을 그릴 수 있는 글꼴 후보 (macOS, Windows, Linux 순서)
KOREAN_FONTS = [
    "Apple SD Gothic Neo",
    "AppleGothic",
    "Malgun Gothic",
    "NanumGothic",
    "Noto Sans CJK KR",
    "Noto Sans KR",
]

MAX_COLOR = "#eb6834"  # 최고기온: 주황
MIN_COLOR = "#2a78d6"  # 최저기온: 파랑
TEXT_COLOR = "#52514e"
GRID_COLOR = "#e4e3df"


def find_korean_font():
    """컴퓨터에 설치된 한글 글꼴 이름을 하나 찾아 돌려줍니다. 없으면 None입니다."""
    installed = set()
    for font in font_manager.fontManager.ttflist:
        installed.add(font.name)
    for name in KOREAN_FONTS:
        if name in installed:
            return name
    return None


def read_points(records):
    """기록에서 날짜, 최고기온, 최저기온 리스트를 날짜순으로 만들어 돌려줍니다.

    날짜나 기온이 올바른 값이 아니면 ValueError를 일으킵니다.
    """
    points = []
    for row in records:
        try:
            day = date.fromisoformat(row["date"])
        except ValueError:
            raise ValueError("날짜가 아닌 값이 들어 있습니다: " + row["date"])
        try:
            highest = float(row["max"])
            lowest = float(row["min"])
        except ValueError:
            raise ValueError(row["date"] + "의 기온이 숫자가 아닙니다.")
        if highest != highest or lowest != lowest or abs(highest) == float("inf") or abs(lowest) == float("inf"):
            raise ValueError(row["date"] + "의 기온이 올바른 숫자가 아닙니다.")
        points.append((day, highest, lowest))

    points.sort()
    days = [point[0] for point in points]
    max_temps = [point[1] for point in points]
    min_temps = [point[2] for point in points]
    return days, max_temps, min_temps


def draw_graph(days, max_temps, min_temps):
    """그래프를 그려서 그림 파일로 저장합니다."""
    figure, axes = plt.subplots(figsize=(8, 4.5))

    # 기록이 있는 날짜에만 점을 찍습니다. 점 사이를 선으로 잇지 않으므로
    # 기록이 없는 날짜는 빈 채로 남습니다.
    axes.scatter(days, max_temps, color=MAX_COLOR, marker="o", s=60,
                 edgecolors="white", linewidths=1, label="최고기온", zorder=3)
    axes.scatter(days, min_temps, color=MIN_COLOR, marker="s", s=60,
                 edgecolors="white", linewidths=1, label="최저기온", zorder=3)

    axes.set_title(GRAPH_TITLE, fontsize=14, pad=12)
    axes.set_xlabel("날짜", color=TEXT_COLOR)
    axes.set_ylabel("기온 (°C)", color=TEXT_COLOR)

    # 가로축: 하루 단위로 눈금을 두되, 기간이 길면 눈금 간격을 넓힙니다.
    span = (days[-1] - days[0]).days
    axes.set_xlim(days[0] - timedelta(days=1), days[-1] + timedelta(days=1))
    axes.xaxis.set_major_locator(mdates.DayLocator(interval=span // 8 + 1))
    axes.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    figure.autofmt_xdate()

    # 세로축: 점이 위아래 끝에 붙지 않게 여유를 둡니다.
    axes.set_ylim(min(min_temps) - 2, max(max_temps) + 2)

    axes.grid(axis="y", color=GRID_COLOR, linewidth=0.8, zorder=0)
    axes.tick_params(colors=TEXT_COLOR)
    for side in ("top", "right"):
        axes.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        axes.spines[side].set_color(GRID_COLOR)
    axes.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.0, 1.0))

    figure.tight_layout()
    figure.savefig(GRAPH_FILE, dpi=150)
    plt.close(figure)


def main():
    if not os.path.exists(RECORD_FILE):
        print("안내: " + RECORD_FILE + " 파일이 없습니다.", file=sys.stderr)
        print("먼저 uv run record_forecast.py 로 예보를 기록해 주세요.", file=sys.stderr)
        return 1

    try:
        records = load_records()
        days, max_temps, min_temps = read_points(records)
    except (ValueError, csv.Error) as error:
        print("오류: " + RECORD_FILE + " 파일을 읽을 수 없습니다. " + str(error), file=sys.stderr)
        return 1
    except OSError as error:
        print("오류: " + RECORD_FILE + " 파일을 열 수 없습니다. " + str(error), file=sys.stderr)
        return 1

    if not days:
        print("안내: " + RECORD_FILE + " 파일에 기록이 없어서 그래프를 그리지 않았습니다.", file=sys.stderr)
        return 1

    font_name = find_korean_font()
    if font_name is None:
        print("주의: 한글 글꼴을 찾지 못했습니다. 그래프의 한글이 네모로 보일 수 있습니다.", file=sys.stderr)
    else:
        plt.rcParams["font.family"] = font_name
    plt.rcParams["axes.unicode_minus"] = False  # 영하 기온의 빼기 기호가 깨지지 않게

    try:
        draw_graph(days, max_temps, min_temps)
    except OSError as error:
        print("오류: " + GRAPH_FILE + " 파일에 저장하지 못했습니다. " + str(error), file=sys.stderr)
        return 1

    print("기록 " + str(len(days)) + "건으로 그래프를 그렸습니다.")
    print("저장한 파일: " + GRAPH_FILE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
