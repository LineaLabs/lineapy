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
from dataclasses import asdict
from functools import lru_cache

import requests

from lineapy.utils.analytics.event_schemas import AllEvents
from lineapy.utils.config import LOG_FILE_NAME, linea_folder

logger = logging.getLogger(__name__)


LINEAPY_VERSION: str = importlib_metadata.version("lineapy")


@lru_cache(maxsize=1)
def _py_version():
    return "{major}.{minor}.{micro}".format(
        major=sys.version_info.major,
        minor=sys.version_info.minor,
        micro=sys.version_info.micro,
    )


def _amplitude_url():
    return "https://api.amplitude.com/2/httpapi"


def _api_key():
    return "90e7eb47aee98355e46e6f6ed81d1a80"


@lru_cache(maxsize=1)
def _session_id():
    return str(uuid.uuid4())  # uuid that marks current python session


@lru_cache(maxsize=1)
def do_not_track() -> bool:
    return os.environ.get("LINEAPY_DO_NOT_TRACK", str(False)).lower() == "true"


def _send_amplitude_event(event_type, event_properties):
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
    with open(linea_folder() / LOG_FILE_NAME, "a+") as f:
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

    # watch for perf!
    # https://stackoverflow.com/questions/52229521/why-is-dataclasses-asdictobj-10x-slower-than-obj-dict
    event_properties = asdict(event)
    event_properties["py_version"] = _py_version()
    event_properties["lineapy_version"] = LINEAPY_VERSION

    return _send_amplitude_event(event.__class__.__name__, event_properties)
