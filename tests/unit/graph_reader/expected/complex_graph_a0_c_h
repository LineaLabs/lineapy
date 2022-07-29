import copy


def get_a0():
    a0 = 0
    a0 += 1
    return a0


def get_a_for_artifact_c_and_downstream():
    a = 1
    a += 1
    return a


def get_c(a, a0):
    b = a * 2 + a0
    c = b + 3
    return c


def get_h(a, c):
    d = a * 4
    e = d + 5
    e += 6
    a += 1
    g = c + e * 2
    h = a + g
    return h


def run_all():
    # Multiple return variables detected, need to save the variable
    # right after calculation in case of mutation downstream
    artifacts = []
    a0 = get_a0()
    artifacts.append(copy.deepcopy(a0))
    a = get_a_for_artifact_c_and_downstream()
    c = get_c(a, a0)
    artifacts.append(copy.deepcopy(c))
    h = get_h(a, c)
    artifacts.append(copy.deepcopy(h))
    return artifacts


if __name__ == "__main__":
    run_all()
