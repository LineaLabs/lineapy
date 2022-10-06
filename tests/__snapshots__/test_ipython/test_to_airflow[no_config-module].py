def get_a(**kwargs):
    a = [1, 2, 3]
    return a


def run_session_including_a():
    # Given multiple artifacts, we need to save each right after
    # its calculation to protect from any irrelevant downstream
    # mutations (e.g., inside other artifact calculations)
    import copy

    artifacts = dict()
    a = get_a()
    artifacts["a"] = copy.deepcopy(a)
    return artifacts


def run_all_sessions():
    artifacts = dict()
    artifacts.update(run_session_including_a())
    return artifacts


if __name__ == "__main__":
    # Edit this section to customize the behavior of artifacts
    artifacts = run_all_sessions()
    print(artifacts)
