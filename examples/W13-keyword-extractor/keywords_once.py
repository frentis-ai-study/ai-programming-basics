from collections import Counter


def main():
    memo = input("메모를 한 줄 입력하세요: ")
    words = memo.split()

    if not words:
        print("메모가 비어 있어요. 말을 넣고 다시 실행해 주세요.")
        return

    counts = Counter(words)

    print("\n많이 나온 순서:")
    for word, count in counts.most_common():
        print(f"{word}: {count}번")


if __name__ == "__main__":
    main()
