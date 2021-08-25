# TODO: reference https://github.com/pallets/flask/blob/afc13b9390ae2e40f4731e815b49edc9ef52ed4b/tests/test_cli.py

from click.testing import CliRunner
import pytest

# TODO
# @pytest.fixture
# def runner():
#     return CliRunner()


def test_no_script_error():
    # TODO
    # from lineapy.cli import cli

    # runner = CliRunner(mix_stderr=False)
    # result = runner.invoke(cli, ["missing"])
    # assert result.exit_code == 2
    # assert "Usage:" in result.stderr
    pass


def test_no_server_error():
    """
    When linea is running, there should be a database server that is active and receiving the scripts
    TODO
    """
    # from lineapy.cli import cli

    # runner = CliRunner(mix_stderr=False)
    # result = runner.invoke(cli, ["missing"])
    # assert result.exit_code == 2
    # assert "FLASK_APP" in result.stderr
    # assert "Usage:" in result.stderr
    pass
