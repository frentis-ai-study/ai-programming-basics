from pathlib import Path
from shutil import copy2


BASE = Path(__file__).parent
PRACTICE = BASE / "연습폴더"
OUTPUT = BASE / "출력"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".heic"}
DOCUMENT_EXTENSIONS = {".pdf", ".txt", ".docx", ".hwp"}


def choose_folder(file_path):
    extension = file_path.suffix.lower()
    if extension in IMAGE_EXTENSIONS:
        return "images"
    if extension in DOCUMENT_EXTENSIONS:
        return "docs"
    return "etc"


def choose_new_name(folder, file_name):
    destination = folder / file_name
    number = 2
    while destination.exists():
        stem = Path(file_name).stem
        suffix = Path(file_name).suffix
        destination = folder / f"{stem} ({number}){suffix}"
        number += 1
    return destination


def organize_files():
    counts = {"images": 0, "docs": 0, "etc": 0}
    if not PRACTICE.exists():
        print("연습폴더를 찾을 수 없습니다.")
        return

    print("정리 전:", ", ".join(p.name for p in sorted(PRACTICE.iterdir())))
    for file_path in sorted(PRACTICE.iterdir()):
        if not file_path.is_file():
            continue
        folder_name = choose_folder(file_path)
        destination_folder = OUTPUT / folder_name
        destination_folder.mkdir(parents=True, exist_ok=True)
        destination = choose_new_name(destination_folder, file_path.name)
        copy2(file_path, destination)
        counts[folder_name] += 1
        print(f"{file_path.name} -> 출력/{folder_name}/{destination.name}")

    print(f"정리 완료: 이미지 {counts['images']}개, 문서 {counts['docs']}개, 기타 {counts['etc']}개")


organize_files()
