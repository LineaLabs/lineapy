from pathlib import Path
from typing import Dict, List

import isort
from jinja2 import Environment, FileSystemLoader

import lineapy
from lineapy.instrumentation.tracer import Tracer
from lineapy.utils.config import linea_folder
from lineapy.utils.utils import prettify


def split_code_blocks(code: str, func_name: str):
    """
    Split the list of code lines to import, main code and main func blocks.
    The code block is added under a function with given name.

    :param code: the source code to split.
    :param func_name: name of the function to create.
    :return: strings representing import_block, code_block, main_block.
    """
    # We split the lines in import and code blocks and join them to full code test
    lines = code.split("\n")
    # Imports are at the top, find where they end
    end_of_imports_line_num = 0
    import_open_bracket = False
    while (
        "import" in lines[end_of_imports_line_num]
        or "#" in lines[end_of_imports_line_num]
        or "" == lines[end_of_imports_line_num]
        or "    " in lines[end_of_imports_line_num]
        and import_open_bracket
        or ")" in lines[end_of_imports_line_num]
        and import_open_bracket
    ):
        if "(" in lines[end_of_imports_line_num]:
            import_open_bracket = True
        elif ")" in lines[end_of_imports_line_num]:
            import_open_bracket = False
        end_of_imports_line_num += 1
    # everything from here down needs to be under def()
    # TODO Support arguments to the func
    code_block = f"def {func_name}():\n\t" + "\n\t".join(
        lines[end_of_imports_line_num:]
    )
    import_block = "\n".join(lines[:end_of_imports_line_num])
    main_block = f"""if __name__ == "__main__":\n\tprint({func_name}())"""
    return import_block, code_block, main_block


def sliced_airflow_dag(
    tracer: Tracer,
    slice_names: List[str],
    func_name: str,
    airflow_task_dependencies: str,
) -> str:
    """
    Returns a an Airflow DAG of the sliced code.

    :param tracer: the tracer object.
    :param slice_names: list of slice names to be used as tasks.
    :param func_name: name of the DAG and corresponding functions and task prefixes,
    i.e. "sliced_housing_dag"
    :param airflow_task_dependencies: task dependencies in Airflow format,
    i.e. "'p value' >> 'y'" or "'p value', 'x' >> 'y'". Put slice names under single quotes.
    This translates to "sliced_housing_dag_p >> sliced_housing_dag_y"
    and "sliced_housing_dag_p,sliced_housing_dag_x >> sliced_housing_dag_y".
    Here "sliced_housing_dag_p" and "sliced_housing_dag_x" are independent tasks
    and "sliced_housing_dag_y" depends on them.
    :return: string containing the code of the Airflow DAG running this slice
    """

    # Remove quotes
    airflow_task_dependencies = airflow_task_dependencies.replace("\\'", "")
    airflow_task_dependencies = airflow_task_dependencies.replace("'", "")

    artifacts_code = {}
    for slice_name in slice_names:
        artifact_var = tracer.artifact_var_name(slice_name)
        slice_code = tracer.slice(slice_name)
        artifacts_code[artifact_var] = slice_code
        # "'p value' >> 'y'" needs to be replaced by "sliced_housing_dag_p >> sliced_housing_dag_y"
        airflow_task_dependencies = airflow_task_dependencies.replace(
            slice_name, f"{func_name}_{artifact_var}"
        )

    return to_airflow(
        artifacts_code,
        func_name,
        Path(tracer.session_context.working_directory),
        airflow_task_dependencies,
    )


def to_airflow(
    artifacts_code: Dict[str, str],
    func_name: str,
    working_directory: Path,
    task_dependencies: str = "",
) -> str:
    """
    Transforms sliced code into airflow code.
    """

    working_dir_str = repr(str(working_directory))

    template_loader = FileSystemLoader(
        searchpath=str(
            (Path(lineapy.__file__) / "../plugins/jinja_templates").resolve()
        )
    )
    template_env = Environment(loader=template_loader)

    AIRFLOW_DAG_TEMPLATE = template_env.get_template("airflow_dag.jinja")

    _import_blocks = []
    _code_blocks = []
    _task_names = []
    for artifact_name, sliced_code in artifacts_code.items():
        # We split the code in import and code blocks and form a function that calculates the artifact
        artifact_func_name = f"{func_name}_{artifact_name}"
        _import_block, _code_block, _ = split_code_blocks(
            sliced_code, artifact_func_name
        )
        _import_blocks.append(_import_block)
        _code_blocks.append(_code_block)
        _task_names.append(artifact_func_name)

    full_code = AIRFLOW_DAG_TEMPLATE.render(
        import_blocks=_import_blocks,
        working_dir_str=working_dir_str,
        code_blocks=_code_blocks,
        DAG_NAME=func_name,
        tasks=_task_names,
        task_dependencies=task_dependencies,
    )
    # Sort imports and move them to the top
    full_code = isort.code(full_code, float_to_top=True, profile="black")
    return prettify(full_code)
