import csv
import re
from collections import Counter
from pathlib import Path


STOPWORDS = {"오늘", "다시", "가장", "없이", "뒤에", "이야기", "했다", "있다", "된다", "것", "수", "때"}
JOSA = ("에서", "으로", "에게", "까지", "부터", "이나", "은", "는", "이", "가", "을", "를", "의", "도", "로", "와", "과", "에")


def remove_josa(word):
    for josa in JOSA:
        if len(word) > len(josa) + 1 and word.endswith(josa):
            return word[: -len(josa)]
    return word


word_counts = Counter()
for path in sorted(Path("notes").glob("*.txt")):
    text = path.read_text(encoding="utf-8")
    for raw_word in re.findall(r"[가-힣A-Za-z]+", text):
        word = remove_josa(raw_word)
        if len(word) >= 2 and word not in STOPWORDS:
            word_counts[word] += 1

for word, count in word_counts.most_common(10):
    print(f"{word:8s} {count}회  {'█' * count}")

output_folder = Path("출력")
output_folder.mkdir(exist_ok=True)
csv_path = output_folder / "keywords.csv"
with csv_path.open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    writer.writerow(["word", "count"])
    writer.writerows(word_counts.most_common())

print(f"전체 결과를 {csv_path}에 저장했습니다.")
