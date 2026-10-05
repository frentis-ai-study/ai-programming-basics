import csv
import os
import tempfile
from collections import Counter
from pathlib import Path


# 공백으로 나눈 토큰의 양끝에서 아래 문자만 제거합니다.
EDGE_CHARS = ".,!?;:\"'()[]{}"

# 관찰한 표기만 명시적으로 묶습니다.
ALIASES = {
    "문의가": "문의",
    "문의는": "문의",
    "문의를": "문의",
    "문의와": "문의",
    "문의로": "문의",
    "회의에서": "회의",
}

EXCLUDED_WORDS = {"오늘", "다시", "가장", "했다", "있다", "검토했다", "정리했다"}


def main():
    notes_dir = Path("notes")
    output_dir = Path("output")
    csv_path = output_dir / "keywords.csv"

    try:
        if not notes_dir.is_dir():
            print("notes 폴더가 없어요. 폴더를 만들고 .txt 메모를 넣어 주세요.")
            print("기존 CSV는 그대로 두었어요.")
            return

        with os.scandir(notes_dir) as entries:
            files = sorted(
                (
                    Path(entry.path)
                    for entry in entries
                    if entry.name.endswith(".txt") and entry.is_file()
                ),
                key=lambda path: path.name,
            )
    except OSError:
        print("notes 폴더를 살펴볼 수 없어요. 폴더의 접근 권한을 확인해 주세요.")
        print("기존 CSV는 그대로 두었어요.")
        return

    if not files:
        print("notes 폴더에 읽을 .txt 파일이 없어요.")
        print("기존 CSV는 그대로 두었어요.")
        return

    # 모든 파일을 읽는 데 성공한 뒤에만 결과 저장을 진행합니다.
    texts = []
    for path in files:
        try:
            texts.append(path.read_text(encoding="utf-8"))
        except UnicodeError:
            print(f"'{path.name}'을 UTF-8로 읽을 수 없어요.")
            print("파일의 저장 인코딩을 확인해 주세요. 기존 CSV는 그대로 두었어요.")
            return
        except OSError:
            print(f"'{path.name}' 파일을 읽을 수 없어요.")
            print("파일이 있는지와 읽기 권한을 확인해 주세요. 기존 CSV는 그대로 두었어요.")
            return

    counts = Counter()
    for text in texts:
        for token in text.split():
            word = token.strip(EDGE_CHARS)
            word = ALIASES.get(word, word)

            # 표기를 묶은 뒤 제외 목록과 글자 수를 확인합니다.
            if word in EXCLUDED_WORDS or len(word) < 2:
                continue

            counts[word] += 1

    if not counts:
        print("셀 수 있는 말이 없어요. 메모 내용을 확인해 주세요.")
        print("기존 CSV는 그대로 두었어요.")
        return

    # 횟수 내림차순, 같은 횟수이면 단어 오름차순으로 정렬합니다.
    results = sorted(counts.items(), key=lambda item: (-item[1], item[0]))

    temp_path = None
    try:
        output_dir.mkdir(parents=True, exist_ok=True)

        # CSV와 같은 폴더에 임시 파일을 완성한 뒤 교체합니다.
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8-sig",
            newline="",
            dir=output_dir,
            prefix=".keywords-",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            writer = csv.writer(temp_file)
            writer.writerow(["word", "count"])
            writer.writerows(results)
            temp_file.flush()
            os.fsync(temp_file.fileno())

        os.replace(temp_path, csv_path)
        temp_path = None

    except (OSError, UnicodeError, csv.Error):
        print("CSV를 저장하지 못했어요. output 폴더의 쓰기 권한과 저장 공간을 확인해 주세요.")
        print("기존 CSV는 그대로 두었어요.")
        return
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass
            except OSError:
                print(f"임시 파일을 지우지 못했어요. 직접 삭제해 주세요: {temp_path}")

    print("\n많이 나온 말 상위 10개:")
    for word, count in results[:10]:
        print(f"{word} {count}회 {'█' * count}")

    print(f"\n전체 결과를 {csv_path}에 저장했어요.")


if __name__ == "__main__":
    main()
