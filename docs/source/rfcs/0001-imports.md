Author: Saul
Reviewer: Yifan
Date: February 5, 2022

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

_An overview of Python's imports, summerized from ["5. The import system"](https://docs.python.org/3/reference/import.html)_.

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
from module import attribute
```

Both of these use `importlib` to first get a `module` object. In the case of the first, we then bind that module object to it's name as a local variable. For the second, we bind each attribute as a name, getting that attribute from the module

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

## Required Behavior

What we are missing is the behavior that importing a submodule will update the parent module with a reference to it. Also, we need to fix the problem where importing `x.y` binds to variable `x.y`. Instead, it should only bind to variable `x` but then modify the import.

## How does (c)Python handle it?

To get some more background on how we might be able to understand this issue, lets first see how cpython handles it. First, let's take a look at the bytecode emitted for an import:

```bash
$ python -c 'import dis; dis.dis("import x.y.z")'
  1           0 LOAD_CONST               0 (0)
              2 LOAD_CONST               1 (None)
              4 IMPORT_NAME              0 (x.y.z)
              6 STORE_NAME               1 (x)
              8 LOAD_CONST               1 (None)
             10 RETURN_VALUE

$ python -c 'import dis; dis.dis("from x.y import z")'
  1           0 LOAD_CONST               0 (0)
              2 LOAD_CONST               1 (('z',))
              4 IMPORT_NAME              0 (x.y)
              6 IMPORT_FROM              1 (z)
              8 STORE_NAME               1 (z)
             10 POP_TOP
             12 LOAD_CONST               2 (None)
             14 RETURN_VALUE
