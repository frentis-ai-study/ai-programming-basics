# AI프로그래밍기초 — 실습 소스코드

이번 과정의 **실행 가능한 예제 코드와 입력·시험 자료**를 주차별로 모읍니다. 교재 원고·슬라이드·고객 제출 PDF는 이 저장소에 자동으로 포함되지 않습니다. 현재 저장소는 비공개이며, 수강생 배포용 공개 전환은 별도 결정입니다.

## 주차별 예제

- [W12 · 날짜별 기온 기록](examples/W12-weather-collector/README.md) — 보관 CSV를 재구성한 고정 JSON 입력과 현재 날씨 API 입력을 구별하고, 날짜별 CSV·PNG를 생성·검증합니다. Python 표준 `unittest` 5건과 요청문 연습 자료를 포함합니다. **실행·시험을 마친 W12 교재 검토용 코드**로, 최종 강의 교재나 AI가 작성했다는 증거는 아닙니다.
- 다른 주차 예제: 검증 후 차례대로 추가합니다. 비어 있는 주차의 코드를 이미 올린 것처럼 표시하지 않습니다.

## W12 빠른 실행

Python 3.9 이상과 `uv`를 사용할 수 있다면:

```bash
cd examples/W12-weather-collector
uv run --python 3.9 --no-project --with requests --with matplotlib python weather.py \
  --fixture fixtures/weather-daily-example.json --output-dir output/demo
uv run --python 3.9 --no-project --with requests --with matplotlib python -m unittest discover -s tests -v
```

기존 CSV 값·출력 파일·현재 API 요청·실패 시험의 차이는 [W12 실행 안내](examples/W12-weather-collector/README.md)에 있습니다. `output/`은 실행할 때 다시 만드는 파일이므로 Git에 올리지 않습니다. 소스·테스트·입력 데이터를 먼저 검증하고 필요할 때만 강의 화면을 만듭니다.
