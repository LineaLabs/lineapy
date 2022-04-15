import io
import os
import re

# read the contents of your README file
from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
LONG_DESCRIPTION = (this_directory / "README.md").read_text()

DESCRIPTION = "Data engineering, simplified. LineaPy creates a frictionless path for taking your data science artifact from development to production."
NAME = "lineapy"
AUTHOR = "linealabs"
AUTHOR_EMAIL = "dev@lineapy.org"
URL = "https://github.com/LineaLabs/lineapy/"


def read(path, encoding="utf-8"):
    path = os.path.join(os.path.dirname(__file__), path)
    with io.open(path, encoding=encoding) as fp:
        return fp.read()


def version(path):
    """Obtain the package version from a python file e.g. pkg/__init__.py
    See <https://packaging.python.org/en/latest/single_source_version.html>.
    """
    version_file = read(path)
    version_match = re.search(
        r"""^__version__ = ['"]([^'"]*)['"]""", version_file, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


DOWNLOAD_URL = "https://github.com/LineaLabs/lineapy/"
LICENSE = "Apache License 2.0"
VERSION = version("lineapy/__init__.py")


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    download_url=DOWNLOAD_URL,
    license=LICENSE,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(exclude=["tests", "tests.*"]),
    # https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html#the-console-scripts-entry-point
    entry_points={"console_scripts": ["lineapy=lineapy.cli.cli:linea_cli"]},
    python_requires=">=3.7",
    install_requires=[
        "Pillow>=9.0.1",  # for security reasons
        "astor",
        "click>=8.0.0",
        "pydantic",
        "SQLAlchemy",
        "networkx",
        "black",
        "rich",
        "astpretty",
        "scour==0.38.2",
        "pyyaml",
        "asttokens",
        "isort",
        "graphviz",
        "IPython",
        "jinja2",
        "nbformat",
        "nbconvert",
        "requests",
    ],
    extras_require={
        "dev": [
            "altair",
            "pandas",
            "sklearn",
            "flake8",
            "fastparquet",
            "syrupy==1.4.5",
            "mypy",
            "pytest",
            "matplotlib",
            # Coveralls doesn't work with 6.0
            # https://github.com/TheKevJames/coveralls-python/issues/326
            "coverage[toml]<6.0",
            "pytest-cov",
            "jupyterlab",
            "pdbpp",
            "pytest-virtualenv",
            "nbval",
            "coveralls",
            "seaborn",
            "pre-commit",
            "SQLAlchemy[mypy]>=1.4.0",
            "sphinx",
            "nbsphinx",
            "sphinx_rtd_theme",
            "types-PyYAML",
            "types-requests",  # to satisfy mypy
            "pg",
            "psycopg2",
            "pytest-xdist",
            "sphinx-autobuild",
            # For benchmark CI
            "scipy",
        ]
    },
    include_package_data=True,
)
