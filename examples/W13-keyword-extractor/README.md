# W13 · 작은 메모에서 파일·CSV 집계로 확장

같은 강의의 단계별 실제 생성 코드를 모았습니다. `notes/`의 세 파일은 수업용 합성 메모이며 실제 고객 기록이 아닙니다. 코드는 기존 생성본 바이트 그대로입니다.

## 실행 순서

이 README가 있는 폴더에서 실행합니다. Python 3.9 이상, 추가 패키지 없음.

```bash
python3 keywords_once.py
# 입력 예: 문의 회의 문의 배송 회의 문의
python3 keywords_files.py
python3 keywords_rules.py
python3 keywords_rules_refined.py
python3 keywords_text_only.py
python3 keywords_checked.py
```

- `keywords_once.py`: 공백으로 나눈 한 줄의 표현을 셉니다. 문의 3·회의 2·배송 1. 파일 생성 없음.
- `keywords_files.py`: `notes/*.txt`를 읽고 전체 결과를 `output/keywords.csv`에 저장합니다.
- `keywords_rules.py`: 명시한 조사 표기 대응표·제외어·두 글자 이상 기준을 적용합니다.
- `keywords_rules_refined.py`: 새로 선택한 제외어를 추가한 후속 단계입니다. 합성 메모의 결과는 전체 16행, 횟수 합계 36입니다.
- `keywords_text_only.py`: 한글·영문 조각만 세도록 확장한 후속 단계입니다.
- `keywords_checked.py`: 실패 종료 상태까지 구별하는 최종 연결용 예제입니다.

파일 단계는 **현재 작업 폴더**의 `notes`를 읽습니다. 같은 `output/keywords.csv`를 단계마다 갱신하므로 단계별 결과를 보관하려면 실행 후 별도 사본을 만드세요. 화면 상위 10개와 CSV 전체 행은 다릅니다.

## W14에 연결

`keywords_checked.py` 또는 `keywords_rules_refined.py`를 제공 메모로 실행한 CSV는 `word,count` 두 열, UTF-8 BOM, 전체 16행·합계 36입니다. W14의 `data/keywords.csv`와 대조할 수 있습니다. W14는 보관 CSV를 읽는 기능이며 메모를 새로 집계하지 않습니다.

## 자료와 한계

- `requests/`: 학생용 요청문 예시. 실제 생성 당시에는 기존 코드와 강사 조건도 함께 전달되었습니다. 짧은 문장만으로 같은 결과가 나온다는 보장은 아닙니다.
- `legacy/`: 이전 교안에 쓰인 `keywords.py`와 입력·보관 출력. 단계별 생성본과 다르므로 같은 버전으로 소개하지 않습니다.
- 규칙은 명시한 범위입니다. 완전한 한국어 형태소·의미 분석이나 업무 중요도 평가가 아닙니다.
- `keywords_files.py`부터 `keywords_text_only.py`까지는 오류 안내 후에도 종료코드가 0일 수 있습니다. 남아 있는 기존 CSV를 이번 집계 성공으로 판단하지 마세요. 후속 연결에서 종료 상태가 필요하면 `keywords_checked.py`를 사용합니다.
- 강사용 AI 응답 전문·원시 로그·전체 시험 근거는 로컬 제작 경로에 따로 보관하고 이 학생용 폴더에는 포함하지 않습니다.
