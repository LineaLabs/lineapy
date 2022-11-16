import ipywidgets
import networkx as nx
import pyvis
from IPython.display import HTML, display

from lineapy.api.models.linea_artifact import LineaArtifact
from lineapy.execution.context import get_context


def lineage_explorer():
    execution_context = get_context()
    executor = execution_context.executor

    db = executor.db

    full_lineage_graph = nx.Graph()

    for artifact_orm in db.get_all_artifacts():

        session_id = LineaArtifact.get_artifact_from_orm(
            db, artifact_orm
        )._session_id
        session_tag = f"User session: {session_id}"

        artifact_tag = f"Artifact: {artifact_orm.name}_{artifact_orm.version}"
        full_lineage_graph.add_node(
            artifact_tag,
            size=20,
            title=artifact_tag,
            group=1,
        )

        if session_tag not in full_lineage_graph:
            full_lineage_graph.add_node(
                session_tag,
                size=20,
                title=session_tag,
                group=2,
            )

        full_lineage_graph.add_edge(
            artifact_tag, session_tag, color="blue", lineage_type="session"
        )

    for pipeline_orm in db.get_all_pipelines():

        pipeline_tag = f"Pipeline: {pipeline_orm.name}"
        full_lineage_graph.add_node(
            pipeline_tag,
            size=20,
            title=pipeline_tag,
            group=3,
        )

        for artifact_orm in pipeline_orm.artifacts:
            artifact_tag = (
                f"Artifact: {artifact_orm.name}_{artifact_orm.version}"
            )

            full_lineage_graph.add_edge(
                pipeline_tag,
                artifact_tag,
                weight=5,
                color="black",
                lineage_type="pipeline",
            )

    output_display_group = ipywidgets.Output(
        layout={"border": "1px solid black"}
    )

    depth_slider = ipywidgets.IntSlider(
        value=1,
        min=1,
        max=4,
        step=1,
        description="Lineage Distance",
        disabled=False,
        continuous_update=False,
        orientation="horizontal",
        readout=True,
        readout_format="d",
        style={"description_width": "initial"},
    )

    select_box = ipywidgets.Combobox(
        # value=list(tag_to_node.keys())[0],
        placeholder="",
        options=list(full_lineage_graph.nodes),
        description="Choose an Artifact/Session/Pipeline",
        style={"description_width": "initial"},
        layout={"width": "max-content"},
        # ensure_option=True,
        disabled=False,
    )

    session_lineage_box = ipywidgets.Checkbox(
        value=True,
        description="Show Session Lineage",
        disabled=False,
        indent=False,
    )

    pipeline_lineage_box = ipywidgets.Checkbox(
        value=True,
        description="Show Pipeline Lineage",
        disabled=False,
        indent=False,
    )

    def event_handler(event):
        with output_display_group:

            if select_box.value in set(full_lineage_graph.nodes):
                show_session = session_lineage_box.value
                show_pipeline = pipeline_lineage_box.value

                output_display_group.clear_output()

                subgraph = nx.ego_graph(
                    full_lineage_graph,
                    select_box.value,
                    radius=depth_slider.value,
                )

                # filtering
                nodes_to_remove = []
                for node in subgraph:
                    if node == select_box.value:
                        continue
                    if subgraph.nodes[node]["group"] == 2 and not show_session:
                        nodes_to_remove.append(node)
                    if (
                        subgraph.nodes[node]["group"] == 3
                        and not show_pipeline
                    ):
                        nodes_to_remove.append(node)
                for node in nodes_to_remove:
                    if node in subgraph:
                        subgraph.remove_node(node)

                # redo after filtering to drop isolated nodes
                subgraph = nx.ego_graph(
                    subgraph,
                    select_box.value,
                    radius=depth_slider.value,
                )

                # highlight the selected node
                subgraph.nodes[select_box.value]["group"] = 0
                subgraph.nodes[select_box.value]["size"] = 30

                nt = pyvis.network.Network("500px", "500px", notebook=True)
                nt.from_nx(subgraph)
                nt.show("lineage_graph.html")
                display(HTML("lineage_graph.html"))

    select_box.observe(event_handler)
    display(select_box)

    depth_slider.observe(event_handler)
    display(depth_slider)

    session_lineage_box.observe(event_handler)

    pipeline_lineage_box.observe(event_handler)

    display(ipywidgets.HBox([session_lineage_box, pipeline_lineage_box]))

    display(output_display_group)
