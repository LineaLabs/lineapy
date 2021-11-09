import os
from pathlib import Path


# Set the IPYTHONDIR globally when running any tests
# This needs to be in the root directory, so that even notebooks
# tested in `./examples` use this plugin
def pytest_configure(config):
    ipython_dir = Path(__file__).parent / ".ipython"
    os.environ["IPYTHONDIR"] = str(ipython_dir.resolve())
