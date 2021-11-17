"""
A Jupyter Config that will be used by default when starting a jupyter command
in this directory.
"""

import os
import pathlib

root_dir = pathlib.Path(__file__).parent.resolve()
# Set the IPYTHONDIR so that python kernels that are started will see it
# and use it, so that they start lineapy by default
os.environ["IPYTHONDIR"] = str((root_dir / ".ipython"))


# Turn off security so it works in codespaces
c.ServerApp.token = ""
c.ServerApp.allow_origin = "*"
c.ServerApp.port = 8888
c.ServerApp.allow_root = True

# Start airflow with Jupyter
# https://jupyter-server-proxy.readthedocs.io/en/latest/server-process.html
c.ServerProxy.servers = {
    "airflow": {
        "command": ["make", "airflow_start"],
        "environment": {"AIRFLOW__WEBSERVER__WEB_SERVER_PORT": "{port}"},
        "timeout": 60 * 5,
        "absolute_url": False,
        "new_browser_tab": False,
    }
}

# Set workspaces dir so our default workspace is picked up
c.LabServerApp.workspaces_dir = str(root_dir / "jupyterlab-workspaces")
