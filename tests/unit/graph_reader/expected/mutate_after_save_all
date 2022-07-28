import copy


def get_a():
    a = [1]
    return a


def get_b(a):
    a.append(2)
    b = a[-1] + 1
    return b


def run_all():
    # Multiple return variables detected, need to save the variable
    # right after calculation in case of mutation downstream
    artifacts = []
    a = get_a()
    artifacts.append(copy.deepcopy(a))
    b = get_b(a)
    artifacts.append(copy.deepcopy(b))
    return artifacts


if __name__ == "__main__":
    run_all()
