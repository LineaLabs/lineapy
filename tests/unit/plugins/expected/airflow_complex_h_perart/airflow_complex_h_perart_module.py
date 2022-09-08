def get_a_c_for_artifact_f_and_downstream():
    a0 = 0
    a0 += 1
    a = 1
    a += 1
    b = a * 2 + a0
    c = b + 3
    return a, c


def get_f(c):
    f = c + 7
    return f


def get_h(a, c):
    d = a * 4
    e = d + 5
    e += 6
    a += 1
    g = c + e * 2
    h = a + g
    return h


def run_session_including_f():
    # Given multiple artifacts, we need to save each right after
    # its calculation to protect from any irrelevant downstream
    # mutations (e.g., inside other artifact calculations)
    import copy

    artifacts = dict()
    a, c = get_a_c_for_artifact_f_and_downstream()
    f = get_f(c)
    artifacts["f"] = copy.deepcopy(f)
    h = get_h(a, c)
    artifacts["h"] = copy.deepcopy(h)
    return artifacts


def run_all_sessions():
    artifacts = dict()
    artifacts.update(run_session_including_f())
    return artifacts


if __name__ == "__main__":
    run_all_sessions()
