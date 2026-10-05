# W12 · 현재 교안의 단계별 AI 생성 예제

부모 폴더의 `weather.py`와 작은 `lookup_today.py`는 기존 검증/연습 코드로 보존했습니다. **현재 교안의 생성 단계와 연결된 파일은 이 `ai-stages/` 폴더**에 있습니다. 모든 Python 원문은 기존 생성본을 수정 없이 복사했습니다.

## 준비와 실행

이 폴더에서 실행합니다. 조회·기록·읽기는 표준 라이브러리만 사용하고, 그림은 Matplotlib이 필요합니다.

```bash
python3 lookup_today.py
python3 record_forecast.py
python3 record_forecast_read.py --show-records
uv run --with matplotlib python plot_forecast.py
```

조회·기록은 인터넷의 Open-Meteo 예보를 요청합니다. 현재 예보 수치는 실행 날짜에 따라 달라지며 고정 정답이 아닙니다. `--show-records`와 `plot_forecast.py`는 기존 `forecast_records.csv`만 읽습니다.

## 개선 단계

```bash
python3 record_forecast_checked.py
# 추가 CSV 검증 보완까지 적용한 최종 기록 프로그램
python3 forecast_collector_checked.py && uv run --with matplotlib python plot_forecast.py
```

- `record_forecast.py`: 초기 조회·기록 단계. 응답 시간대 확인 등 후속 보완을 적용한 버전이 아닙니다.
- `record_forecast_read.py --show-records`: 파일 읽기 전용 모드. 이 파일의 기본 실행은 초기 조회·기록 기능입니다.
- `record_forecast_checked.py`: 응답 시간대를 확인하는 수정 단계.
- `forecast_collector_checked.py`: 기존 CSV 날짜·기온 검사까지 보완한 최종 조회·기록 단계.
- `plot_forecast.py`: CSV의 날짜별 최고·최저를 **점만 있는 산점도**로 저장합니다.

CSV는 현재 실행 폴더에 `date,max,min` 열로 저장됩니다. 결과 PNG도 같은 실행 폴더에 생성됩니다. 그래프는 macOS AppleGothic을 사용합니다. Windows/Linux에서는 설치된 한글 폰트로 바꾸는 추가 작업이 필요합니다.

기록 실패 때 `&&`로 연결한 그림은 실행되지 않습니다. 다만 기록이 성공한 뒤 그림 자체가 실패하면 CSV는 이미 저장된 상태일 수 있습니다. 두 파일의 원자적 저장을 보장하는 예제가 아닙니다.

**과거 날짜 중복의 한계:** 최종 기록 프로그램은 오늘 날짜의 행은 갱신하지만, 기존 CSV에 있던 과거 날짜의 중복 행까지 제거하거나 거절하지는 않습니다. 반면 그림 프로그램은 같은 날짜가 두 번 있으면 오류로 멈춥니다. 따라서 기록 성공이 그림 성공까지 뜻하지 않습니다. 이런 경우 CSV를 별도 사본으로 보관한 뒤 중복을 확인하고, 원본을 보존하는 중복 처리 개선을 AI에 추가 요청하세요. 이번 패키지에서는 기존 생성 코드 원문을 바꾸지 않았습니다.

`requests/`는 학생용 짧은 요청문이며 실제 생성 때는 기존 코드·강사 조건 등 추가 문맥을 함께 사용했습니다. 전체 요청·AI 응답·원시 로그·강사용 시험 도구는 로컬 제작 자료로 별도 보관했습니다. 새로 생성하거나 과거 시험을 이번 실행으로 바꿔 표시하지 않습니다.
