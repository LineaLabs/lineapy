# Unpacking

## Background

Python supports different forms of variable unpacking, which we currently do not support.

For example:

```python
a, b = c
a, *rest = c
[a, b], *rest = c
a = b = c
```

The variable unpacking was added in Python 3.0 in [PEP 3132](https://www.python.org/dev/peps/pep-3132/).

On the left side of the `=`, a tuple or a list is equivalent.

This shows up in the AST in the `ast.Assign` node.


## Lineapy

We currently do not support this type of assignments. We only support basic assignment and a special case for
iterable assignments, which is incorrect.

We treat `a, b = c` as `a = c[0]; b=c[1]`, which fails when `c` is an
iterable that does not support indexing, like in a generate expression:

```bash
$ echo 'a, b = (x for x in range(2))' > tmp.py
$ lineapy python tmp.py
TypeError: 'generator' object is not subscriptable
```



