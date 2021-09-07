# lineapy

## Using Linea

There are two ways to use `linea`:
* The CLI tool: `python lineapy/cli/cli.py --mode dev your_file.py`
    * The dev mode is local, and the remote one is under development).
* A new IPython kernel: select the lineapy Kernel when you open your jupyter notebook. 
    * Note that this is still under development.

## First-time Setup

```bash
conda create --name lineapy-env python=3.8
conda activate lineapy-env
pip install -r requirements.txt
pip install -r dev-requirements.txt
pip install -e . --user
```

## Tests
Note: these should be run in root (``graph_with_csv_import`` does a relative file access)
```bash
mypy -p lineapy
black lineapy/ --check
pytest
```

## Jupyter

To make use of our virtual env, you need to do these steps (referece: https://medium.com/@nrk25693/how-to-add-your-conda-environment-to-your-jupyter-notebook-in-just-4-steps-abeab8b8d084)

```bash
conda install -c anaconda ipykernel 
python -m ipykernel install --user --name=lineapy-env
```
## Best practices

For any Jupyter Notebooks that you think your reviewer might directly comment on,
please run `jupyter nbconvert --to script` and commit the corresponding .py script to make comments easier.
