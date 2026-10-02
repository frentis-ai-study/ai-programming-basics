"""app_dashboard.py — 동결된 stage2 모듈 data_sources.py를 가져와 연결한다."""

import csv
import hashlib
import io
import json
import os
import tempfile
from datetime import date
from pathlib import Path

import streamlit as st

import data_sources as ds


APP_ROOT = Path(__file__).resolve().parent
FIXTURE_ROOT = Path(
    "/Users/andy/.hermes/cache/scratch/sjcu-w14-lo-integration-v2"
).resolve()
WEATHER_COLUMNS = ["city", "date", "max_temp", "min_temp", "unit"]


def _is_under(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _approved_path(value) -> Path:
    """환경변수 경로를 실제 경로로 해석하고 허용된 영역을 확인한다."""
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = APP_ROOT / path
    path = path.resolve()
    if not any(_is_under(path, root) for root in (APP_ROOT, FIXTURE_ROOT)):
        raise ds.DataSourceError(
            "설정 경로는 앱 폴더 또는 승인된 교사용 실습 폴더 안이어야 합니다."
        )
    return path


def _configured_path(name: str, default: Path) -> Path:
    value = os.environ.get(name)
    if value is not None and not value.strip():
        raise ds.DataSourceError(f"{name} 설정이 비어 있습니다.")
    return _approved_path(default if value is None else value)


def _output_child(output_dir: Path, *parts: str) -> Path:
    path = output_dir.joinpath(*parts)
    if not _is_under(path.resolve(), output_dir):
        raise ds.DataSourceError("출력 파일의 실제 경로가 출력 폴더를 벗어납니다.")
    return path


def _validate_for_save(result) -> None:
    """동결된 검증기를 재사용하여 원문과 저장할 행의 일치를 확인한다."""
    try:
        rows = result["rows"]
        raw = result["raw_bytes"]
        if not isinstance(rows, list) or len(rows) != 8:
            raise ds.DataSourceError("저장할 날씨 자료는 검증된 전체 8행이어야 합니다.")
        if not isinstance(raw, bytes):
            raise ds.DataSourceError("실제 날씨 응답 원문이 없습니다.")
        if hashlib.sha256(raw).hexdigest() != result["raw_sha256"]:
            raise ds.DataSourceError("날씨 응답 원문의 SHA-256이 일치하지 않습니다.")
        if any(
            not isinstance(row, dict) or set(row) != set(WEATHER_COLUMNS)
            for row in rows
        ):
            raise ds.DataSourceError("날씨 저장 열이 올바르지 않습니다.")

        city = ds.normalize_city(result["city"])
        payload = json.loads(
            raw.decode("utf-8"),
            parse_constant=ds._reject_json_constant,
        )
        # 요청 날짜 검증은 fetch_weather에서 이미 수행했다.
        # 여기서는 같은 원문을 기존 검증기로 확인하여 저장 행과 대조한다.
        validated_rows = ds._validate_weather(
            payload, city, date.fromisoformat(rows[-1]["date"])
        )
        if rows != validated_rows:
            raise ds.DataSourceError("날씨 원문과 저장할 전체 행이 일치하지 않습니다.")
        if result["timezone"] != "Asia/Seoul":
            raise ds.DataSourceError("날씨 시간대가 올바르지 않습니다.")
        status = result["http_status"]
        if isinstance(status, bool) or status != 200:
            raise ds.DataSourceError("정상 HTTP 응답만 저장할 수 있습니다.")
        for key in (
            "source",
            "data_kind",
            "request_url",
            "response_url",
            "retrieved_at",
        ):
            if not isinstance(result[key], str) or not result[key].strip():
                raise ds.DataSourceError(f"날씨 출처 정보가 없습니다: {key}")
    except ds.DataSourceError:
        raise
    except (KeyError, TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ds.DataSourceError(
            "날씨 원문·전체 행·출처 정보를 저장 전에 확인하지 못했습니다."
        ) from exc


def summarize_weather(result) -> str:
    """검증된 전체 8행의 날짜 범위와 최고·최저 값을 요약한다."""
    rows = result["rows"]
    highest = max(row["max_temp"] for row in rows)
    lowest = min(row["min_temp"] for row in rows)
    return (
        f"{result['city']} · {rows[0]['date']} ~ {rows[-1]['date']} "
        f"전체 {len(rows)}일 자료: "
        f"기간 중 최고기온 최댓값 {highest:g} °C, "
        f"최저기온 최솟값 {lowest:g} °C."
    )


def _write_evidence(path: Path, content: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def save_weather_csv(result, output_dir) -> Path:
    """증거 파일을 먼저 저장하고, 완성된 CSV를 마지막에 원자 교체한다."""
    temporary_path = None
    try:
        _validate_for_save(result)
        output_dir = _approved_path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        saved_path = _output_child(output_dir, "weather.csv")
        evidence_root = _output_child(output_dir, "evidence")
        evidence_root.mkdir(parents=True, exist_ok=True)

        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=WEATHER_COLUMNS)
        writer.writeheader()
        writer.writerows(result["rows"])
        csv_bytes = buffer.getvalue().encode("utf-8-sig")

        # 매 성공 시도마다 별도 폴더를 사용한다. 실패한 증거는 진단용으로 남는다.
        run_dir = Path(
            tempfile.mkdtemp(prefix="weather-", dir=str(evidence_root))
        )
        metadata = {
            key: value for key, value in result.items() if key != "raw_bytes"
        }
        metadata.update(
            {
                "saved_path": str(saved_path),
                "evidence_directory": str(run_dir),
                "csv_sha256": hashlib.sha256(csv_bytes).hexdigest(),
                "evidence_note": (
                    "교체 전 저장한 응답 증거입니다. 이 파일의 존재만으로 "
                    "weather.csv 교체 성공을 뜻하지 않습니다."
                ),
            }
        )
        metadata_bytes = json.dumps(
            metadata, ensure_ascii=False, indent=2, allow_nan=False
        ).encode("utf-8")

        _write_evidence(run_dir / "raw_response.bin", result["raw_bytes"])
        _write_evidence(run_dir / "metadata.json", metadata_bytes)
        _write_evidence(run_dir / "weather.csv", csv_bytes)

        # 최종 CSV와 같은 디렉터리에 임시 파일을 만든다.
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=".weather-",
            suffix=".tmp",
            dir=str(output_dir),
            delete=False,
        ) as stream:
            temporary_path = Path(stream.name)
            stream.write(csv_bytes)
            stream.flush()
            os.fsync(stream.fileno())

        # 증거와 전체 CSV 준비가 끝난 뒤 마지막 파일 작업으로 교체한다.
        os.replace(temporary_path, saved_path)
        temporary_path = None
        return saved_path
    except ds.DataSourceError:
        raise
    except OSError:
        raise
    except (csv.Error, TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ds.DataSourceError(
            "날씨 CSV 또는 증거 파일을 구성하지 못했습니다. "
            "기존 weather.csv는 교체하지 않았습니다."
        ) from exc
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass


def _clear_weather() -> None:
    st.session_state["weather_result"] = None
    st.session_state["weather_saved_path"] = None
    st.session_state["weather_notice"] = None


def _print_event(event: dict) -> None:
    print(
        json.dumps(event, ensure_ascii=False, allow_nan=False),
        flush=True,
    )


def _handle_weather(city_text: str) -> None:
    _clear_weather()
    if not city_text.strip():
        st.session_state["weather_notice"] = (
            "info",
            "도시를 입력해 주세요. 서울·부산·제주를 지원합니다.",
        )
        return

    try:
        city = ds.normalize_city(city_text)
        output_dir = _configured_path("W14_OUTPUT_DIR", APP_ROOT / "output")
        result = ds.fetch_weather(city)
        saved_path = save_weather_csv(result, output_dir)
        summary = summarize_weather(result)
        _print_event(
            {
                "event": "weather_success",
                "rows": result["rows"],
                "summary": summary,
                "request_url": result["request_url"],
                "retrieved_at": result["retrieved_at"],
                "saved_path": str(saved_path),
                "raw_sha256": result["raw_sha256"],
            }
        )
    except ds.DataSourceError as exc:
        st.session_state["weather_notice"] = ("error", str(exc))
    except OSError as exc:
        st.session_state["weather_notice"] = (
            "error",
            "날씨 처리 중 파일 저장 또는 터미널 기록에 실패했습니다. "
            "출력 폴더의 권한·여유 공간과 실행 터미널을 확인한 뒤 "
            f"다시 눌러 주세요. 이번 결과는 성공으로 표시하지 않습니다. ({exc})",
        )
    else:
        st.session_state["weather_result"] = result
        st.session_state["weather_saved_path"] = str(saved_path)


def _handle_memo() -> None:
    st.session_state["memo_result"] = None
    st.session_state["memo_notice"] = None
    try:
        memo_path = _configured_path(
            "W14_MEMO_PATH", APP_ROOT / "data" / "keywords.csv"
        )
        result = ds.read_archived_memo(memo_path)
        _print_event(
            {
                "event": "memo_success",
                "rows": result["rows"],
                "row_count": result["row_count"],
                "count_sum": result["count_sum"],
                "sha256": result["sha256"],
                "loaded_at": result["loaded_at"],
            }
        )
    except ds.DataSourceError as exc:
        st.session_state["memo_notice"] = (
            f"{exc} W13에서 검증해 보관한 CSV와 실행 환경의 "
            "메모 경로 설정을 확인한 뒤 다시 눌러 주세요."
        )
    except OSError as exc:
        st.session_state["memo_notice"] = (
            "보관 메모 읽기 또는 터미널 기록에 실패했습니다. "
            f"파일 읽기 권한과 실행 터미널을 확인해 주세요. ({exc})"
        )
    else:
        st.session_state["memo_result"] = result


def _show_weather() -> None:
    notice = st.session_state["weather_notice"]
    if notice is not None:
        level, message = notice
        if level == "info":
            st.info(message)
        else:
            st.error(message)

    result = st.session_state["weather_result"]
    if result is None:
        return

    st.success("표시 중인 날씨 자료의 검증과 CSV 저장을 완료했습니다.")
    st.write(summarize_weather(result))
    st.caption(
        f"source: {result['source']} | data_kind: {result['data_kind']} | "
        f"timezone: {result['timezone']} | "
        f"retrieved_at: {result['retrieved_at']}"
    )
    st.caption(
        f"저장 경로: {st.session_state['weather_saved_path']} | "
        f"응답 SHA-256: {result['raw_sha256']}"
    )
    rows = result["rows"]
    st.dataframe(rows, hide_index=True)
    st.caption(
        "기온 단위: °C(섭씨). max_temp는 날짜별 최고기온, "
        "min_temp는 날짜별 최저기온입니다. 그래프는 예보 자료의 날짜별 값을 보여 줍니다."
    )
    st.line_chart(rows, x="date", y=["max_temp", "min_temp"])


def _show_memo() -> None:
    notice = st.session_state["memo_notice"]
    if notice is not None:
        st.error(notice)

    result = st.session_state["memo_result"]
    if result is None:
        return

    st.success("검증된 W13 보관 CSV의 전체 행을 읽었습니다.")
    st.metric("보관 CSV 행 수", result["row_count"])
    st.metric("보관 CSV 횟수 합계", result["count_sum"])
    st.caption(
        f"W13 교육용 보관 자료 | loaded_at: {result['loaded_at']} | "
        f"원본 CSV SHA-256: {result['sha256']}"
    )
    st.caption(result["provenance"])
    st.dataframe(result["rows"], hide_index=True)


def main() -> None:
    defaults = {
        "weather_result": None,
        "memo_result": None,
        "weather_saved_path": None,
        "weather_notice": None,
        "memo_notice": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    st.title("통합 대시보드")
    st.write("서울·부산·제주 중 도시를 입력한 뒤 확인 버튼을 눌러 주세요.")
    city = st.text_input(
        "도시",
        value="",
        key="city_input",
        on_change=_clear_weather,
    )
    if st.button("확인", key="weather_fetch"):
        _handle_weather(city)

    _show_weather()

    st.subheader("W13 보관 메모")
    if st.button("보관 메모 읽기", key="memo_read"):
        _handle_memo()

    _show_memo()


if __name__ == "__main__":
    main()
