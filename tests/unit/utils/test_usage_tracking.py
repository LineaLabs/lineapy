from unittest.mock import ANY, patch

import pytest

from lineapy.utils.analytics.event_schemas import SaveEvent
from lineapy.utils.analytics.usage_tracking import (
    _amplitude_url,
    _api_key,
    _device_id,
    _send_amplitude_event,
    _session_id,
    _user_id,
    track,
)
from lineapy.utils.config import options


@patch("lineapy.utils.analytics.usage_tracking.requests.post")
@patch("lineapy.utils.analytics.usage_tracking.do_not_track")
def test_send_usage(mock_do_not_track, mock_post):
    event_properties = SaveEvent(side_effect="file_system")

    mock_do_not_track.return_value = False
    track(
        event_properties,
    )
    assert mock_do_not_track.called
    assert mock_post.called


@patch("lineapy.utils.analytics.usage_tracking.requests.post")
@patch("lineapy.utils.analytics.usage_tracking.do_not_track")
def test_do_not_track(mock_do_not_track, mock_post):
    event_properties = SaveEvent(side_effect="file_system")

    mock_do_not_track.return_value = True
    track(
        event_properties,
    )
    assert mock_do_not_track.called
    assert not mock_post.called


@patch("lineapy.utils.analytics.usage_tracking.logger")
@patch("lineapy.utils.analytics.usage_tracking.requests.post")
@patch("lineapy.utils.analytics.usage_tracking.do_not_track")
def test_send_usage_failure(mock_do_not_track, mock_post, mock_logger):
    event_properties = SaveEvent(side_effect="file_system")

    mock_do_not_track.return_value = False
    mock_post.side_effect = AssertionError("something went wrong")
    track(
        event_properties,
    )
    assert mock_do_not_track.called
    assert mock_post.called
    mock_logger.debug.assert_called_with(
        "Tracking Error: something went wrong"
    )


@patch("lineapy.utils.analytics.usage_tracking.requests.post")
def test_send_amplitude_event_adds_userdata(mock_post):
    _send_amplitude_event("TestEvent", {})
    expected_event_data = [
        {
            # calling the functions generating the ids should work
            # because the results are cached with maxsize 1
            # testing if user_id/device_id etc return the right thing
            # is moot because we'll be testing uuid and pathlib module
            "event_type": "TestEvent",
            "user_id": _user_id(),
            "device_id": _device_id(),
            "session_id": _session_id(),
            "event_properties": {},
        }
    ]
    mock_post.assert_called_with(
        _amplitude_url(),
        json={
            "api_key": _api_key(),
            "events": expected_event_data,
        },
        headers=ANY,
        timeout=ANY,
    )

    # calling a second time should not change any of the properties.
    _send_amplitude_event("TestEvent", {})
    mock_post.assert_called_with(
        _amplitude_url(),
        json={
            "api_key": _api_key(),
            "events": expected_event_data,
        },
        headers=ANY,
        timeout=ANY,
    )


@pytest.mark.folder(options.safe_get("home_dir"))
def test_device_id_persisted(move_folder):
    # should not need to remove the old file since move folder is creating a new one for us
    # call the device id function.
    new_dev_id = _device_id()
    with open(options.safe_get("dev_id"), "r") as f:
        assert f.read() == new_dev_id
