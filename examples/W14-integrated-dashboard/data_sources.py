"""화면 변경·파일 저장 없이 날씨와 검증된 W13 보관 CSV를 읽는다."""

import csv
import hashlib
import io
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


CITIES = {"서울": (37.57, 126.98), "부산": (35.18, 129.08), "제주": (33.50, 126.53)}

KST = timezone(timedelta(hours=9), name="Asia/Seoul")
API_URL = "https://api.open-meteo.com/v1/forecast"


class DataSourceError(Exception):
    """사용자에게 안내할 수 있는 자료 읽기 오류."""


def normalize_city(text):
    """양끝 공백만 제거하고 지원하는 한글 도시 이름을 확인한다."""
    if not isinstance(text, str) or not text.strip():
        raise DataSourceError("도시를 입력해 주세요. 서울·부산·제주를 지원합니다.")
    city = text.strip()
    if city not in CITIES:
        raise DataSourceError("서울·부산·제주만 지원합니다. 한글 도시 이름을 입력해 주세요.")
    return city


def _reject_json_constant(value):
    raise ValueError(f"허용하지 않는 JSON 숫자: {value}")


def _is_finite_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except (OverflowError, ValueError):
        return False


def _validate_weather(payload, city, today):
    if not isinstance(payload, dict):
        raise DataSourceError("날씨 응답은 JSON 객체여야 합니다.")

    if "error" in payload and payload["error"] is not False:
        raise DataSourceError("날씨 제공처가 오류 응답을 반환했습니다.")

    if payload.get("timezone") != "Asia/Seoul":
        raise DataSourceError("날씨 응답의 시간대가 Asia/Seoul이 아닙니다.")

    offset = payload.get("utc_offset_seconds")
    if not _is_finite_number(offset) or offset != 32400:
        raise DataSourceError("날씨 응답의 UTC 시차가 한국 표준시와 다릅니다.")

    units = payload.get("daily_units")
    if (
        not isinstance(units, dict)
        or units.get("time") != "iso8601"
        or units.get("temperature_2m_max") != "°C"
        or units.get("temperature_2m_min") != "°C"
    ):
        raise DataSourceError("날씨 응답의 날짜 형식 또는 섭씨 기온 단위가 잘못됐습니다.")

    daily = payload.get("daily")
    if not isinstance(daily, dict):
        raise DataSourceError("날씨 응답에 일별 자료가 없습니다.")

    dates = daily.get("time")
    maxima = daily.get("temperature_2m_max")
    minima = daily.get("temperature_2m_min")

    if not all(isinstance(values, list) for values in (dates, maxima, minima)):
        raise DataSourceError("날짜·최고기온·최저기온 자료가 배열이 아닙니다.")
    if not (len(dates) == len(maxima) == len(minima) == 8):
        raise DataSourceError("날짜·최고기온·최저기온이 각각 8개씩 있어야 합니다.")

    expected_dates = [
        (today - timedelta(days=days_ago)).isoformat()
        for days_ago in range(7, -1, -1)
    ]
    if dates != expected_dates:
        raise DataSourceError(
            "날짜가 요청 시점의 한국 날짜를 기준으로 지난 7일부터 오늘까지 "
            "빠짐없이 오름차순으로 들어 있어야 합니다."
        )

    rows = []
    for date, maximum, minimum in zip(dates, maxima, minima):
        if not _is_finite_number(maximum) or not _is_finite_number(minimum):
            raise DataSourceError(
                f"{date}의 기온이 유효하지 않습니다. "
                "누락값·참/거짓·무한대가 아닌 유한한 숫자가 필요합니다."
            )
        if maximum < minimum:
            raise DataSourceError(f"{date}의 최고기온이 최저기온보다 낮습니다.")
        rows.append(
            {
                "city": city,
                "date": date,
                "max_temp": maximum,
                "min_temp": minimum,
                "unit": "°C",
            }
        )
    return rows


def fetch_weather(city):
    """지난 7일의 보관 예보와 오늘 예보를 모두 검증한 뒤 반환한다."""
    city = normalize_city(city)
    latitude, longitude = CITIES[city]
    request_url = API_URL + "?" + urlencode(
        {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min",
            "past_days": 7,
            "forecast_days": 1,
            "timezone": "Asia/Seoul",
            "temperature_unit": "celsius",
        }
    )
    request_date = datetime.now(KST).date()

    try:
        with urlopen(request_url, timeout=15) as response:
            http_status = response.status
            if isinstance(http_status, bool) or http_status != 200:
                raise DataSourceError(
                    f"날씨 요청이 정상 처리되지 않았습니다. HTTP 상태: {http_status}"
                )
            response_url = response.geturl()
            raw_bytes = response.read()
            retrieved_at = datetime.now(KST).isoformat()
    except HTTPError as exc:
        raise DataSourceError(
            f"날씨 제공처가 HTTP {exc.code} 오류를 반환했습니다."
        ) from exc
    except (URLError, OSError) as exc:
        raise DataSourceError(
            "날씨 자료를 가져오지 못했습니다. 인터넷 연결이나 응답 시간을 확인해 주세요."
        ) from exc
    except Exception as exc:
        if isinstance(exc, DataSourceError):
            raise
        raise DataSourceError("날씨 응답을 읽는 중 통신 오류가 발생했습니다.") from exc

    if not isinstance(raw_bytes, bytes):
        raise DataSourceError("날씨 응답 원문이 바이트 자료가 아닙니다.")
    if not isinstance(response_url, str) or not response_url:
        raise DataSourceError("날씨 응답의 URL을 확인할 수 없습니다.")

    try:
        payload = json.loads(
            raw_bytes.decode("utf-8"),
            parse_constant=_reject_json_constant,
        )
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise DataSourceError("날씨 응답을 올바른 UTF-8 JSON으로 읽을 수 없습니다.") from exc

    rows = _validate_weather(payload, city, request_date)
    return {
        "rows": rows,
        "city": city,
        "timezone": "Asia/Seoul",
        "source": "Open-Meteo Forecast API",
        "data_kind": (
            "지난 7일의 보관 예보(archived forecasts)와 오늘의 예보 자료이며, "
            "기상 관측소의 관측값이 아닙니다."
        ),
        "request_url": request_url,
        "response_url": response_url,
        "http_status": http_status,
        "retrieved_at": retrieved_at,
        "raw_bytes": raw_bytes,
        "raw_sha256": hashlib.sha256(raw_bytes).hexdigest(),
    }


