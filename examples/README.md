# Lineapy Examples

To validate our features, we downloaded some Kaggle notebook and added the two lines of `lineapy` instrumentation:

```python
import lineapy
lineapy.linea_publish(variable, "a description")
```

Currently we have a working example, `kaggle_example1.py` (the other example, `kaggle_example2.py` is [WIP due to a known bug](https://github.com/LineaLabs/lineapy/issues/204)).

```bash
lineapy --print-source kaggle_example1.py --slice 'mushroom feature importance'
```


## Limitations

- The second notebook doesn't currently work

```bash
lineapy --print-source  kaggle_example2.py --slice 'nn for diabetes'
```

- [Can only slice one variable through the CLI](https://github.com/LineaLabs/lineapy/issues/307)
- [The CLI does not run a notebook](https://github.com/LineaLabs/lineapy/issues/304)

Again, we welcome any feature requests you might have!