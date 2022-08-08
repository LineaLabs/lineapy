from script_pipeline_a0_b0_module import get_a0, get_b0


def pipeline():
    a0 = get_a0()
    b0 = get_b0()
    return a0, b0


if __name__ == "__main__":
    pipeline()
