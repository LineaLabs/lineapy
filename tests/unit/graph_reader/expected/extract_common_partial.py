def get_b():
    a = 1
    a += 1
    b = a + 1
    return b


def run_all():
    b = get_b()
    return b


if __name__ == "__main__":
    run_all()
