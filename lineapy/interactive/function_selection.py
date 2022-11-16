import ipywidgets
from IPython.display import display

from lineapy.execution.context import get_context
from lineapy.graph_reader.node_collection import UserCodeNodeCollection
from lineapy.graph_reader.program_slice import (
    get_source_code_from_graph,
    get_subgraph_nodelist,
)
from lineapy.graph_reader.utils import _is_import_node
from lineapy.instrumentation.tracer import get_tracer


def function_selector():
    execution_context = get_context()
    executor = execution_context.executor
    tracer = get_tracer()

    session_id = tracer.get_session_id()
    session_graph = tracer.graph

    vars = executor.db.get_variables_for_session(session_id)

    input_lines = []
    output_lines = []

    output_display_group = ipywidgets.Output(
        layout={"border": "1px solid black"}
    )

    for node_id, var_name in vars:
        if not _is_import_node(session_graph, node_id):
            source_code = get_source_code_from_graph(
                set([node_id]), session_graph
            )
            input_lines.append(
                (
                    node_id,
                    ipywidgets.Checkbox(
                        value=False,
                        description=f"{source_code}",
                        disabled=False,
                        indent=False,
                    ),
                    var_name,
                )
            )
            output_lines.append(
                (
                    node_id,
                    ipywidgets.Checkbox(
                        value=False,
                        description=f"{source_code}",
                        disabled=False,
                        indent=False,
                    ),
                    var_name,
                )
            )

    btn = ipywidgets.Button(description="Create Function")

    def event_handler(event):

        input_ids = []
        input_vars = []
        for node_id, checkbox, var_name in input_lines:
            if checkbox.value:
                input_ids.append(node_id)
                input_vars.append(var_name)

        output_ids = []
        output_vars = []
        for (node_id, checkbox, var_name) in output_lines:
            if checkbox.value:
                output_ids.append(node_id)
                output_vars.append(var_name)

        with output_display_group:
            output_display_group.clear_output()
            if event is btn:
                subgraph_nodelist = get_subgraph_nodelist(
                    session_graph,
                    sinks=output_ids,
                    sources=input_ids,
                    keep_lineapy_save=False,
                )
                unc = UserCodeNodeCollection(
                    subgraph_nodelist,
                    "user created function",
                    input_variables=set(input_vars),
                    return_variables=output_vars,
                )
                print("Commit")
                print(unc.get_function_definition(session_graph, False))

    btn.on_click(event_handler)

    w = ipywidgets.widgets.Output()
    with w:
        display("Input variables")
    input_widgets = [w]
    for _, widget, _ in input_lines:
        input_widgets.append(widget)
        widget.observe(event_handler)

    input_box = ipywidgets.VBox(input_widgets)

    w = ipywidgets.widgets.Output()
    with w:
        display("Output variables")
    output_widgets = [w]
    for _, widget, _ in output_lines:
        output_widgets.append(widget)
        widget.observe(event_handler)

    output_box = ipywidgets.VBox(output_widgets)

    display(ipywidgets.HBox([input_box, output_box]))
    display(btn)
    display(output_display_group)
