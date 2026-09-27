"""W12 예제: 날짜별 기온을 CSV와 PNG로 저장합니다.

기본 실습은 보관 CSV로 재구성한 JSON 입력을 사용하여 인터넷 없이 재현합니다.
--live는 현재 API를 호출하므로 보관된 2026-08 자료와 값이 다릅니다.
"""

import argparse
import csv
import io
import json
import math
import sys
from datetime import date
from pathlib import Path
from typing import List, Tuple

API_URL = "https://api.open-meteo.com/v1/forecast"
CONDITIONS = {
    "latitude": 37.57,
    "longitude": 126.98,
    "daily": "temperature_2m_max,temperature_2m_min",
    "past_days": 7,
    "forecast_days": 1,
    "timezone": "Asia/Seoul",
}
Record = Tuple[str, float, float]


def parse_daily(payload: dict) -> List[Record]:
    """JSON의 같은 위치에 있는 날짜·최고·최저기온을 한 행으로 묶습니다."""
    try:
        daily = payload["daily"]
        dates = daily["time"]
        highs = daily["temperature_2m_max"]
        lows = daily["temperature_2m_min"]
    except (KeyError, TypeError) as error:
        raise ValueError("daily의 날짜와 최고·최저기온 배열이 필요합니다") from error

    if not all(isinstance(values, list) for values in (dates, highs, lows)):
        raise ValueError("날짜와 기온 값은 배열이어야 합니다")
    if not dates or len(dates) != len(highs) or len(dates) != len(lows):
        raise ValueError("날짜와 두 기온 배열의 길이가 같아야 합니다")

    rows = []
    for day, high, low in zip(dates, highs, lows):
        try:
            date.fromisoformat(day)
        except (TypeError, ValueError) as error:
            raise ValueError("날짜는 YYYY-MM-DD 형식이어야 합니다") from error
        if any(earlier == day for earlier, _, _ in rows):
            raise ValueError("중복된 날짜가 있습니다: {}".format(day))
        if (not isinstance(high, (int, float)) or isinstance(high, bool)
                or not isinstance(low, (int, float)) or isinstance(low, bool)):
            raise ValueError("최고·최저기온은 숫자여야 합니다")
        try:
            high_value, low_value = float(high), float(low)
        except (OverflowError, ValueError) as error:
            raise ValueError("최고·최저기온은 유한한 숫자여야 합니다") from error
        if not math.isfinite(high_value) or not math.isfinite(low_value):
            raise ValueError("최고·최저기온은 유한한 숫자여야 합니다")
        if high_value < low_value:
            raise ValueError("최고기온은 최저기온보다 낮을 수 없습니다")
        rows.append((day, high_value, low_value))
    return rows


def csv_content(rows: List[Record]) -> bytes:
    text = io.StringIO(newline="")
    writer = csv.writer(text)
    writer.writerow(["date", "max_temp", "min_temp"])
    writer.writerows(rows)
    return text.getvalue().encode("utf-8")


def png_content(rows: List[Record], fixture: bool) -> bytes:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    korean_font = None
    for name in ("Apple SD Gothic Neo", "NanumGothic", "Malgun Gothic"):
        try:
            font_manager.findfont(name, fallback_to_default=False)
        except ValueError:
            continue
        korean_font = name
        break
    if korean_font:
        plt.rcParams["font.family"] = korean_font
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=140)
    days = [day[5:] for day, _, _ in rows]
    ax.plot(days, [high for _, high, _ in rows], marker="o", label="최고기온" if korean_font else "High")
    ax.plot(days, [low for _, _, low in rows], marker="o", label="최저기온" if korean_font else "Low")
    ax.set_ylabel("기온(°C)" if korean_font else "Temperature (°C)")
    ax.grid(axis="y", alpha=0.3)
    ax.legend()
    if fixture:
        ax.set_title("보관 CSV를 재구성한 예제 입력" if korean_font else "Reconstructed archived CSV")
    else:
        ax.set_title("이번 실행의 API 응답" if korean_font else "Current API response")
    fig.tight_layout()
    image = io.BytesIO()
    try:
        fig.savefig(image, format="png")
        return image.getvalue()
    finally:
        plt.close(fig)


def fetch_live(endpoint: str) -> dict:
    import requests
    try:
        response = requests.get(endpoint, params=CONDITIONS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        raise RuntimeError("날씨 정보를 받지 못했습니다: {}".format(error)) from error


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="보관 예제 또는 현재 API 응답으로 날씨 기록 만들기")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--fixture", type=Path, help="보관 CSV에서 재구성한 JSON 예제 입력")
    source.add_argument("--live", action="store_true", help="현재 API에 직접 요청 (인터넷 필요)")
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--endpoint", default=API_URL, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    try:
        if args.fixture:
            payload = json.loads(args.fixture.read_text(encoding="utf-8"))
        else:
            payload = fetch_live(args.endpoint)
        rows = parse_daily(payload)
        table = csv_content(rows)
        graph = png_content(rows, fixture=bool(args.fixture))
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "weather.csv").write_bytes(table)
        (args.output_dir / "weather.png").write_bytes(graph)
    except (OSError, ValueError, RuntimeError) as error:
        print("오류: {}".format(error), file=sys.stderr)
        return 1

    kind = "보관 예제 입력" if args.fixture else "현재 API 응답"
    print("{}: {}일치 기온을 {}에 저장했습니다.".format(kind, len(rows), args.output_dir / "weather.csv"))
    print("그래프를 {}에 저장했습니다.".format(args.output_dir / "weather.png"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
