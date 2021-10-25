import io
import os
import re

from setuptools import find_packages, setup

LONG_DESCRIPTION = """"""
DESCRIPTION = ""
NAME = "lineapy"
AUTHOR = "linealabs"
AUTHOR_EMAIL = "dev@linea.ai"
URL = "linea.ai"


def read(path, encoding="utf-8"):
    path = os.path.join(os.path.dirname(__file__), path)
    with io.open(path, encoding=encoding) as fp:
        return fp.read()


def version(path):
    """Obtain the packge version from a python file e.g. pkg/__init__.py
    See <https://packaging.python.org/en/latest/single_source_version.html>.
    """
    version_file = read(path)
    version_match = re.search(
        r"""^__version__ = ['"]([^'"]*)['"]""", version_file, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


DOWNLOAD_URL = "linea.ai"
LICENSE = "TODO"
VERSION = version("lineapy/__init__.py")

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    download_url=DOWNLOAD_URL,
    license=LICENSE,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
    ],
    packages=find_packages(),
    # https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html#the-console-scripts-entry-point
    entry_points={
        "console_scripts": ["lineapy=lineapy.cli.cli:linea_cli"],
    },
    install_requires=[
        "Pillow",
        "astor",
        "click>=8.0.0",
        "pydantic",
        "SQLAlchemy",
        "networkx",
        "black",
        "rich",
        "astpretty",
    ],
    extras_require={
        "dev": [
            "altair",
            "pandas",
            "sklearn",
            "flake8",
            "syrupy==1.4.5",
            "mypy",
            "isort",
            "pytest",
            "matplotlib",
            # Coveralls doesn't work with 6.0
            # https://github.com/TheKevJames/coveralls-python/issues/326
            "coverage[toml]<6.0",
            "pytest-cov",
            "jupyterlab",
            "ipython",
            "nbval",
            "SQLAlchemy[mypy]",
            "coveralls",
            "seaborn",
            "graphviz",
            "apache-airflow==2.2.0",
        ]
    },
    include_package_data=True,
)
