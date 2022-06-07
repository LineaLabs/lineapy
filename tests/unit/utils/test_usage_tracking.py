from unittest.mock import patch

from lineapy.utils.analytics.event_schemas import SaveEvent
from lineapy.utils.analytics.usage_tracking import track


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
