# AI프로그래밍기초 — W10~W14 실습 소스코드

이 강의의 예제 코드·공통 입력·요청문·실행 안내를 **하나의 저장소**에 주차별로 모았습니다. 교재 원고·슬라이드·고객 제출 PDF와 강사용 원시 생성 로그는 이 저장소에 자동으로 포함하지 않습니다. 공개 저장소이므로 제작사와 수강생 모두 별도 접근 승인 없이 예제와 실습 자료를 확인할 수 있습니다.

## 전체 다운로드와 준비

GitHub 로그인 없이 **Code → Download ZIP**으로 전체를 받거나 다음 명령으로 복제합니다.

```bash
git clone https://github.com/frentis-ai-study/ai-programming-basics.git
cd ai-programming-basics
```

기존 작업 사본은 로컬 변경을 먼저 확인한 뒤 `git pull --ff-only`로 갱신합니다. 자료 열람·다운로드·HTTPS 복제에는 GitHub 계정이나 별도 초대가 필요하지 않습니다.

## 주차별 예제

- [W10 · 계산기](examples/W10-calculator/README.md): 사칙연산·입력 오류·반복 실행. `calculator.py`와 기존 실행 기록.
- [W11 · 파일 정리기](examples/W11-file-organizer/README.md): 다운로드 폴더를 모사한 `연습폴더/`, 실제로 열리는 합성 이미지·문서·ZIP, 입력 원본 사본, 종류별 복사·중복 이름 보호.
- [W12 · 날씨 수집기](examples/W12-weather-collector/README.md): 조회 → 기록 → 읽기 → 그래프. Claude Code에 보낸 요청문 네 개와 만들어진 프로그램 네 개, 시작 기록 파일과 실행 결과.
- [W13 · 키워드 추출기](examples/W13-keyword-extractor/README.md): 한 줄 세기 → 메모 파일 → 세는 규칙 → 규칙 다듬기. 실습용 메모 세 편과 요청문 네 개, 단계별 결과.
- [W14 · 기록 대시보드](examples/W14-integrated-dashboard/README.md): W12의 날씨 기록과 W13의 결과 파일을 한 화면에서 보는 Streamlit 대시보드. 요청문 네 개와 단계별 코드, 실제 화면 캡처.

W12~W14는 2026-10-07에 교안과 같은 예제로 바꾸었습니다. 세 주차 모두 폴더의 요청문을 Claude Code에 차례로 보내 만든 것입니다. 이전 예제는 Git 이력에 남아 있습니다.

## 빠른 실행

저장소 루트(`ai-programming-basics`)에서 아래 명령을 실행합니다. 괄호 안에서만 주차 폴더로 이동하므로 명령이 끝나면 원래 위치로 돌아옵니다.

```bash
(cd examples/W10-calculator && python3 calculator.py)
(cd examples/W11-file-organizer && python3 organize.py)

# W12 · 시작 기록을 넣고 조회 → 기록 → 읽기 → 그래프 (조회와 기록에는 인터넷이 필요합니다)
(cd examples/W12-weather-collector && cp forecast_records.start.csv forecast_records.csv && uv run lookup_today.py && uv run record_forecast.py && uv run show_records.py && uv run plot_forecast.py)

# W13 · 메모 파일 세기와 규칙을 더한 세기
(cd examples/W13-keyword-extractor && uv run count_notes.py && uv run count_rules.py)

# W14 · 대시보드 (끝내려면 Ctrl+C)
(cd examples/W14-integrated-dashboard && uv run --with streamlit --with pandas streamlit run dashboard.py)
```

W11은 실제 개인 Downloads를 사용하지 않습니다. 입력 원본을 옮기거나 지우지 않고 `출력/images`, `출력/docs`, `출력/etc`로 복사합니다. 자세한 절차는 W11 README에 있습니다.

W12의 날씨 값은 조회하는 날짜에 따라 달라지는 예보이며 고정 정답이 아닙니다. W12 그래프의 한글은 macOS에서 확인했습니다.

## 예제의 성격과 안전 범위

코드는 AI에게 요청해 만든 결과를 비교·확인하기 위한 자료이며 유일한 모범답안이 아닙니다. 요청문 예시를 그대로 사용해도 AI 응답은 달라질 수 있습니다. 초기 단계와 개선 단계의 기능·한계를 구별하고, 기존 출력 파일이 남았다는 사실만으로 새 실행의 성공을 판단하지 않습니다.

연습 입력은 수업용 합성 자료 또는 성격을 명시한 보관 예보입니다. 실제 개인 다운로드 파일·고객 자료·자격증명은 포함하지 않습니다. 실행 중 만든 파일은 해당 주차의 제외 규칙에 따라 Git에 올리지 않습니다. W12~W14의 `results/`와 `screens/`에는 비교용으로 보관한 실행 결과가 들어 있습니다.
