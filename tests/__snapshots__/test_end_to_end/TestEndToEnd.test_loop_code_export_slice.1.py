def loop():
    a = []
    b = 0
    for x in range(9):
        a.append(x)
        b += x
    x = sum(a)
    y = x + b

    return y


if __name__ == "__main__":
    print(loop())
