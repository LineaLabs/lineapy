import os
from pathlib import Path


# Set the IPYTHONDIR globally when running any tests
# This needs to be in the root directory, so that even notebooks
# tested in `./examples` use this plugin
def pytest_configure(config):
    ipython_dir = Path(__file__).parent / ".ipython"
    os.environ["IPYTHONDIR"] = str(ipython_dir.resolve())
    os.environ["AIRFLOW_HOME"] = "/tmp/airflow_home"


def pytest_collectstart(collector):
    if collector.fspath and collector.fspath.ext == ".ipynb":

        collector.skip_compare += ("image/svg+xml",)
