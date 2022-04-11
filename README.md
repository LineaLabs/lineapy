<p align="center">
    <a href="https://linea.ai/">
      <img src="https://linea.ai/banner-wide-negative.png">
    </a>
</p>
<br />

![Python Versions](https://img.shields.io/badge/Python--versions-3.7%20%7C%203.8%20%7C%203.9-brightgreen)
[![Build](https://github.com/LineaLabs/lineapy/actions/workflows/python-app.yml/badge.svg)](https://github.com/LineaLabs/lineapy/actions/workflows/python-app.yml)

LineaPy is a Python package for capturing, analyzing, and automating data science workflows.
On a high level, LineaPy traces the sequence of code execution in an interactive computing
environment (e.g., Jupyter Notebook) to form a comprehensive understanding of the code and
its context. This understanding allows LineaPy to provide a set of tools that help the user
get more value out of their work.

- [Why Use LineaPy?](#why-use-lineapy)
- [Getting Started](#getting-started)
- [What Next?](#what-next)

## Why Use LineaPy?

(TO ADD)

## Getting Started

### Installation

To minimize potential interference with your existing system setup, we recommend
you install LineaPy in a virtual environment using ``venv``, ``conda``, or ``poetry``.

Once the virtual environment is activated, run:

```bash
$ pip install lineapy
```

Or, if using ``poetry``, run:

```bash
$ poetry add lineapy
```

### Quick Start

In an interactive computing environment such as Jupyter Notebook, we often find our work
evolving incrementally. That is, our code takes different turns to reflect our thought stream.
The following exemplifies this type of "dynamism" in interactive computing:

```python
import lineapy

# Define text to display in page heading
text = "Greetings"

# Change heading text
text = "Hello"

# Augment heading text
text = text + " World!"

# Try an alternative display
alt_text = text.split()
```

Now, let's say we have reached the end of our programming session and decided that we like
what we see when we ``print(text)``. As shown above, ``text`` has gone through different
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

Note that these are the minimal essential steps to get to the final state of the variable ``text``.

## What Next?

If you want to learn more about `lineapy`, please check out our project [documentation](https://lineapy.org/docs) which contains many examples you can follow with. Some key resources include:

| Resource | Description |
| ------------- | - |
| **[Docs]** | This is our knowledge hub &mdash; when in doubt, start here! |
| **[Concepts]** | Learn about key concepts underlying LineaPy! |
| **[Tutorials]** | These notebook tutorials will help you better understand core functionalities of LineaPy |
| **[Use Cases]** | These domain examples will illustrate how LineaPy can help in real-world applications |
| **[API Reference]** | Need more technical details? This reference may help! |
| **[Contribute]** | Want to contribute? These instructions will help you get set up! |
| **[Slack]** | Have questions or issues unresolved? Join our community and ask away! |

[Docs]: https://lineapy.org/docs
[Concepts]: https://lineapy.org/docs/fundamentals/concepts.html
[Tutorials]: https://github.com/LineaLabs/lineapy/tree/main/examples/tutorials
[Use Cases]: https://github.com/LineaLabs/lineapy/tree/main/examples/use-cases
[API Reference]: https://lineapy.org/docs/references/api_reference.html
[Contribute]: https://lineapy.org/docs/references/development.html
[Slack]: https://lineacommunity.slack.com
