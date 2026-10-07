# 메모 한 줄을 입력받아, 띄어쓰기로 나눈 말이 각각 몇 번 나왔는지 세어 보여 주는 프로그램

from collections import Counter

# 1. 메모 한 줄 입력받기
memo = input("메모를 한 줄 입력하세요: ")

# 2. 띄어쓰기를 기준으로 말 나누기 (띄어쓰기가 여러 칸이어도 알아서 처리됩니다)
words = memo.split()

if not words:
    # 3. 아무것도 입력하지 않았을 때 안내하기
    print("입력된 말이 없습니다. 메모를 한 줄 입력한 뒤 Enter를 눌러 주세요.")
else:
    # 4. 말이 각각 몇 번 나왔는지 세기
    counts = Counter(words)

    # 5. 많이 나온 말부터 차례로 보여 주기
    print()
    print("많이 나온 말부터 보여 드립니다.")
    for word, count in counts.most_common():
        print(f"{word}: {count}번")
