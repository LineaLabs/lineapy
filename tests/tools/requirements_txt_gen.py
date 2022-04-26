#!/usr/bin/env python
"""
Generates the requirement infra
"""

import subprocess
from pathlib import Path

import click


INSTALL_REQUIRES = [
    "astor",
    "click>=8.0.0",
    "pydantic",
    "SQLAlchemy",
    "networkx",
    "black",
    "rich",
    "pyyaml",
    "asttokens",
    "isort",
    "IPython>=7.0.0",
    "jinja2",
    "nbformat",
    "nbconvert",
    "requests",
]


def clean_requires():
    return [req.replace(">=", "==").split("==")[0] for req in INSTALL_REQUIRES]


@click.command()
@click.option("--newreq", default=0, show_default=True)
def gen_requirements(newreq):
    # write to tmp file
    f = open("tmp_requirement.txt", "w")
    if newreq:
        # run pip freeze
        requirements = subprocess.check_output(["pip", "freeze"])
    else:
        # print(Path.cwd())
        f_r = open("requirements.txt", "r")
        requirements = f_r.read()
    reqs = clean_requires()
    # make sure to only include that what's in setup
    requirements = requirements.split("\n")
    for req in requirements:
        if req and req.split("==")[0] in reqs:  # type: ignore
            f.write(req + "\n")  # type: ignore


if __name__ == "__main__":
    gen_requirements()
