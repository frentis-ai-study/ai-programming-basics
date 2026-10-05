# 서울 하루 예보 조회 · 1차시 작은 프로그램

기존 `weather.py`는 CSV와 그래프를 저장하는 **다음 단계 예제**입니다. 첫 차시에는 별도 `lookup_today.py`만 실행해 날짜·최고·최저기온 예보를 **화면에서 읽습니다**.

## 인터넷으로 서울 예보 조회

이 폴더에서 터미널을 열고 아래 명령을 실행합니다. 추가 파이썬 패키지는 필요하지 않습니다.

```bash
python3 lookup_today.py
```

화면에는 요청을 실행한 시점의 서울 기준 날짜, 최고기온, 최저기온 예보가 표시됩니다. 수업 자료에 나온 숫자는 2026-09-29 00:37 KST에 캡처한 **예시**입니다. 같은 수치가 나오는지를 채점 기준으로 삼지 말고, 같은 실행에서 받은 날짜와 두 기온이 화면에 나타나는지 확인하세요.

## 인터넷 없이 구조 연습

```bash
python3 lookup_today.py --fixture fixtures/lookup-seoul-2026-09-28-example.json
```

이 경우 2026-09-28에 보관한 실제 응답의 필요한 부분만 읽습니다. `보관 응답 예시 · 현재 예보 아님`이라는 안내가 먼저 표시됩니다. 이 파일은 현재 날씨가 아니며 API 전체 원문도 아닙니다.

## 값이 어디서 왔는지 확인하기

- **요청 조건:** `latitude=37.57`, `longitude=126.98`, `forecast_days=1`, `timezone=Asia/Seoul`, 일별 최고·최저기온 두 항목.[1]
- **응답:** JSON의 `daily.time`, `daily.temperature_2m_max`, `daily.temperature_2m_min` 목록에서 첫 번째 값을 각각 읽습니다. 각 목록에 값이 하나씩 있고, 시간대·단위가 예상과 같은지 먼저 확인합니다.
- **표시:** `서울 · 날짜`와 `최고 …°C · 최저 …°C` 두 줄을 출력합니다. 파일 저장은 하지 않습니다.
- **오류:** 인터넷 장애나 응답 구조·단위 이상이면 오류를 표시하고 정상 조회라고 말하지 않습니다.

시험 명령: `python3 -m unittest discover -s tests -v`. 이 폴더에서 실행하세요. 루트에서 같은 명령을 실행하면 무관한 설치 패키지의 `tests`를 탐색할 수 있습니다.

## Sources

[1] https://open-meteo.com/en/docs — Open-Meteo Forecast API documentation
