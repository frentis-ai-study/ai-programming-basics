# W12 · 날씨 수집기

서울의 오늘 최고기온과 최저기온 예보를 조회하고, 파일에 기록하고, 기록을 다시 읽어 그래프로 그리는 예제입니다. 12주차 교안과 같은 예제입니다.

`requests/`의 요청문 네 개를 빈 폴더에서 Claude Code에 차례로 보내 만들었습니다(2026-10-07). 같은 요청문을 보내도 Claude Code가 만드는 코드는 달라질 수 있습니다. 이 폴더의 코드는 자신의 결과와 비교해 보는 견본이며 정답이 아닙니다.

## 파일

| 파일 | 만든 요청 | 하는 일 |
|---|---|---|
| `lookup_today.py` | `requests/1-lookup.txt` | 서울의 오늘 최고·최저기온 예보를 조회해 화면에 보여 줍니다 |
| `record_forecast.py` | `requests/2-record.txt` | 조회한 값을 `forecast_records.csv`에 저장합니다. 같은 날짜는 바꾸고 다른 날짜는 남깁니다 |
| `show_records.py` | `requests/3-read.txt` | 저장된 기록을 날짜순으로 보여 줍니다. 새로 조회하지 않습니다 |
| `plot_forecast.py` | `requests/4-plot.txt` | 저장된 기록을 점 그래프로 그려 `forecast_records.png`로 저장합니다 |
| `forecast_records.start.csv` | (실습 자료) | 지난 예보 기록 세 줄(9/29, 9/30, 10/1)이 든 시작 파일입니다. 프로그램이 모은 것이 아니라 실습용으로 준비한 것입니다 |
| `results/` | (실행 결과) | 시작 파일에서 출발해 2026-10-07에 실행한 뒤의 기록 파일과 그래프입니다 |

## 실행

이 폴더에서 실행합니다. 조회와 기록에는 인터넷 연결이 필요합니다.

```bash
cp forecast_records.start.csv forecast_records.csv   # 시작 기록을 넣어 둡니다 (Windows: copy)
uv run lookup_today.py
uv run record_forecast.py
uv run show_records.py
uv run plot_forecast.py
```

조회와 기록, 읽기는 파이썬 기본 기능만 씁니다. 그래프에는 matplotlib이 필요하며, `plot_forecast.py` 첫머리의 표시를 보고 uv가 준비합니다. 네 파일은 같은 폴더에 두어야 합니다. 뒤의 프로그램이 앞의 프로그램의 기능을 가져다 쓰기 때문입니다.

## 확인해 볼 것

- 화면의 날짜가 오늘인지, 기온 옆에 섭씨 단위가 있는지 확인합니다.
- 기록 프로그램을 실행한 뒤 `forecast_records.csv`를 열어 마지막 줄이 화면의 값과 같은지 확인합니다.
- 기록 프로그램을 한 번 더 실행해도 줄 수가 늘지 않는지 확인합니다.
- 인터넷 연결을 끊고 기록 프로그램을 실행하면 오류 안내가 나오고 기록 파일이 그대로인지 확인합니다.
- 그래프에서 기록이 없는 날짜가 비어 있는지 확인합니다.

## 알아 둘 점

기온은 Open-Meteo의 예보 값입니다(CC BY 4.0, 비상업적 용도 무료). 관측한 값이 아니며 조회하는 시점에 따라 달라집니다. 화면의 값이 `results/`의 값과 같을 필요는 없습니다. 그래프의 한글은 macOS에서 확인했습니다. 다른 운영체제에서는 한글 글꼴에 따라 다르게 보일 수 있습니다.
