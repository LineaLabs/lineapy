#!/usr/bin/env python
"""
Validate the annotations.yaml files in the instrumentation directory.
"""
import json  # for pretty printing dicts
from pathlib import Path
from typing import Any, List

import pydantic
import yaml

from lineapy.instrumentation.annotation_spec import ModuleAnnotation


def validate_spec(spec_file: Path) -> List[Any]:
    """
    Validate all '.annotations.yaml' files at path
    and return all invalid items.

    Throws yaml.YAMLError
    """
    invalid_specs: List[Any] = []
    with open(spec_file, "r") as f:
        doc = yaml.safe_load(f)

        for item in doc:
            print(
                "Module specification: {}\n".format(json.dumps(item, indent=4))
            )

            try:
                a = ModuleAnnotation(**item)
            except pydantic.error_wrappers.ValidationError as e:
                invalid_specs.append(item)
    return invalid_specs