```

We can see that it seperates the import into two pieces described above:

1. Load the module with `IMPORT_NAME`
2. Set the attribute locally with `STORE_NAME`.

We can also see there where we call `getattr` it uses ` IMPORT_FROM` bytecode, to handle getting the `z` submodule or property from `x.y`.

Now we know how it translates these, lets take a look at how these bytecode instructions are interpreted.

The cpython bytecode executor is defined in [`ceval.c`](https://github.com/python/cpython/blob/main/Python/ceval.c).

We can see that `IMPORT_NAME` calls the `import_name` function:

```c
        TARGET(IMPORT_NAME) {
            PyObject *name = GETITEM(names, oparg);
            PyObject *fromlist = POP();
            PyObject *level = TOP();
            PyObject *res;
            res = import_name(tstate, frame, name, fromlist, level);
            Py_DECREF(level);
            Py_DECREF(fromlist);
            SET_TOP(res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }
```

and the `IMPORT_FROM` call the `import_from` function:

```c
        TARGET(IMPORT_FROM) {
            PyObject *name = GETITEM(names, oparg);
            PyObject *from = TOP();
            PyObject *res;
            res = import_from(tstate, from, name);
            PUSH(res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }
```

In `import_name`, it get the `__import__` function and calls that. It has a "fast path" if the `__import__`
function is the builtin import function, then it can call that directly, instead of having to do the whole function setup dance:

```c
static PyObject *
import_name(PyThreadState *tstate, InterpreterFrame *frame,
            PyObject *name, PyObject *fromlist, PyObject *level)
{
    _Py_IDENTIFIER(__import__);
    PyObject *import_func, *res;
    PyObject* stack[5];

    import_func = _PyDict_GetItemIdWithError(frame->f_builtins, &PyId___import__);
    if (import_func == NULL) {
        if (!_PyErr_Occurred(tstate)) {
            _PyErr_SetString(tstate, PyExc_ImportError, "__import__ not found");
        }
        return NULL;
    }
    PyObject *locals = frame->f_locals;
    /* Fast path for not overloaded __import__. */
    if (import_func == tstate->interp->import_func) {
        int ilevel = _PyLong_AsInt(level);
        if (ilevel == -1 && _PyErr_Occurred(tstate)) {
            return NULL;
        }
        res = PyImport_ImportModuleLevelObject(
                        name,
                        frame->f_globals,
                        locals == NULL ? Py_None :locals,
                        fromlist,
                        ilevel);
        return res;
    }

    Py_INCREF(import_func);

    stack[0] = name;
    stack[1] = frame->f_globals;
    stack[2] = locals == NULL ? Py_None : locals;
    stack[3] = fromlist;
    stack[4] = level;
    res = _PyObject_FastCall(import_func, stack, 5);
    Py_DECREF(import_func);
    return res;
}
```

In `import_from`, it takes care of the logic we talked about above with relative imports. It first tries to do an attribute lookup. If that fails, it does an import of the full module, by appending the submodule name to the full package name (I have omitted the error case because it's long and deals with circular imports, which are out of scope).

```c
static PyObject *
import_from(PyThreadState *tstate, PyObject *v, PyObject *name)
{
    PyObject *x;
    PyObject *fullmodname, *pkgname, *pkgpath, *pkgname_or_unknown, *errmsg;

    if (_PyObject_LookupAttr(v, name, &x) != 0) {
        return x;
    }
    /* Issue #17636: in case this failed because of a circular relative
       import, try to fallback on reading the module directly from
       sys.modules. */
    pkgname = _PyObject_GetAttrId(v, &PyId___name__);
    if (pkgname == NULL) {
        goto error;
    }
    if (!PyUnicode_Check(pkgname)) {
        Py_CLEAR(pkgname);
        goto error;
    }
    fullmodname = PyUnicode_FromFormat("%U.%U", pkgname, name);
    if (fullmodname == NULL) {
        Py_DECREF(pkgname);
        return NULL;
    }
    x = PyImport_GetModule(fullmodname);
    Py_DECREF(fullmodname);
    if (x == NULL && !_PyErr_Occurred(tstate)) {
        goto error;
    }
    Py_DECREF(pkgname);
    return x;
```

In our `import_name`, we can see that it calls `PyImport_ImportModuleLevelObject`. This in turn eventually calls `importlib._find_and_load` which calls `_find_and_load_unlocked`. This is finally the place where it calls `setattr` on the parent module:

```python
def _find_and_load_unlocked(name, import_):
    path = None
    parent = name.rpartition('.')[0]
    parent_spec = None
    if parent:
        if parent not in sys.modules:
            _call_with_frames_removed(import_, parent)
        # Crazy side-effects!
        if name in sys.modules:
            return sys.modules[name]
        parent_module = sys.modules[parent]
        try:
            path = parent_module.__path__
        except AttributeError:
            msg = (_ERR_MSG + '; {!r} is not a package').format(name, parent)
            raise ModuleNotFoundError(msg, name=name) from None
        parent_spec = parent_module.__spec__
        child = name.rpartition('.')[2]
    spec = _find_spec(name, path)
    if spec is None:
        raise ModuleNotFoundError(_ERR_MSG.format(name), name=name)
    else:
        if parent_spec:
            # Temporarily add child we are currently importing to parent's
            # _uninitialized_submodules for circular import tracking.
            parent_spec._uninitialized_submodules.append(child)
        try:
            module = _load_unlocked(spec)
        finally:
            if parent_spec:
                parent_spec._uninitialized_submodules.pop()
    if parent:
        # Set the module as an attribute on its parent.
        parent_module = sys.modules[parent]
        try:
            setattr(parent_module, child, module)
        except AttributeError:
            msg = f"Cannot set an attribute on {parent!r} for child module {child!r}"
            _warnings.warn(msg, ImportWarning)
    return module
```

## Possible Solutions

### Producing setattr calls

One way to model this then would be to turn model imports into setattr calls:

```python
import x.y.z
import x.y.q
```

This would be converted into:

```python
x = l_import('x')
x.y = l_import('x.y')
x.y.z = l_import('x.y.z')
x.y.q = l_import('x.y.q')
```

(Here, I convert the `ImportNode` into a function call, `l_import` to make it more clear that it is simply
a function call to import the module and there is nothing special about the node.)

We could model this currently, if we treat view the import of a submodule as doing a `setattr` of the parent, like above.

However, one thing that makes this tricky is that we need to know when we add a `l_import(...)` call, what is the node for the parent call that
is updated? In some ways, this is similar to saying "path x/y/z.py was updated in this function" because we would have to implicitly look up nodes
for the parent paths and update them.

We don't support this currently, so implementing this change would require a larger refactor of how we treat these special "global/side effect" values.

### Import as a relative operation

The thing that was slightly challenging about the previous solution was that we had a function `l_import` which has an implicit dependency on the "parent" import. What if instead of having this be implicit, we make it explicit by adding this as an argument? Then our current mechanisms for modifying nodes are more readily applicable. So it would translate to:

```python
x = l_import('x')
x_y = l_import('y', x)
x_y_z = l_import('z', x_y)
x_y_q = l_import('q', x_y)
```

This is closer to the Python built in behavior, where you have a global `sys.modules` where it has a pointer to each module. And to import a child, you
grab the parent from this and update it.

I propose that we take this solution, where we keep our own internal version of `sys.modules` to map each module name to the ID of the node which imports
that module. We also make all imports relative to their parents, so that we can track all the modifications easily.

This means having more special casing for imports in our tracer, we will need a new table to keep track of them. Eventually, this could possibly be subsumed by the functionality to do path based file side effects, but instead of tackling that now, I opt to defer that till we implement that feature.

### Drawbacks

Doing this wouldn't let us slice two different submodule imports, like:

```python
import x.y
import x.z

slice(x.y.method())
# This should slice out `import x.z` but with this solution would output both of the imports
```

but I think that is fine for the time being. We haven't been doing any slicing based off of which attribute you access, so I think it's ok to keep this for modules as well. When we want to tackle tracking properties, we can tackle this case as well.

### Detail

Here I sketch some details of how we could implement most of this:

```python

##
# Linea builtins
##
# Note: this should have annotations added to make the result depend on the base_module arg if provided.
def l_import(name: str, base_module: types.ModuleType = None) -> types.ModuleType:
    """
    Imports and returns a module. If the base_module is provided, the module
    will be a submodule of the base.

    Marks the `base_module` as modified if provided.
    """
    assert "." not in name
    full_name = base_module.__name__ + "." + name if base_module else name
    __import__(full_name)
    return sys.modules[full_name]

##
# Tracer
##

class Tracer:
    # Mapping of module name to node of module.
    modules: dict[str, LineaID] = {}

    def import_module(self, name: str) -> LineaID:
        """
        Import a module. If we have already imported it, just return its ID.
        Otherwise, create new module nodes for each submodule in its parents and return it.
        """
        if name in self.modules:
            return self.modules[name]
        # Recursively go up the tree, to try to get parents, and if we don't have them, import them
        *parents, module_name = name.split(".")
        if parents:
            parent_module = self.import_module(".".join(parents))
            module = l_import(module_name, parent_module)
        else:
            module = l_import(module_name)

        self.modules[name] = module
        return module

```

Here is some pseudocode to handle the most common cases in the tracer:

`from x import y`:

```python
def handle_from_import(self, base: str, from_: str) -> None:
    """
    If `x.y` is a module, load that, otherwise get the `y` attribute of `x`.
    """
    complete_name = f"{base}.{from_}"
    if is_module(complete_name):
        value = self.import_module(complete_name)
    else:
        value = self.call("getattr", self.import_module(base), from_)
    self.assign(from_, value)
```

`import x.y`:

```python
def handle_import(self, module_name: str) -> None:
    """
    Load the module `x.y` and set the base module.
    """
    self.import_module(module_name)
    base_module = module_name.split(".")[0]
    self.assign(base_module, self.import_module(base_module))
```

`import x.y as z`:

```python
def handle_import(self, module_name: str, as_: str) -> None:
    """
    Import the full module and set it to the name
    """
    self.assign(as_, self.import_module(module_name))
```

`from x.y import *`:

```python
def handle_import(self, module_name: str) -> None:
    """
    Import the module, get all public attributes, and set them as globals
    """
    module_node = self.import_module(module_name)
    module = self.executor.get_value(module_node.id)
    for attr in get_public_attributes(module):
        self.assign(attr, self.call("getattr", module_node, attr))
```
