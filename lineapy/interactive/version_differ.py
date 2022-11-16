import difflib
from typing import Dict, List, Optional

import ipywidgets
import networkx as nx
import pyvis
from IPython.display import IFrame, display

from lineapy.api.models.linea_artifact import LineaArtifact
from lineapy.execution.context import get_context


def version_differ():
    execution_context = get_context()
    executor = execution_context.executor

    db = executor.db

    all_artifact_orms = db.get_all_artifacts()

    artifact_lines: Dict[str, List[LineaArtifact]] = {}

    for artifact_orm in all_artifact_orms:
        if artifact_orm.name not in artifact_lines:
            artifact_lines[artifact_orm.name] = []

        artifact_lines[artifact_orm.name].append(
            LineaArtifact.get_artifact_from_orm(db, artifact_orm)
        )

    for art_name in artifact_lines:
        artifact_lines[art_name].sort(key=lambda art: art.version)

    select_box = ipywidgets.Combobox(
        # value=list(tag_to_node.keys())[0],
        placeholder="",
        options=list(artifact_lines.keys()),
        description="Choose an Artifact Name",
        style={"description_width": "initial"},
        layout={"width": "max-content"},
        # ensure_option=True,
        disabled=False,
    )

    slider_display_group = ipywidgets.Output(
        layout={"border": "1px solid black"}
    )

    diff_display_group = ipywidgets.Output(
        layout={"border": "1px solid black"}
    )

    prev_select_box_value = select_box.value
    base_slider: Optional[ipywidgets.IntRangeSlider] = None

    artifact_map: Dict[int, LineaArtifact] = {}

    def diff_event_handler(event):
        nonlocal base_slider
        nonlocal artifact_map
        with diff_display_group:
            if (
                base_slider
                and base_slider.value[0] in artifact_map
                and base_slider.value[1] in artifact_map
            ):
                diff_display_group.clear_output()
                base_artifact = artifact_map[base_slider.value[0]]
                head_artifact = artifact_map[base_slider.value[1]]
                diff = diff_lines(base_artifact, head_artifact)
                if not diff.strip():
                    print(base_artifact.get_code())
                else:
                    print(diff)

    def event_handler(event):
        nonlocal prev_select_box_value
        nonlocal base_slider
        nonlocal artifact_map

        with slider_display_group:

            art_name = select_box.value
            if (
                art_name in artifact_lines
                and art_name != prev_select_box_value
            ):
                slider_display_group.clear_output()
                diff_display_group.clear_output()

                prev_select_box_value = art_name

                artifact_line = artifact_lines[art_name]
                max_version = max(art.version for art in artifact_line)

                artifact_map = {}
                artifact_graph = nx.DiGraph()

                for i, head_artifact in enumerate(artifact_line):
                    artifact_map[head_artifact.version] = artifact_line[i]
                    artifact_graph.add_node(
                        str(head_artifact.version),
                        size=20,
                        title=str(head_artifact.version),
                        group=0,
                    )
                    if i > 0:
                        for base_artifact in artifact_line[i - 1 :: -1]:
                            if diff_ratio(base_artifact, head_artifact) > 0.75:
                                artifact_graph.add_edge(
                                    str(head_artifact.version),
                                    str(base_artifact.version),
                                    color="black",
                                )
                                break
                nt = pyvis.network.Network(
                    "200px", "500px", notebook=True, directed=True
                )
                nt.from_nx(artifact_graph)
                nt.show("artifact_graph.html")
                display(IFrame("artifact_graph.html", 500, 200))

                base_slider = ipywidgets.IntRangeSlider(
                    value=[0, 0],
                    min=0,
                    max=max_version,
                    step=1,
                    description="Select version:",
                    disabled=False,
                    continuous_update=False,
                    orientation="horizontal",
                    readout=True,
                    readout_format="d",
                    style={"description_width": "initial"},
                )
                base_slider.observe(diff_event_handler)
                display(base_slider)

    select_box.observe(event_handler)
    display(select_box)
    display(slider_display_group)
    display(diff_display_group)


def diff_ratio(base_artifact, head_artifact) -> float:
    head_code = head_artifact.get_code().split("\n")
    base_code = base_artifact.get_code().split("\n")

    return difflib.SequenceMatcher(None, base_code, head_code).ratio()


def diff_lines(base_artifact, head_artifact) -> str:
    head_code = head_artifact.get_code().split("\n")
    base_code = base_artifact.get_code().split("\n")

    diff = difflib.unified_diff(a=head_code, b=base_code)
    return "\n".join([d for d in diff])
