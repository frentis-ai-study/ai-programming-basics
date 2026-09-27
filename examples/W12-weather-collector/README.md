# W12 날씨 기록 — 교재 재구성용 실행 예제 v3

**기존 `W12-날씨수집기`는 보존합니다.** 이 폴더는 강의 내용을 확정하기 전에 코드를 실제로 실행하고, 화면에서 보여 줄 값과 확인 방법을 고르기 위한 별도 예제입니다. `fixtures/weather-archived.csv`는 기존 출력 CSV의 바이트 동일 사본으로, 이 폴더만 내려받아도 입력 출처를 대조할 수 있습니다. AI가 작성한 코드나 기존의 실제 API 응답 원본이라고 주장하지 않습니다.

## 입력의 출처

- `fixtures/weather-daily-example.json`은 `fixtures/weather-archived.csv`(기존 `W12-날씨수집기/출력/weather.csv`의 사본)의 **2026-08-07~14, 날짜 8개·기온 16개 값**을 `daily` 배열 형태로 옮긴 교육용 입력입니다. 원본 JSON 응답은 보관되지 않았습니다. 따라서 이 입력으로 실행해도 **과거 실제 API 응답을 다시 받은 것은 아닙니다.**
- `weather.py --live`는 별도로 현재 Open-Meteo API를 호출합니다. 실행한 날짜에 따라 결과가 달라지며, 네트워크가 필요합니다. 기존 CSV 날짜·값이 그대로 나올 것을 기대하지 마세요.

## 설치와 실행

Python 3.9 이상, `requests`와 `matplotlib`가 필요합니다. 먼저 이 폴더로 이동합니다.

실행 결과인 `output/`은 저장소에 포함하지 않습니다. 아래 명령으로 각자 다시 생성합니다.

```bash
# uv가 있는 환경: 별도 가상환경의 필요한 패키지로 실행
uv run --python 3.9 --no-project --with requests --with matplotlib python weather.py \
  --fixture fixtures/weather-daily-example.json --output-dir output/demo

# 이미 두 패키지가 설치된 환경이라면 동일한 실행
python3 weather.py --fixture fixtures/weather-daily-example.json --output-dir output/demo
```

**확인할 것:** `output/demo/weather.csv`의 머리글은 `date,max_temp,min_temp`이며 8개 날짜 행이 있습니다. 첫 행은 `2026-08-07,35.7,24.8`, 마지막 행은 `2026-08-14,27.8,22.3`입니다. `output/demo/weather.png`에는 날짜에 따른 최고·최저기온 변화가 나타납니다. 그래프 제목에 보관 CSV 재구성 입력이라고 명시합니다. 실행 안내만 읽고 끝내지 말고 두 파일을 열어 보세요.

현재 데이터를 조회하고 싶을 때만 다음을 사용합니다. 이전 결과와 혼동하지 않게 출력 폴더를 나눕니다. **2026-09-28 현장 검증에서는 API 정상 응답으로 `output/live/`에 8행 CSV와 PNG를 생성했습니다.** 이후 다시 실행할 때에는 날짜·값이 달라질 수 있습니다.

```bash
python3 weather.py --live --output-dir output/live
```

## 실패 시험과 주의할 점

```bash
python3 -m unittest discover -s tests -v
```

자동 시험 5건은 ① 보관 CSV와 교육용 JSON의 모든 날짜·값 일치, ② 보관 입력→CSV 전 행 일치와 PNG 생성·크기 검사, ③ NaN·무한대 기온의 거부와 결과 파일 미생성, ④ 중복 날짜의 거부와 결과 파일 미생성, ⑤ **로컬에서 만든 HTTP 503 응답**에서 종료 코드 1·오류 안내·기존 결과 파일 불변을 확인합니다. PNG의 날짜·범례 내용은 자동 시험이 아니라 생성된 이미지를 열어 별도로 확인합니다. ⑤는 실제 외부 API 장애의 관찰 결과가 아니라 **통제된 실패 재현**입니다. 외부 API **정상 응답**은 별도 실습 명령으로 한 차례 확인했지만 외부 API **실제 장애**는 관찰하지 않았습니다. 기존 출력 파일이 남아 있다면 실패 후에도 보일 수 있으니 파일 존재만으로 **이번 실행 성공**을 판단하지 마세요.

코드는 입력을 먼저 읽고 배열 길이·날짜·값을 확인한 뒤 CSV와 그래프를 만들어 저장합니다. API 응답 대기 제한은 10초입니다. 재요청·자동 복구·데이터 갱신 주기 등은 이 예제의 범위 밖입니다.

## 교재와 연결할 순서

1. **섹션 1 — 입력·출력·판정 기준:** 보관된 날짜별 CSV 두 행을 읽고, `fixtures/weather-daily-example.json`의 같은 위치 세 값을 한 행으로 묶어 보는 실습. `weather.py`의 `CONDITIONS`, `parse_daily`, `csv_content`, `png_content`에 각각 연결합니다. **fixture 실행과 실제 API 요청을 분리해서** 설명합니다.
2. **섹션 2 — AI 요청문:** `teaching-request-based-on-tested-code.md`에서 작동하는 코드를 거꾸로 분석해 대상·기간·필드·CSV/PNG·10초 제한·오류 안내를 확인 항목으로 씁니다. 기존 요청문과 비교하되 **이 새 코드가 이 연습용 요청문으로 자동 생성됐다고 말하지 않습니다.**
3. **섹션 3 — 실행·검증:** 오프라인 fixture를 실제로 실행하고 CSV 8행·그래프·출력 문구를 대조합니다. 별도로 한 차례 성공한 실제 API 요청, 로컬 HTTP 503 시험, **실측하지 않은 외부 장애**를 명확히 나눕니다. 섹션별 표지는 만들지 않고 **주차 표지 한 장과 섹션 간지 세 장**만 둡니다.

학생용 교재와 강사용 말하기 메모는 이 코드를 바탕으로 별도 검토합니다. 이 폴더가 생겼다는 사실만으로 기존 60쪽 PDF가 강의 가능해진 것은 아닙니다.
