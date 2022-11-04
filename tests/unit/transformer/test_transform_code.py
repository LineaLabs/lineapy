from mock import MagicMock, patch

from lineapy.transformer.transform_code import transform


@patch(
    "lineapy.transformer.transform_code.NodeTransformer",
)
def test_transform_fn(nt_mock: MagicMock):
    """
    Test that the transform function calls the NodeTransformer
    """
    mocked_tracer = MagicMock()
    source_location = MagicMock()
    transform("x = 1", source_location, mocked_tracer)
    nt_mock.assert_called_once()
    mocked_tracer.db.commit.assert_called_once()
    # TODO - test that source giver is called only for 3.7 and below
