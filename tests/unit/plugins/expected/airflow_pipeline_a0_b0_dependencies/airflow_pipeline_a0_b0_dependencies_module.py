def get_b0():
    b0 = 0
    return b0


def get_a0():
    a0 = 0
    a0 += 1
    return a0


def run_session_including_b0():
    # Given multiple artifacts, we need to save each right after
    # its calculation to protect from any irrelevant downstream
    # mutations (e.g., inside other artifact calculations)
    import copy

    artifacts = dict()
    b0 = get_b0()
    artifacts["b0"] = copy.deepcopy(b0)
    return artifacts


def run_session_including_a0():
    # Given multiple artifacts, we need to save each right after
    # its calculation to protect from any irrelevant downstream
    # mutations (e.g., inside other artifact calculations)
    import copy

    artifacts = dict()
    a0 = get_a0()
    artifacts["a0"] = copy.deepcopy(a0)
    return artifacts


def run_all_sessions():
    artifacts = dict()
    artifacts.update(run_session_including_b0())
    artifacts.update(run_session_including_a0())
    return artifacts


if __name__ == "__main__":
    # Edit this section to customize the behavior of artifacts
    artifacts = run_all_sessions()
