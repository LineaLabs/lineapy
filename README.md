<p align="center">
    <a href="https://linea.ai/">
      <img src="https://linea.ai/banner-wide-negative.png">
    </a>
</p>
<br />

![Python Versions](https://img.shields.io/badge/Python--versions-3.7%20%7C%203.8%20%7C%203.9-brightgreen)
[![Build](https://github.com/LineaLabs/lineapy/actions/workflows/python-app.yml/badge.svg)](https://github.com/LineaLabs/lineapy/actions/workflows/python-app.yml)
[![Documentation Status](https://readthedocs.com/projects/lineapy-org-lineapy/badge/?version=latest&token=925cd1d5eaedb7cc60508c9cce377574da748a7d6c050bb2c3de2a360a9f4f20)](https://docs.lineapy.org/en/latest/?badge=latest)
[![Slack](https://img.shields.io/badge/slack-@lineapy--community-CF0E5B.svg?logo=slack&logoColor=white&labelColor=3F0E40)](https://join.slack.com/t/lineacommunity/shared_invite/zt-172ddmbon-vAl4Ca8LwcnTP99UTWLVRg)
[![License](https://img.shields.io/badge/license-Apache%202-brightgreen.svg?logo=apache)](https://github.com/LineaLabs/lineapy/blob/main/LICENSE.txt)
[![PyPi](https://img.shields.io/pypi/v/lineapy.svg?logo=pypi&logoColor=white)](https://pypi.org/project/lineapy/)


Supercharge your data science workflow with LineaPy! Just two lines of code captures, analyzes,
and transforms Python code to extract production data pipelines in minutes.

- [Why Use LineaPy?](#why-use-lineapy)
- [Getting Started](#getting-started)
- [What Next?](#what-next)

## Why Use LineaPy?

Going from development to production is full of friction. Data engineering is a manual and
time-consuming process. A proliferation of libraries, tools, and technologies means data teams
spend countless hours managing infrastructure and repeating tasks. This drastically reduces
the team’s ability to deliver actionable insights in real-time.

LineaPy creates a frictionless path for taking your data science work from development to production,
backed by a decade of research and industry expertise tackling hyperscale data challenges.

> ***Data engineering, simplified.*** Your data science artifact works, now comes the cleanup.
LineaPy extracts essential operations from the messy development code in minutes not days,
simplifying data engineering with just two lines of code.

> ***You analyze, we productionize.*** Productionization is manual, messy, and it requires
software engineering expertise to create clean, reproducible code. LineaPy automatically handles
lineage and refactoring so you can focus on experimenting, analyzing, and modeling.

> ***Move fast from prototype to pipeline.*** LineaPy automates code translations to save you time
and help you stay focused. Rapidly create analytics pipelines with a simple API &mdash; no refactoring
or new tools needed. Go from your Jupyter notebook to an Airflow pipeline in minutes.

## Getting Started

### Installation

To install LineaPy, run:

```bash
$ pip install lineapy
```

Or, if using `poetry`, run:

```bash
$ poetry add lineapy
```

Or, if you want the latest version of LineaPy directly from the source, run:
```
python -m pip install git+https://github.com/LineaLabs/lineapy.git
```

### Interfaces

#### Jupyter and IPython

To use LineaPy in an interactive computing environment such as Jupyter Notebook/Lab or IPython, launch the environment with the `lineapy` command, like so:

```bash
$ lineapy jupyter notebook
```

```bash
$ lineapy jupyter lab
```

```bash
$ lineapy ipython
```

This will automatically load the LineaPy extension in the corresponding interactive shell application.

#### CLI

We can also use LineaPy as a CLI command. Run:

```bash
$ lineapy python --help
```

to see available options.

### Quick Start

Once you have LineaPy installed, you are ready to start using the package. We can start with a simple
example that demonstrates how to use LineaPy to store a variable's history. The `lineapy.save()` function
removes extraneous code to give you the simplest version of a variable's history.

Say we have development code looking as follows:

```python
import lineapy

# Define text to display in page heading
text = "Greetings"

# Some irrelevant operation
num = 1 + 2

# Change heading text
text = "Hello"

# Another irrelevant operation
num_squared = num**2

# Augment heading text
text = text + " World!"

# Try an alternative display
alt_text = text.split()
```

Now, we have reached the end of our development session and decided that we like
what we see when we `print(text)`. As shown above, `text` has gone through different
modifications, and it might not be clear how it reached its final state especially given other
extraneous operations between these modifications. We can cut through this by running:

```python
# Store the variable's history or "lineage"
lineapy.save(text, "text_for_heading")

# Retrieve the stored "artifact"
artifact = lineapy.get("text_for_heading")

# Obtain the simplest version of a variable's history
print(artifact.code)
```

which will print:

```
text = "Hello"
text = text + " World!"
```

Note that these are the minimal essential steps to get to the final state of the variable `text`.
That is, LineaPy has performed code cleanup on our behalf.


## Usage Reporting

LineaPy collects anonymous usage data that helps our team to improve the product.
Only LineaPy's API calls and CLI commands are being reported.
We strip out as much potentially sensitive information as possible, and we will
never collect user code, data, variable names, or stack traces.

You can opt-out of usage tracking by setting environment variable:

```bash
export LINEAPY_DO_NOT_TRACK=True
```

## What Next?

To learn more about LineaPy, please check out the project [documentation](https://lineapy.org/docs)
which contains many examples you can follow with. Some key resources include:

| Resource | Description |
| ------------- | - |
| **[Docs]** | This is our knowledge hub &mdash; when in doubt, start here! |
| **[Concepts]** | Learn about key concepts underlying LineaPy! |
| **[Tutorials]** | These notebook tutorials will help you better understand core functionalities of LineaPy |
| **[Use Cases]** | These domain examples illustrate how LineaPy can help in real-world applications |
| **[API Reference]** | Need more technical details? This reference may help! |
| **[Contribute]** | Want to contribute? These instructions will help you get set up! |
| **[Slack]** | Have questions or issues unresolved? Join our community and ask away! |

[Docs]: https://docs.lineapy.org/en/latest/index.html
[Concepts]: https://lineapy.org/docs/fundamentals/concepts.html
[Tutorials]: https://github.com/LineaLabs/lineapy/tree/main/examples/tutorials
[Use Cases]: https://github.com/LineaLabs/lineapy/tree/main/examples/use-cases
[API Reference]: https://lineapy.org/docs/references/api_reference.html
[Contribute]: https://lineapy.org/docs/references/development.html
[Slack]: https://lineacommunity.slack.com

