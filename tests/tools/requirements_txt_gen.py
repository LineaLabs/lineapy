#!/usr/bin/env python
"""
Generates the requirement infra
the INSTALL_REQUIRES is copied over manually from setup.py (since it can't be accessed as a module)

Not the highest quality code, just a helper script.
"""

import subprocess

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


DEV_REQUIRES = [
    ##
    # graphing libs
    ##
    "graphviz",
    "scour==0.38.2",  # also for graphing use, pinned because other versions are not tested and to increase stability
    ##
    # external libs used for testing
    ##
    "altair",
    "pandas",
    "sklearn",
    "flake8",
    "fastparquet",
    "matplotlib",
    "jupyterlab",
    "seaborn",
    # pinned for security reasons
    "Pillow>=9.0.1",
    ##
    # testing
    ##
    "syrupy==1.4.5",
    "pytest",
    # Coveralls doesn't work with 6.0
    # https://github.com/TheKevJames/coveralls-python/issues/326
    "coverage[toml]<6.0",
    "pytest-cov",
    "pdbpp",
    "pytest-virtualenv",
    "nbval",
    "coveralls",
    "pre-commit",
    # For benchmark CI
    "scipy",
    "astpretty",
    ##
    # docs
    ##
    "sphinx",
    "nbsphinx",
    "sphinx_rtd_theme",
    ##
    # typing
    ##
    "mypy",
    "types-PyYAML",
    "types-requests",
    "SQLAlchemy[mypy]>=1.4.0",
    ##
    # DBs
    ##
    "pg",
    "psycopg2",
    "pytest-xdist",
    "sphinx-autobuild",
]


def clean_requires():
    return [
        req.replace(">=", "==").split("==")[0]
        for req in INSTALL_REQUIRES + DEV_REQUIRES
    ]


@click.command()
@click.option("--newreq", is_flag=True, default=False, show_default=True)
def gen_requirements(newreq):
    # write to tmp file
    f = open("tmp_requirement.txt", "w")
    if newreq:
        # run pip freeze
        requirements = str(
            subprocess.check_output(["pip", "freeze"]).decode("UTF-8")
        )
    else:
        f_r = open("requirements.txt", "r")
        requirements = f_r.read()  # type: ignore
    reqs = clean_requires()
    # make sure to only include that what's in setup
    requirements = requirements.split("\n")  # type: ignore
    for req in requirements:
        if req and req.split("==")[0] in reqs:  # type: ignore
            f.write(req + "\n")  # type: ignore


if __name__ == "__main__":
    gen_requirements()
