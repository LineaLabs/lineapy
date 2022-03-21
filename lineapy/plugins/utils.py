import re
import sys
from pathlib import Path
from typing import Dict

from jinja2 import Environment, FileSystemLoader, Template

import lineapy

# Python is not aware of a package's pip name, so we need to get it from the module
PIP_PACKAGE_NAMES: Dict[str, str] = {
    "sklearn": "scikit-learn",
}


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


def safe_var_name(name: str) -> str:
    """
    Returns a python-safe variable name for the given string.
    eg for name = "p value"  "p_value" is returned
    """
    return re.sub("\W|^(?=\d)", "_", name)  # noqa


def get_lib_version_text(name: str) -> str:
    mod = sys.modules[name]
    package_name = mod.__name__
    mod_version = None
    if hasattr(mod, "__version__"):
        mod_version = mod.__version__
    else:
        # package is probably a submodule
        parent_package_name = name.split(".")[0]
        parent_package = sys.modules[parent_package_name]
        package_name = parent_package.__name__
        if hasattr(parent_package, "__version__"):
            mod_version = parent_package.__version__

    # change to pip package name if an override exists
    package_name = PIP_PACKAGE_NAMES.get(package_name, package_name)

    text = package_name + (("==" + mod_version) if mod_version else "")
    return text
