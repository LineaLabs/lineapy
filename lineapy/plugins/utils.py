import re
import unicodedata
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


def slugify(value, allow_unicode=False):
    """
    Taken from
    https://github.com/django/django/blob/master/django/utils/text.py

    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    Lastly, replace all dashes with underscores.

    Copyright (c) Django Software Foundation and individual contributors.
    All rights reserved.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    value = re.sub(r"[-\s]+", "_", value).strip("-_")
    value = re.sub("-", "_", value)
    return value
