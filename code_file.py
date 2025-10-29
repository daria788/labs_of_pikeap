import sys
import math

def get_coefficient(prompt):
    while True:
        try:
            value = input(prompt)
            return float(value)
        except ValueError:
            print("Ошибка, введите другое число")

def d_urav(a, b, c):
    if a == 0:
        if b == 0:
            if c == 0:
                return "inf"
            else:
                return []
        m = -c / b
        return [m]
    discriminat = b * b - 4 * a * c
    if discriminat < 0:
        return []
    elif discriminat == 0:
        y = -b / (2 * a)
        return [y]
    else:
        sqd = math.sqrt(discriminat)
        y1 = (-b - sqd) / (2 * a)
        y2 = (-b + sqd) / (2 * a)
        return [y1, y2]

def solve_biquadratic_or_reduced(a, b, c):
    print(f"Решение уравнения: ({a})x^4 + ({b})x^2 + ({c}) = 0")

    if a == 0 and b == 0 and c == 0:
        print("Уравнение: 0 = 0")
        print("Бесконечное количество решений.")
        return

    if a == 0 and b == 0:
        print(f"Уравнение: {c} = 0")
        print("Нет решений.")
        return

    y_roots = d_urav(a, b, c)

    if y_roots == "inf":
        print("Бесконечное количество решений.")
        return

    x_roots = []

    for y in y_roots:
        if y < 0:
            continue
        elif y == 0:
            x_roots.append(0.0)
        else:
            sqrt_y = math.sqrt(y)
            x_roots.append(sqrt_y)
            x_roots.append(-sqrt_y)

    x_roots = sorted(set(x_roots))

    if x_roots:
        print("Действительные корни уравнения:")
        for root in x_roots:
            print(root)
    else:
        print("Действительных корней нет.")

def main():
    coeff = []

    # Попробуем прочитать коэффициенты из командной строки
    if len(sys.argv) == 4:
        try:
            a = float(sys.argv[1])
            b = float(sys.argv[2])
            c = float(sys.argv[3])
            coeff = [a, b, c]
            print(f"A: {a}, B: {b}, C: {c}")
        except ValueError:
            print("Аргументы должны быть числами. Переход к ручному вводу...")


    if len(coeff) != 3:
        a = get_coefficient("Введите A: ")
        b = get_coefficient("Введите B: ")
        c = get_coefficient("Введите C: ")
        coeff = [a, b, c]

    a, b, c = coeff

    solve_biquadratic_or_reduced(a, b, c)

if __name__ == "__main__":
    main()
