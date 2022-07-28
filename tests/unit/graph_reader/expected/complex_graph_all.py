import copy


def get_a():
    a = 1
    return a


def get_a0():
    a0 = 0
    a0 += 1
    return a0


def get_a_for_artifact_c_and_downstream(a):
    a += 1
    return a


def get_c(a, a0):
    b = a * 2 + a0
    c = b + 3
    return c


def get_f(c):
    f = c + 7
    return f


def get_e(a):
    d = a * 4
    e = d + 5
    e += 6
    return e


def get_g2(c, e):
    g = c + e * 2
    return g


def get_h(a, g):
    a += 1
    h = a + g
    return h


def get_z(h):
    z = [1]
    z.append(h)
    return z


def run_all():
    # Multiple return variables detected, need to save the variable
    # right after calculation in case of mutation downstream
    artifacts = []
    a = get_a()
    artifacts.append(copy.deepcopy(a))
    a0 = get_a0()
    artifacts.append(copy.deepcopy(a0))
    a = get_a_for_artifact_c_and_downstream(a)
    c = get_c(a, a0)
    artifacts.append(copy.deepcopy(c))
    f = get_f(c)
    artifacts.append(copy.deepcopy(f))
    e = get_e(a)
    artifacts.append(copy.deepcopy(e))
    g = get_g2(c, e)
    artifacts.append(copy.deepcopy(g))
    h = get_h(a, g)
    artifacts.append(copy.deepcopy(h))
    z = get_z(h)
    artifacts.append(copy.deepcopy(z))
    return artifacts


if __name__ == "__main__":
    run_all()
