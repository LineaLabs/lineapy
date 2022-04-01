# Editor Integration & UX

## Supported Editors

We currently support CLI, jupyter notebook, and IPython.

If you have a custom kernels, it would be compatible with lineapy if it supports
`load_ipython_extension`, and if they follow the standard process to add the configs to IPython (e.g., `c.InteractiveShellApp.extensions = ["lineapy"]` to `ipython_config.py` and `ipython_kernel_config.py`). [More docs here](https://ipython.readthedocs.io/en/stable/config/intro.html).


## User error reporting

### Removing Lineapy errors

To reduce user confusion, we remove Lineapy's stack trace from the trace shared
with the user.

We do this by tracking the user error, and modifying the top level errors 
(which includes both lineapy errors and user errors) to just include the user errors.
Along the way, we also need to create the frame that simulates the user code (in
`executor.py`) because the original user code is not actually executed.

To achieve the stack modification for IPython, we have to override a private method:
`IPython.core.InteractiveShell._get_exc_info`, watch out for IPython upgrades.

### Correctly reporting the line number

Jupyter Notebook & Lab are more complicated than executing files. There we
write the code to be executed in a tmp file so that the error reporting
aligns. This is done in the `_end_cell` call in `ipython.py`. This aligns with
existing Jupyter/IPython behavior. For instance, if you run `1 / 0` in a
notebook, you'll get the following error (on IPython `7.31.0`).

```bash
ZeroDivisionError                         Traceback (most recent call last)
/tmp/ipykernel_195393/1455669704.py in <module>
----> 1 1 / 0

ZeroDivisionError: division by zero
```

You can trace where the error handling happens by searching for all the
invocations of `get_location_path`. You will see that it's used in quite a few
places:

- `executor.py` uses it create the new frame for error reporting
- `node_transformer.py` uses it to report errors during AST parsing
- `lineabuiltins.py` uses it for exec error reporting

## Future work

We are looking to support other editors, such as VSCode and Databricks notebooks.
If you'd like to request integration support, please let us know on Github!