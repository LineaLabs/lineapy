# lineapy

## Using Linea

There are two ways to use `linea`:
* The CLI tool: `python lineapy/cli/cli.py --mode dev your_file.py`
    * The dev mode is local, and the remote one is under development).
* A new IPython kernel: select the lineapy Kernel when you open your 
  jupyter notebook. 
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

Note: these should be run in root (``graph_with_csv_import`` does a
  relative file access)

```bash
mypy -p lineapy
black lineapy/ --check
pytest
```


### Static end to end test/demo
For a static end to end test along with [linea-server](https://github.com/LineaLabs/linea-server)

```bash
python tests/setup_integrated_tests.py
python lineapy/app/application.py 
```

`setup_integrated_tests.py` creates the stub data that the flask application then serves.

Then head over to [linea-server](https://github.com/LineaLabs/linea-server) and 
run the usual commands there (`python application.py` and `yarn start` in 
the `/server` and `/frontend` folders respectively)

Note that if you are running these on EC2, you need to do tunneling on **three**
ports:
* One for the lineapy flask app, which is currently on 4000
* One for the linea-server flask app, which is on 5000
* And one for the linea-server dev server (for the React app), which  is on 3000

For Yifan's machine, the tunneling looks like the following:

```bash
ssh -N -f -L localhost:3000:0.0.0.0:3000 ubuntu@3.18.79.230
ssh -N -f -L localhost:5000:0.0.0.0:5000 ubuntu@3.18.79.230
ssh -N -f -L localhost:4000:0.0.0.0:4000 ubuntu@3.18.79.230
```

## Running the servers live

Coming soon!

## Jupyter

To make use of our virtual env, you need to do these steps (referece: https://medium.com/@nrk25693/how-to-add-your-conda-environment-to-your-jupyter-notebook-in-just-4-steps-abeab8b8d084)

```bash
conda install -c anaconda ipykernel 
python -m ipykernel install --user --name=lineapy-env
```
## Best practices

For any Jupyter Notebooks that you think your reviewer might directly comment on,
please run `jupyter nbconvert --to script` and commit the corresponding .py script to make comments easier.
