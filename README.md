<p align="center">
<img src="https://user-images.githubusercontent.com/724072/165418570-7338c65b-0fd1-489c-b76a-f03f074f42ca.png" width="500">
</p>

![Python Versions](https://img.shields.io/badge/Python--versions-3.7%20%7C%203.8%20%7C%203.9-brightgreen)
[![Build](https://github.com/LineaLabs/lineapy/actions/workflows/python-app.yml/badge.svg)](https://github.com/LineaLabs/lineapy/actions/workflows/python-app.yml)
[![Documentation Status](https://readthedocs.com/projects/lineapy-org-lineapy/badge/?version=latest&token=925cd1d5eaedb7cc60508c9cce377574da748a7d6c050bb2c3de2a360a9f4f20)](https://docs.lineapy.org/en/latest/?badge=latest)
[![Slack](https://img.shields.io/badge/slack-@lineapy--community-CF0E5B.svg?logo=slack&logoColor=white&labelColor=3F0E40)](https://join.slack.com/t/lineacommunity/shared_invite/zt-172ddmbon-vAl4Ca8LwcnTP99UTWLVRg)
[![License](https://img.shields.io/badge/license-Apache%202-brightgreen.svg?logo=apache)](https://github.com/LineaLabs/lineapy/blob/main/LICENSE.txt)
[![PyPi](https://img.shields.io/pypi/v/lineapy.svg?logo=pypi&logoColor=white)](https://pypi.org/project/lineapy/)
[![Twitter](https://img.shields.io/twitter/follow/lineapy_oss?labelColor=00ACEE&logo=twitter)](https://twitter.com/lineapy_oss)

LineaPy is a Python package for capturing, analyzing, and automating data science workflows.
At a high level, LineaPy traces the sequence of code execution to form a comprehensive understanding
of the code and its context. This understanding allows LineaPy to provide a set of tools that help
data scientists bring their work to production more quickly and easily, with just **two lines** of code.

<p align="center">
    <b style="font-size:24px;">👇 Try It Out! 👇</b>
    <br>
    <a href="https://colab.research.google.com/drive/1o7SoVlQ-2SxjqKL7A1Dk2TbMx-utJXf2?usp=sharing"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab"/></a>
</p>

- [What Problems Can LineaPy Solve?](#what-problems-can-lineapy-solve)
  - [Cleaning Messy Notebooks](#use-case-1-cleaning-messy-notebooks)
  - [Revisiting Previous Work](#use-case-2-revisiting-previous-work)
  - [Building Pipelines](#use-case-3-building-pipelines)
- [Getting Started](#getting-started)
- [Usage Reporting](#usage-reporting)
- [What Next?](#what-next)

## What Problems Can LineaPy Solve?

### Use Case 1: Cleaning Messy Notebooks

When working in a Jupyter notebook day-to-day, it is easy to write messy code by
jumping around between cells, deleting cells, editing cells, and executing the same cell multiple times
&mdash; until we think we have some good results (e.g., tables, models, charts).
With this highly dynamic and interactive nature of notebook use, some issues may arise. For instance, 
our colleagues who try to rerun the notebook may not be able to reproduce our results. Worse, with time passing,
we ourselves may have forgotten the exact steps to produce the previous results, hence unable to help our
colleagues. 

One way to deal with this problem is to keep the notebook in sequential operations by constantly re-executing
the entire notebook during development. However, we soon realize that this interrupts our natural workflows and stream of
thoughts, decreasing our productivity. Therefore, it is much more common to clean up the notebook after development. This is a very time-consuming process and is not immune from reproducibility issues caused by deleting cells and out-of-order cell executions.

To see how LineaPy can help here, check out [this](https://github.com/LineaLabs/demos/blob/apply-consistent-notebook-structure/story/clean_up_a_messy_notebook/clean_up_a_messy_notebook.ipynb) demo.

### Use Case 2: Revisiting Previous Work

Data science is often a team effort where one person's work uses results from another's. For instance,
a data scientist building a model may use various features engineered by other colleagues.
In using results generated by other people, we may encounter issues such as missing values, numbers that
look suspicious, and unintelligible variable names. If so, we may need to check how
these results came into being in the first place. Often, this means tracing back the code that was used
to generate the result in question (e.g., feature table). In practice, this can become a challenging task
because it may not be clear who produced the result. Even if we knew who to ask, the person might not remember
where the exact version of the code is. Worse, the person may have overwritten the code without version control.
Or, the person may no longer be in the organization with no proper handover of the relevant knowledge.
In any of these cases, it becomes extremely difficult to identify the root of the issue, which may render the result
unreliable and even unusable.

To see how LineaPy can help here, check out [this](https://github.com/LineaLabs/demos/blob/apply-consistent-notebook-structure/story/discover_and_trace_past_work/discover_and_trace_past_work.ipynb) demo.

### Use Case 3: Building Pipelines

As our notebooks become more mature, they may get used like pipelines. For instance, our notebook might process the 
latest data to update dashboards. Or, it may pre-process data and dump it to the filesystem for downstream model development.
Since other people rely on up-to-date results from our work, we might be expected to re-execute these processes on a regular basis.
Running a notebook is a manual, brittle process prone to errors, so we may want to set up proper pipelines for production.
Relevant engineering support may not be available, so we may need to clean up and refactor the notebook code so it can be used in
orchestration systems or job schedulers (e.g., cron, Apache Airflow, Prefect). Of course, this is assuming that we already know
what they are and how to work with them. If not, we need to spend time learning about them in the first place.
All this operational work involves time-consuming, manual labor, which means less time for us to spend on our core duties as a data scientist.

To see how LineaPy can help here, check out [this](https://github.com/LineaLabs/demos/blob/apply-consistent-notebook-structure/story/create_a_simple_pipeline/create_a_simple_pipeline.ipynb) demo.

## Getting Started

### Installation

To install LineaPy, run:

```bash
pip install lineapy
```

Or, if you want the latest version of LineaPy directly from the source, run:

```
pip install git+https://github.com/LineaLabs/lineapy.git --upgrade
```

LineaPy offers several extras to extend its core capabilities:

| Version  | Installation Command            | Enables                                                  |
|----------|---------------------------------|----------------------------------------------------------|
| minimal  | `pip install lineapy[minimal]`  | Minimal dependencies for LineaPy                         |
| dev      | `pip install lineapy[dev]`      | All LineaPy dependencies for testing and development     |
| graph    | `pip install lineapy[graph]`    | Dependencies to visualize LineaPy node graph             |
| postgres | `pip install lineapy[postgres]` | Dependencies to use PostgreSQL backend                   |

The `minimal` version of LineaPy does not include `black` or `isort`,
which may result in less organized output code and scripts.

By default, LineaPy uses SQLite for artifact store, which keeps the package light and simple.
However, SQLite has several limitations, one of which is that it does not support multiple concurrent
writes to a database (it will result in a database lock). If you want to use a more robust database,
please follow [instructions](https://docs.lineapy.org/en/latest/guide/manage_artifacts/database/postgres.html) for using PostgreSQL.

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
print(artifact.get_code())
```

which will print:

```
text = "Hello"
text = text + " World!"
```

Note that these are the minimal essential steps to get to the final state of the variable `text`.
That is, LineaPy has performed code cleanup on our behalf, moving us a step closer to production.

### Interfaces

#### Jupyter and IPython

To use LineaPy in an interactive computing environment such as Jupyter Notebook/Lab or IPython, launch the environment with the `lineapy` command, like so:

```bash
lineapy jupyter notebook
```

```bash
lineapy jupyter lab
```

```bash
lineapy ipython
```

This will automatically load the LineaPy extension in the corresponding interactive shell application.

Or, if the application is already running without the extension loaded, which can happen
when we start the Jupyter server with `jupyter notebook` or `jupyter lab` without `lineapy`,
you can load it on the fly with:

```python
%load_ext lineapy
```

executed at the top of your session. Please note:

- You will need to run this as the first command in a given session; executing it
in the middle of a session will lead to erroneous behaviors by LineaPy.

- This loads the extension to the current session only, i.e., it does not carry over
to different sessions; you will need to repeat it for each new session.

#### Hosted Jupyter Environment

In hosted Jupyter notebook environments such as JupyterHub, Google Colab, Kaggle or other environments that you do not start your notebook from CLI (such as Jupyter extension within VS Code), you need to install `lineapy` directly within your notebook first via:

```ipython
!pip install lineapy
```

then you can manually load `lineapy` extension with :

```python
%load_ext lineapy
```

For environments with older versions `IPython<7.0` like Google Colab, we need to upgrade the `IPython>=7.0` module before the above steps, we can upgrade `IPython` via:

```ipython
!pip install --upgrade ipython
```

and restart the notebook runtime:

```ipython
exit()
```

then we can start setting up LineaPy as described previously.

#### CLI

We can also use LineaPy as a CLI command. Run:

```bash
lineapy python --help
```

to see available options.

## Usage Reporting

LineaPy collects anonymous usage data that helps our team to improve the product.
Only LineaPy's API calls and CLI commands are being reported.
We strip out as much potentially sensitive information as possible, and we will
never collect user code, data, variable names, or stack traces.

You can opt-out of usage tracking by setting environment variable:

```bash
export LINEAPY_DO_NOT_TRACK=true
```

## What Next?

To learn more about LineaPy, please check out the project [documentation](https://docs.lineapy.org/en/latest/index.html)
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
[Concepts]: https://docs.lineapy.org/en/latest/fundamentals/concepts.html
[Tutorials]: https://github.com/LineaLabs/lineapy/tree/main/examples/tutorials
[Use Cases]: https://github.com/LineaLabs/lineapy/tree/main/examples/use_cases
[API Reference]: https://docs.lineapy.org/en/latest/references/api_reference.html
[Contribute]: https://github.com/LineaLabs/lineapy/blob/main/CONTRIBUTING.md
[Slack]: https://lineacommunity.slack.com
