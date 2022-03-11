from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template

import lineapy


def load_plugin_template(template_name: str) -> Template:
    """
    Loads a jinja template for a plugin (currently only airflow) from the jinja_templates folder.
    """
    template_loader = FileSystemLoader(
        searchpath=str(
            (Path(lineapy.__file__) / "../plugins/jinja_templates").resolve()
        )
    )
    template_env = Environment(loader=template_loader)
    return template_env.get_template(template_name)
