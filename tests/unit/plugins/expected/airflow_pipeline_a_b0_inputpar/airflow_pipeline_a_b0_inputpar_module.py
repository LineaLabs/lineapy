import argparse


def get_b0(b0, **kwargs):

    return b0


def get_a(b0, **kwargs):
    a = b0 + 1
    return a


def run_session_including_b0(b0=0):
    # Given multiple artifacts, we need to save each right after
    # its calculation to protect from any irrelevant downstream
    # mutations (e.g., inside other artifact calculations)
    import copy

    artifacts = dict()
    b0 = get_b0(b0)
    artifacts["b0"] = copy.deepcopy(b0)
    a = get_a(b0)
    artifacts["a"] = copy.deepcopy(a)
    return artifacts


def run_all_sessions(
    b0=0,
):
    artifacts = dict()
    artifacts.update(run_session_including_b0(b0))
    return artifacts


if __name__ == "__main__":
    # Edit this section to customize the behavior of artifacts
    parser = argparse.ArgumentParser()
    parser.add_argument("--b0", type=int, default=0)
    args = parser.parse_args()
    artifacts = run_all_sessions(
        b0=args.b0,
    )
    print(artifacts)
