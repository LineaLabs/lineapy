import copy


def get_a_for_artifact_b_and_downstream():
    a = 1
    a += 1
    return a


def get_b(a):
    b = a + 1
    return b


def get_c(a):
    c = a + 2
    return c


def run_all():
    # Multiple return variables detected, need to save the variable
    # right after calculation in case of mutation downstream
    artifacts = []
    a = get_a_for_artifact_b_and_downstream()
    b = get_b(a)
    artifacts.append(copy.deepcopy(b))
    c = get_c(a)
    artifacts.append(copy.deepcopy(c))
    return artifacts


if __name__ == "__main__":
    run_all()
