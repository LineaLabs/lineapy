# lineapy

## First-time Setup

```bash
conda create --name lineapy-env python=3.8
conda activate lineapy-env
pip install -r requirements.txt
pip install -r dev-requirements.txt
pip install -e . --user
```



## Tests

```bash
mypy -p linea
black linea/ --check
```


## Best practices

For any Jupyter Notebooks that you think your reviewer might directly comment on,
please run `jupyter nbconvert --to script` and commit the corresponding .py script to make comments easier.