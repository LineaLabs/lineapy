from lineapy.graph_reader.graph_util import are_nodes_content_equal
from tempfile import NamedTemporaryFile
from click.testing import CliRunner
import pytest

import lineapy
from lineapy.cli.cli import linea_cli
from lineapy.data.types import NodeType, SessionType
from lineapy.db.base import get_default_config_by_environment
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.transformer.transformer import ExecutionMode
from lineapy.utils import get_current_time, info_log

from tests.util import (
    compare_pydantic_objects_without_keys,
    reset_test_db,
    run_code,
)
from tests.stub_data.graph_with_simple_function_definition import (
    definition_node,
    assignment_node,
    code as function_definition_code,
)

# from tests.stub_data.graph_with_basic_image import (
#     code as graph_with_basic_image_code,
#     session as graph_with_basic_image_session,
# )
from tests.stub_data.graph_with_import import (
    code as import_code,
    session as import_session,
)

publish_name = "testing artifact publish"
publish_code = (
    f"import {lineapy.__name__}\na ="
    f" abs(-11)\n{lineapy.__name__}.{lineapy.linea_publish.__name__}(a,"
    f" '{publish_name}')\n"
)


class TestEndToEnd:
    """
    This Cli test serves as one end to end test and covers the
      following components:
    - LineaCli
    - transformer
    - tracer
    - LineaDB
    """

    def setup(self):
        """
        Reference https://github.com/pallets/flask/blob/
        afc13b9390ae2e40f4731e815b49edc9ef52ed4b/tests/test_cli.py

        TODO
        - More testing of error cases and error messages
        """
        self.runner = CliRunner()
        # FIXME: test harness cli, extract out magic string
        # FIXME: add methods instead of accessing session
        config = get_default_config_by_environment(ExecutionMode.DEV)
        # also reset the file
        reset_test_db(config.database_uri)
        self.db = RelationalLineaDB()
        self.db.init_db(config)

    @pytest.mark.parametrize(
        "session_type",
        [
            SessionType.SCRIPT,
            SessionType.STATIC,
        ],
    )
    def test_end_to_end_simple_graph(self, session_type, execute):
        res = execute(publish_code, session_type=session_type)

        nodes = res.graph.nodes
        assert len(nodes) == 3

    def test_publish(self, execute):
        """
        testing something super simple
        """
        res = execute(publish_code)

        artifacts = res.artifacts

        assert len(artifacts) == 1
        artifact = artifacts[0]

        info_log("logged artifact", artifact)
        assert artifact.name == publish_name
        time_diff = get_current_time() - artifact.date_created
        assert time_diff < 1000

    def test_publish_via_cli(self):
        """
        same test as above but via the CLI
        """
        with NamedTemporaryFile() as tmp:
            tmp.write(str.encode(publish_code))
            tmp.flush()
            # might also need os.path.dirname() in addition to file name
            tmp_file_name = tmp.name
            result = self.runner.invoke(
                linea_cli, ["--mode", "dev", tmp_file_name]
            )
            assert result.exit_code == 0
            return tmp_file_name

    @pytest.mark.parametrize(
        "session_type",
        [
            SessionType.SCRIPT,
            SessionType.STATIC,
        ],
    )
    def test_function_definition_without_side_effect(
        self, session_type: SessionType
    ):
        with NamedTemporaryFile() as tmp:
            tmp.write(str.encode(function_definition_code))
            tmp.flush()
            # might also need os.path.dirname() in addition to file name
            tmp_file_name = tmp.name
            # FIXME: make into constants
            result = self.runner.invoke(
                linea_cli,
                [
                    "--mode",
                    "dev",
                    "--session",
                    session_type.name,
                    tmp_file_name,
                ],
            )
            assert result.exit_code == 0
            nodes = self.db.get_nodes_by_file_name(tmp_file_name)
            assert len(nodes) == 4
            for c in nodes:
                if c.node_type == NodeType.FunctionDefinitionNode:
                    assert are_nodes_content_equal(
                        c,
                        definition_node,
                        function_definition_code,
                    )
                if c.node_type == NodeType.CallNode:
                    assert are_nodes_content_equal(
                        c,
                        assignment_node,
                        function_definition_code,
                    )

    # FIXME: this does not work, need a better story around files
    # def test_graph_with_basic_image(self):
    #     # FIXME: need to be refactored after Sauls' changes
    #     # we want to check that session context is also loading in the libraries

    #     # assert that the sessions are equal graph_with_basic_image_session
    #     tmp_file_name = run_code(graph_with_basic_image_code, "basic_image")
    #     nodes = self.db.get_nodes_by_file_name(tmp_file_name)
    #     print(nodes)
    #     assert len(nodes) == 17
    #     # TODO: check that the nodes are equal
    #     session_context = self.db.get_context(nodes[0].session_id)
    #     assert compare_pydantic_objects_without_id(
    #         session_context, graph_with_basic_image_session, True
    #     )
    def test_import(self):
        tmp_file_name = run_code(import_code, "basic_import")
        nodes = self.db.get_nodes_by_file_name(tmp_file_name)
        assert len(nodes) == 6
        session_context = self.db.get_context(nodes[0].session_id)
        # make sure that the libraries are the sam
        assert compare_pydantic_objects_without_keys(
            session_context,
            import_session,
            ["id", "libraries", "file_name", "creation_time"],
            True,
        )
        assert len(session_context.libraries) == len(import_session.libraries)
        for idx, l in enumerate(session_context.libraries):
            assert compare_pydantic_objects_without_keys(
                l, import_session.libraries[idx], ["id"], True
            )

    def test_no_script_error(self):
        # TODO
        # from lineapy.cli import cli

        # runner = CliRunner(mix_stderr=False)
        # result = runner.invoke(cli, ["missing"])
        # assert result.exit_code == 2
        # assert "Usage:" in result.stderr
        pass

    def test_compareops(self, execute):
        code = "b = 1 < 2 < 3\nassert b"
        execute(code)

    def test_binops(self, execute):
        code = "b = 1 + 2\nassert b == 3"
        execute(code)

    def test_subscript(self, execute):
        code = "ls = [1,2]\nassert ls[0] == 1"
        execute(code)

    def test_simple_graph(self, execute):
        assert execute("a = abs(-11)").values["a"] == 11
