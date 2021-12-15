#!/usr/bin/env python
"""
Validate the annotations.yaml files in the instrumentation directory.
"""
import glob
import json  # for pretty printing dicts

import yaml

from lineapy.instrumentation.annotation_spec import ModuleAnnotation


def test_validate_specs():
    """
    TODO: make into a nice cli tool. Also improve errors.
    """
    path = "./lineapy/instrumentation/*.annotations.yaml"
    all_valid_specs = []
    for filename in glob.glob(path):
        with open(filename, "r") as f:
            print("Evaluating file: {}\n".format(filename))
            doc = yaml.safe_load(f)
            for item in doc:
                print(
                    "Module specification: {}\n".format(
                        json.dumps(item, indent=4)
                    )
                )
                a = ModuleAnnotation(**item)
                print(f"Successfully loaded spec {a}.\n")
    return all_valid_specs


if __name__ == "__main__":
    test_validate_specs()
