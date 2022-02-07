# Imports 

The goal of this RFC is to propose a way to improve our way of dealing with imports.

The outline of this RFC is:

1. An outline of imports in Python
2. Overview of how we handle imports now in lineapy
3. Outline some issues with the current approach, with examples
4. Sketch the various features of a required solution
5. Document how other software handles Python imports
6. Propose a concrete solution for lineapy.


## Python Imports

*An overview of Python's imports, summerized from ["5. The import system"](https://docs.python.org/3/reference/import.html)*.

In Python, imports are the method for loading code from another module. The `import` statement does two main tasks:

1. Creates a `module` object, by searching for the module.
2. Binds names in local scope to pieces of the module

Modules can nested within one another to make submodules. Submodules can be accessed as attributes of the parent module, if they are loaded. This is the main part that is not implemented correctly currently. It's documented under the ["Submodules"](https://docs.python.org/3/reference/import.html#submodules) section of the Python docs.


## Current Approach in `lineapy`

In lineapy today, we support two main forms of imports.

A base import:

```python
import module
```

An import from of an attribute in the module:

```python
import attribute from module
```

Both of these use `importlib` to first get a `module` object. In the case of the first, we then bind that module object to it's name as a local variable.  For the second, we bind each attribute as a name, getting that attribute from the module


## Shortcomings

The current approach that is implemented has a number of shortcomings.

First, we cannot use the statement `from x import y` when `y` is a non imported submodule of `x`:

```bash
$ echo 'from matplotlib import pyplot' > tmp.py
$ lineapy python tmp.py
Traceback (most recent call last):
  File "/usr/local/Caskroom/miniconda/base/envs/lineapy/lib/python3.9/site-packages/matplotlib/_api/__init__.py", line 222, in __getattr__
    raise AttributeError(
AttributeError: module 'matplotlib' has no attribute 'pyplot'
```

When trying to performing a `getattr(x, "y")`, and if `x.y` has not been imported, then `y` will not be an attribute of the `x` module yet.


Second, we cannot import a submodule and then refer to the parent module:

```bash
$ echo 'import matplotlib.pyplot; print(matplotlib.pyplot)' > tmp.py
$ lineapy python tmp.py
Traceback (most recent call last):
  File "/Users/saul/p/lineapy/tmp.py", line 1, in <module>
    import matplotlib.pyplot; print(matplotlib.pyplot)
NameError: name 'matplotlib' is not defined
```

When we do the `import x.y` form, we bind the result of importing `x.y` to the local variable `x.y` (which is not even a valid variable name. Instead, we need to import `x.y` but only bind `x` locally, because `x` will have a `y` attribute once, `x.y` is imported.
