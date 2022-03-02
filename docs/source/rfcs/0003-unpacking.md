Author: Saul
Reviewer: Yifan
Date: February 8, 2022

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

## Current Lineapy Behavior

We currently do not support this type of assignments. We only support basic assignment and a special case for
iterable assignments, which is incorrect.

We treat `a, b = c` as `a = c[0]; b=c[1]`, which fails when `c` is an
iterable that does not support indexing, like in a generate expression:

```bash
$ echo 'a, b = (x for x in range(2))' > tmp.py
$ lineapy python tmp.py
TypeError: 'generator' object is not subscriptable
```

## Python Behavior

Let's take a look at how this is translated into Python bytecode, to see how it interprets these expressions.

Starting with a simple one, `a, b = c`:

```python
>>> import dis
>>> dis.dis('a, b = c')
  1           0 LOAD_NAME                0 (c)
              2 UNPACK_SEQUENCE          2
              4 STORE_NAME               1 (a)
              6 STORE_NAME               2 (b)
              8 LOAD_CONST               0 (None)
             10 RETURN_VALUE
```

It uses the `UNPACK_SEQUENCE` operation with an arg of `2` to assert that the sequence has two items
and unpack it to the stack.

What about one with nesting, like `[[a], b] = c`:

```python
>>> dis.dis('[[a], b] = c')
  1           0 LOAD_NAME                0 (c)
              2 UNPACK_SEQUENCE          2
              4 UNPACK_SEQUENCE          1
              6 STORE_NAME               1 (a)
              8 STORE_NAME               2 (b)
             10 LOAD_CONST               0 (None)
             12 RETURN_VALUE
```

We see that in turn nests the `UNPACK_SEQUENCE` to just call it recursively.

Ok, what about something more complicated? Where we have a variable arg `a, *b, c, d = e`:

```python
>>> dis.dis('a, *b, c, d = e')
  1           0 LOAD_NAME                0 (e)
              2 EXTENDED_ARG             2
              4 UNPACK_EX              513
              6 STORE_NAME               1 (a)
              8 STORE_NAME               2 (b)
             10 STORE_NAME               3 (c)
             12 STORE_NAME               4 (d)
             14 LOAD_CONST               0 (None)
             16 RETURN_VALUE
```

This is a bit less straightforward. First off, the `EXTENDED_ARG` simply is used to add bytes to the argument
of the next arg, so its a detail of how the bytecode is stored. So the main story here is calling `UNPACK_EX`
with an arg value of `513`. Let's see [what the Python docs have to say about it](https://docs.python.org/3/library/dis.html#opcode-UNPACK_EX):

> Implements assignment with a starred target: Unpacks an iterable in TOS into individual values, where the total number of values can be smaller than the number of items in the iterable: one of the new values will be a list of all leftover items.
>
> The low byte of counts is the number of values before the list value, the high byte of counts the number of values after it. The resulting values are put onto the stack right-to-left.

So it's actually two bytes. If we unpack it, the high bytes are 2 and the low bytes are 1. So this means we want to unpack the first two values, and the last 1 value, and keep the rest in the middle.

These two opcodes cover all of the complex unpacking.

## Proposed Behavior

One way we could improve our current approach is to translate more versions of the variable unpacking and try to preserve its behavior more faithfully.

We could do this by trying to map to equivalent operations to the Python bytecode. We don't have a stack to push things to, but we can instead return a list of values from a function, to represent the different pieces.

If we did so, we could implement the bytecodes as two builtin functions:

```python
def l_unpack_sequence(xs: Iterable[T], n: int) -> list[T]:
    """
    Asserts the iterable `xs` is of length `n` and turns it into a list.

    The same as `l_list` but asserts the length. This was modeled after the UNPACK_SEQUENCE
    bytecode to be used in unpacking

    The result should be a view of the input.
    """
    res = list(xs)
    actual_n = len(res)
    if actual_n > n:
        raise ValueError(f"too many values to unpack (expected {n})")
    if actual_n < n:
        raise ValueError(f"not enough values to unpack (expected {n}, got {actual_n})")
    return res

def l_unpack_ex(xs: Iterable[T], before: int, after: int) -> list[Union[T, list[T]]]:
    """
    Slits the iterable `xs` into three pieces and then joins them [*first, middle, *list]
    The first of length `before`, the last of length `after`, and the middle whatever is remaining.

    Modeled after the UNPACK_EX bytecode to be used in unpacking.
    """
    res: list[Union[T, list[T]] = []
    xs_list = list(xs)
    xs_n = len(xs_list)
    min_values = before + after
    if xs_n < min_values:
        raise ValueError(f"not enough values to unpack (expected at least {min_values}, got {xs_n})")
    before_list = xs[:before]
    after_list = xs[-after:]
    middle_list = xs[before:-after]
    return [*before_list, after_list, *middle_list]
```

Now lets look at our examples.

```python
x, y = z

# should be turned into
res = l_unpack_sequence(z, 2)
x = res[0]
y = res[1]


[x], y = z

# should be turned into
res = l_unpack_sequence(z, 2)
x = l_unpack_sequence(res[0], 1)[0]
y = res[1]

x, *y, z, a = b
res = l_unpack_ex(b, 1, 2)
x = res[0]
y = res[1]
z = res[2]
a = res[3]
```