def read_archived_memo(path):
    """호출자가 선택한 W13 검증 보관 CSV를 재집계 없이 전체 읽는다."""
    try:
        file_path = Path(path)
    except (TypeError, ValueError, OSError) as exc:
        raise DataSourceError("읽을 W13 보관 CSV의 파일 경로를 확인해 주세요.") from exc

    try:
        raw_bytes = file_path.read_bytes()
    except FileNotFoundError as exc:
        raise DataSourceError(f"보관 CSV 파일이 없습니다: {file_path}") from exc
    except IsADirectoryError as exc:
        raise DataSourceError(f"폴더가 아닌 CSV 파일을 선택해 주세요: {file_path}") from exc
    except (OSError, ValueError) as exc:
        raise DataSourceError(
            f"보관 CSV 파일을 읽을 수 없습니다. 경로와 읽기 권한을 확인해 주세요: {file_path}"
        ) from exc

    try:
        decoded = raw_bytes.decode("utf-8-sig")
    except UnicodeError as exc:
        raise DataSourceError("보관 CSV는 UTF-8 또는 UTF-8 BOM 인코딩이어야 합니다.") from exc

    rows = []
    seen_words = set()
    previous_key = None

    try:
        with io.StringIO(decoded, newline="") as stream:
            reader = csv.DictReader(stream, strict=True)
            if reader.fieldnames != ["word", "count"]:
                raise DataSourceError(
                    "CSV 열 이름과 순서는 정확히 word,count여야 합니다."
                )

            for record in reader:
                location = f"CSV {reader.line_num}행"
                if set(record) != {"word", "count"}:
                    raise DataSourceError(f"{location}에 불필요한 열이 있습니다.")
                if record["word"] is None or record["count"] is None:
                    raise DataSourceError(f"{location}에 빠진 셀이 있습니다.")

                word = record["word"]
                count_text = record["count"]
                if not word.strip():
                    raise DataSourceError(f"{location}의 word가 비어 있습니다.")
                if not count_text or any(
                    character < "0" or character > "9" for character in count_text
                ):
                    raise DataSourceError(
                        f"{location}의 count는 공백 없이 ASCII 숫자 0~9로 적은 "
                        "양의 정수여야 합니다."
                    )

                try:
                    count = int(count_text)
                except ValueError as exc:
                    raise DataSourceError(
                        f"{location}의 count를 정수로 읽을 수 없습니다."
                    ) from exc
                if count <= 0:
                    raise DataSourceError(f"{location}의 count는 1 이상이어야 합니다.")
                if word in seen_words:
                    raise DataSourceError(f"{location}에 중복된 word가 있습니다: {word}")

                current_key = (-count, word)
                if previous_key is not None and current_key < previous_key:
                    raise DataSourceError(
                        f"{location}의 정렬 순서가 잘못됐습니다. "
                        "count 내림차순, 같은 count에서는 word 오름차순이어야 합니다."
                    )

                rows.append({"word": word, "count": count})
                seen_words.add(word)
                previous_key = current_key
    except csv.Error as exc:
        raise DataSourceError("CSV 형식이 잘못됐습니다. 구분자와 따옴표를 확인해 주세요.") from exc

    if not rows:
        raise DataSourceError("보관 CSV에 데이터 행이 하나 이상 있어야 합니다.")

    return {
        "rows": rows,
        "row_count": len(rows),
        "count_sum": sum(row["count"] for row in rows),
        "path": str(file_path),
        "sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "provenance": (
            "호출자가 W13에서 검증해 저장한 교육용 출력으로 지정한 보관 CSV입니다. "
            "이 함수는 파일 형식·값·중복·정렬을 검사하고 모든 행과 순서를 보존하며, "
            "새 메모를 수집하거나 단어별 횟수를 다시 집계하지 않습니다. "
            "W13 원본의 선택과 검증 이력은 호출자가 별도로 확인합니다."
        ),
        "loaded_at": datetime.now(KST).isoformat(),
    }
