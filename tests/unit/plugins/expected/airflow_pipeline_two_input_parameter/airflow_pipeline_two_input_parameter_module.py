import argparse


def get_pn(n, p):
    pn = p * n
    return pn


def run_session_including_pn(
    p="p",
    n=5,
):
    # Given multiple artifacts, we need to save each right after
    # its calculation to protect from any irrelevant downstream
    # mutations (e.g., inside other artifact calculations)
    import copy

    artifacts = dict()
    pn = get_pn(n, p)
    artifacts["pn"] = copy.deepcopy(pn)
    return artifacts


def run_all_sessions(
    n=5,
    p="p",
):
    artifacts = dict()
    artifacts.update(run_session_including_pn(p, n))
    return artifacts


if __name__ == "__main__":
    # Edit this section to customize the behavior of artifacts
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5)
    parser.add_argument("--p", type=str, default="p")
    args = parser.parse_args()
    artifacts = run_all_sessions(
        n=args.n,
        p=args.p,
    )
    print(artifacts)
