import os
import subprocess

import pytest

from .utils import (
    WrongSlice,
    create_virtualenv,
    get_slice_path,
    get_source_path,
    normalize_source,
)


@pytest.fixture(autouse=True)
def pytorch_virtualenv():
    yield from create_virtualenv(
        "pytorch", ["torch==1.10.2", "torchvision==0.11.3", "matplotlib"]
    )


@pytest.mark.integration
@pytest.mark.xfail(reason="with statement", raises=WrongSlice)
def test_vision_plot_scripted_tensor_transforms():
    os.chdir(get_source_path("pytorch-vision/gallery"))

    args = [
        "lineapy",
        "file",
        "plot_scripted_tensor_transforms.py",
        "plot_scripted_tensor_transforms_fs",
        "lineapy.file_system",
    ]

    sliced_code = subprocess.run(
        args, check=True, stdout=subprocess.PIPE
    ).stdout.decode()

    sliced_path = get_slice_path(
        "pytorch_plot_scripted_tensor_transforms_fs.py"
    )

    # Verify running normalized version works
    subprocess.run(["python", sliced_path], check=True)

    desired_slice = sliced_path.read_text()
    try:
        # Compare code by transforming both to AST, and back to source,
        # to remove comments
        assert normalize_source(sliced_code) == normalize_source(desired_slice)
    except AssertionError:
        raise WrongSlice()
