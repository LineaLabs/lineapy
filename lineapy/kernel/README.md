# Kernel Readme

## Setup

Please follow the following commands
```bash
python -m lineapy.kernel.install
```

### Some notes on the installation process

Note that we shouldn't need to run the above directly, and the setup.py should handle it, but that's for future debugging.
Yifan has explored a few different options (and it seems like the documentation is a little sparse...) 
* Having the `data_file` in `setup.py` should have worked, but they don't.
* Another command that should probably work `jupyter kernelspec install --user lineapy/kernel` which I haven't tried, was not working for an older iteration.

But the Kernel currently hangs.


## Dev notes

For **code changes**: the kernel is running the lineapy through `python -m`, so if your local pip install of `lineapy` is aliased (as is the case with the `-e` flag), the code should be changing automatically.

For **when your kernel hangs**: you should be able to see the error messages in the terminal where you start the Jupyter notebook. Note that unlike the commandline solution, the Kernel code outpyts will not be mixed with the user code outputs.
