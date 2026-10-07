# notes 폴더의 메모 파일(.txt)을 모두 읽어, 띄어쓰기로 나눈 말이 각각 몇 번 나왔는지 세는 프로그램
# count_notes.py에 세는 규칙을 더했습니다.
# 많이 나온 10개는 화면에 보여 주고, 전체 결과는 keywords.csv에 저장합니다.

import csv
import sys
from collections import Counter
from pathlib import Path

# 이 프로그램 파일이 있는 폴더를 기준으로 notes 폴더와 keywords.csv 위치를 정합니다.
base_folder = Path(__file__).parent
notes_folder = base_folder / "notes"
csv_file = base_folder / "keywords.csv"

# 세는 규칙 1: 왼쪽 말은 오른쪽 말로 바꿔서 셉니다. (여기에 없는 말은 바꾸지 않습니다)
same_words = {
    "문의가": "문의",
    "문의는": "문의",
    "문의를": "문의",
    "문의와": "문의",
    "문의로": "문의",
    "회의에서": "회의",
    "초안을": "초안",
}

# 세는 규칙 2: 이 말들은 세지 않습니다.
skip_words = {
    "오늘", "다시", "가장", "뒤에",
    "검토했다", "정리했다", "많았다", "살펴봤다", "나눴다", "공유했다", "확인했다",
}


def apply_rules(word):
    """말 하나에 세는 규칙을 적용합니다. 세지 않을 말이면 None을 돌려줍니다."""
    # 문장 끝의 마침표 떼기
    if word.endswith("."):
        word = word[:-1]

    # 같은 말로 묶기 (same_words에 없으면 그대로 둡니다)
    word = same_words.get(word, word)

    # 세지 않을 말과 한 글자 이하인 말 빼기
    if word in skip_words or len(word) <= 1:
        return None

    return word


# 1. notes 폴더가 있는지 확인하기
if not notes_folder.is_dir():
    print("notes 폴더를 찾을 수 없습니다. count_rules.py와 같은 곳에 notes 폴더를 만들어 주세요.")
    sys.exit(1)

# 2. notes 폴더에서 .txt 파일 찾기 (파일 이름 순서대로)
try:
    note_files = sorted(notes_folder.glob("*.txt"))
except OSError:
    print("notes 폴더를 읽을 수 없습니다. 폴더의 권한을 확인해 주세요.")
    sys.exit(1)

if not note_files:
    print("notes 폴더에 .txt 파일이 없습니다. 메모 파일을 넣은 뒤 다시 실행해 주세요.")
    sys.exit(1)

# 3. 메모 파일을 하나씩 읽어서 말 세기 (읽기만 하고, 메모 파일은 바꾸지 않습니다)
counts = Counter()
for note_file in note_files:
    try:
        text = note_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        # 하나라도 읽지 못하면 여기서 멈추므로 기존 keywords.csv는 그대로 남습니다.
        print(f"{note_file.name} 파일을 읽을 수 없습니다. 파일의 권한과 저장 형식(UTF-8)을 확인해 주세요.")
        sys.exit(1)

    for word in text.split():
        word = apply_rules(word)
        if word is not None:
            counts[word] += 1

if not counts:
    print("메모 파일에 셀 말이 없습니다. 저장하지 않고 마칩니다.")
    sys.exit(1)

# 4. 많이 나온 말부터 차례로 정리하기
results = counts.most_common()

# 5. 많이 나온 10개를 화면에 보여 주기
print(f"메모 파일 {len(note_files)}개를 읽었습니다.")
print()
print("많이 나온 말 10개")
for word, count in results[:10]:
    print(f"{word}: {count}번")

# 6. 전체 결과를 keywords.csv에 저장하기
try:
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["word", "count"])
        writer.writerows(results)
except OSError:
    print()
    print(f"{csv_file.name} 파일에 저장할 수 없습니다. 파일이 다른 프로그램에서 열려 있는지 확인해 주세요.")
    sys.exit(1)

# 7. 저장한 파일 이름 알려 주기
print()
print(f"전체 결과 {len(results)}개를 {csv_file.name} 파일에 저장했습니다.")
