import os
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

import wandb
from lineapy.utils.utils import prettify


@pytest.mark.smoke
def test_basic_wandb_slices(execute):
    os.environ["WANDB_API_KEY"] = "f40d7ccaf135db1a3103ceb335100380c3e502df"
    os.environ["WANDB_MODE"] = "offline"
    code = """import wandb

wandb.init(project='offline-demo')

config = wandb.config
config.learning_rate = 0.01
loss=-.5
wandb.log({"loss": loss})
total_time = wandb.summary["_runtime"]
"""
    res = execute(code, artifacts=["total_time"])
    assert res.artifacts["total_time"] == prettify(code)
