# `lineapy`

Lineapy is a Python library for analyzing data science workflows.

TODO: Insert terminal gif of running lineapy slicing on datascience file.

## Features

Currently, you can run Linea as CLI command to slice your Python code to extract
only the code that is neccesary to recompute some result. Along the way, Linea
stores the semantics of your code into a database, which we are working on exposing
as well.

We are working to add support for more Python contructs. We currently don't support
much control flow, function mutation, or all function definitions.

```bash
$ lineapy --help
Usage: lineapy [OPTIONS] FILE_NAME

Options:
  --mode TEXT     Either `memory`, `dev`, `test`, or `prod` mode
  --session TEXT  Either `STATIC`,or `SCRIPT` mode
  --slice TEXT    Print the sliced code that this artifact depends on
  --help          Show this message and exit.
# Run linea on a Python file to analyze it.
# Use --print-graph to print out the graph it creates
$ lineapy --print-source --print-graph tests/simple.py
...
# Use --slice to slice the code to that which is needed to recompute an artifact
$ lineapy --print-source tests/artifact.py --slice 'result'
...
```

### Installing

You can run linea either by cloning the repository or by using our Docker image.

### Docker

1. First install Docker and then authenticate to the [Github Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-to-the-container-registry)
   so you can pull our private image.
2. Now you can pull and run our image to slice Python code:

```bash
$ cat my_script.py
x = 1 + 2
y = x + 3
assert y == 4

$ docker run --rm -v $PWD:/app -w /app ghcr.io/LineaLabs/lineapy:main my_script.py --print-graph
...
```

### Repository

You can also run Linea by cloning this repository and running the `lineapy`:

```bash
$ git clone git@github.com:LineaLabs/lineapy.git
$ cd lineapy
# Linea currently requires Python 3.9
$ pip install -e .

$ cat tests/housing.py
import lineapy

import altair as alt
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier

alt.data_transformers.enable("json")
alt.renderers.enable("mimetype")

assets = pd.read_csv("ames_train_cleaned.csv")

sns.relplot(data=assets, x="Year_Built", y="SalePrice", size="Lot_Area")


def get_threshold():
    return 1970


def is_new(col):
    return col > get_threshold()


assets["is_new"] = is_new(assets["Year_Built"])

clf = RandomForestClassifier(random_state=0)
y = assets["is_new"]
x = assets[["SalePrice", "Lot_Area", "Garage_Area"]]

clf.fit(x, y)
p = clf.predict([[100 * 1000, 10, 4]])
lineapy.linea_publish(p, "p value")
# Linea will analyze your file in order to slice your code for a certain artifact.
$ lineapy --slice "p value" tests/housing.py
from sklearn.ensemble import RandomForestClassifier

clf = RandomForestClassifier(random_state=0)

p = clf.predict([[100 * 1000, 10, 4]])
```
