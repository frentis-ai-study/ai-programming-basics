def 보기좋은_숫자(숫자):
    """정수는 소수점 없이 보여 줍니다."""
    return f"{숫자:g}"


def 계산하기(첫째, 연산자, 둘째):
    if 연산자 == "+":
        return 첫째 + 둘째
    if 연산자 == "-":
        return 첫째 - 둘째
    if 연산자 == "*":
        return 첫째 * 둘째
    if 연산자 == "/":
        if 둘째 == 0:
            return "0으로 나눌 수 없습니다."
        return 첫째 / 둘째
    return "+, -, *, / 중에서 선택해 주세요."


print("간단한 계산기입니다.")

while True:
    try:
        첫째 = float(input("첫 번째 수: "))
        연산자 = input("연산자(+, -, *, /): ").strip()
        둘째 = float(input("두 번째 수: "))
        결과 = 계산하기(첫째, 연산자, 둘째)

        if isinstance(결과, float):
            결과 = 보기좋은_숫자(결과)
        print(f"결과: {결과}")
    except ValueError:
        print("숫자를 입력해 주세요.")

    계속 = input("계속 계산할까요? (y/n): ").strip().lower()
    if 계속 != "y":
        print("계산기를 종료합니다.")
        break
