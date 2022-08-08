from script_pipeline_a0_b0_dependencies_module import get_a0, get_b0


def pipeline():
    b0 = get_b0()
    a0 = get_a0()
    return b0, a0


if __name__ == "__main__":
    pipeline()
