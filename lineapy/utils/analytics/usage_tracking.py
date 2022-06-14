# this page contains references file usage_stats.py from  https://github.com/bentoml/BentoML

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    # this is for python 3.7
    import importlib_metadata  # type: ignore

import json
import logging
import os
import sys
import uuid
from functools import lru_cache

import requests
from IPython import get_ipython

from lineapy.utils.analytics.event_schemas import AllEvents
from lineapy.utils.config import options

logger = logging.getLogger(__name__)


LINEAPY_VERSION: str = importlib_metadata.version("lineapy")


@lru_cache(maxsize=1)
def _py_version() -> str:
    return "{major}.{minor}.{micro}".format(
        major=sys.version_info.major,
        minor=sys.version_info.minor,
        micro=sys.version_info.micro,
    )


@lru_cache(maxsize=1)
def _runtime() -> str:
    if get_ipython() is None:
        runtime = "non-ipython"
    else:
        # Collect and concatenate all env var names to see
        # if this concatenated string contains a pattern
        # unique to each runtime.
        # NOTE: We are not using ``get_ipython()`` as it does not really give the info we desire.
        # For instance, it returns ``ipykernel.zmqshell.ZMQInteractiveShell`` object in both Databricks
        # and local Jupyter; and it does not seem to contain attribute(s) to distinguish the two.
        envars: str = ";".join(list(os.environ))
        if "DATABRICKS_" in envars:
            runtime = "ipython-databricks"
        elif "COLAB_" in envars:
            runtime = "ipython-colab"
        elif "DEEPNOTE_" in envars:
            runtime = "ipython-deepnote"
        elif "BINDER_" in envars:
            runtime = "ipython-binder"
        else:
            runtime = "ipython-unknown"

    # Support optional custom tag which can be used to flag
    # and discard certain events such as those from dev work
    tag = os.environ.get("LINEAPY_RUNTIME_TAG")
    if tag is not None:
        return f"[{tag}]{runtime}"

    return runtime


def _amplitude_url() -> str:
    return "https://api.amplitude.com/2/httpapi"


def _api_key() -> str:
    return "90e7eb47aee98355e46e6f6ed81d1a80"


@lru_cache(maxsize=1)
def _session_id() -> str:
    return str(uuid.uuid4())  # uuid that marks current python session


@lru_cache(maxsize=1)
def do_not_track() -> bool:
    do_not_track: bool = str(options.get("do_not_track")).lower() == "true"
    is_demo: bool = str(options.get("is_demo")).lower() == "true"
    return do_not_track or is_demo


def _send_amplitude_event(event_type: str, event_properties: dict):
    events = [
        {
            "event_type": event_type,
            "user_id": _session_id(),
            "event_properties": event_properties,
        }
    ]
    event_data = {"api_key": _api_key(), "events": events}
    headers = {"Content-Type": "application/json", "Accept": "*/*"}

    # also append to a local file for sanity checking
    with open(options.safe_get("logging_file"), "a+") as f:
        f.write(json.dumps(events) + "\n")

    # send to amplitude
    try:
        return requests.post(
            _amplitude_url(), json=event_data, headers=headers, timeout=1
        )
    except Exception as err:
        # silently fail since this error does not concern end users
        logger.debug(f"Tracking Error: {str(err)}")


def track(event: AllEvents):
    """ """
    if do_not_track():
        return

    # We assume all events are un-nested objects
    event_properties = {k: str(v) for k, v in event.__dict__.items()}
    event_properties["py_version"] = _py_version()
    event_properties["lineapy_version"] = LINEAPY_VERSION
    event_properties["runtime"] = _runtime()

    return _send_amplitude_event(event.__class__.__name__, event_properties)
