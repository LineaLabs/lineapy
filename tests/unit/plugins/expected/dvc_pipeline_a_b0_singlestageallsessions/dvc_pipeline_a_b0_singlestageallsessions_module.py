def get_b0(**kwargs):
    b0 = 0
    return b0


def get_a(b0, **kwargs):
    a = b0 + 1
    return a


def run_session_including_b0():
    # Given multiple artifacts, we need to save each right after
    # its calculation to protect from any irrelevant downstream
    # mutations (e.g., inside other artifact calculations)
    import copy

    artifacts = dict()
    b0 = get_b0()
    artifacts["b0"] = copy.deepcopy(b0)
    a = get_a(b0)
    artifacts["a"] = copy.deepcopy(a)
    return artifacts


def run_all_sessions():
    artifacts = dict()
    artifacts.update(run_session_including_b0())
    return artifacts


if __name__ == "__main__":
    # Edit this section to customize the behavior of artifacts
    artifacts = run_all_sessions()
    print(artifacts)
