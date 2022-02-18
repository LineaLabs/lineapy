Author: Saul
Date: February 18, 2022

# Decomposing Control Flow RFC

When dealing with control flow, we currently treat slicing it as an all-or-nothing
proposition. For example, if we have this for loop to sum some list:

```python
s = 0
for x in xs:
    print(x)
    s += x
```

We can't slice to remove the `print(x)` line. We either have to include
the full for loop or none of it.

One of the reasons this is currently not possible, is that our graph currently
represents the black boxes as single operations, a string of text to `exec`.

If we want to be able to slice inside of them, we have to break this open.

## Control Flow to Functional Form

Our current slicing algorithm is rather simple. Every node in the graph has
edges to connect all the other nodes which it depends on. So we simply walk the
graph to do our slice, and find all ancestors of the node we are looking for.

This RFC explores turning the control flow into
functional forms, by moving all of the state (io, globals, etc) into an explicit
state variable that is passed through the graph, to enable us to break up black boxes
and generates slices for parts of them.

## Example

Let's start with a simple example, to motivate this idea. We will show it is represented
currently and then how we could change the implementation.

```python
# Writes some bytes to a file
x = 100
y = x + 1
z = y + 1
f = open("some_path")
f.write(bytes([y]))

import lineapy

lineapy.save(lineapy.file_system, "fs")
```

### Current Behavior

Currently, if we wrote our graph for this, it would look like this:

```python
# x = 100
x = Literal(100, line=1)
# y = x + 1
y = Call(Lookup("add"), [x, Literal(1)], line=2)
# z = y + 1
z = Call(Lookup("add"), [y, Literal(1)], line=3)
# f = open("some_path")
f = Call(Lookup("open"), ["some_path"], line=4)
# f.write(bytes([y]))
f_write = Call(Lookup("getattr"), [f, Literal("write")], line=5)
bytes_ = Call(Lookup("bytes"), [Call(Lookup("l_list"), [y])], line=5)
f_write_bytes = Call(f_write, [bytes_], line=5)
mutated_fs = Mutate(Lookup("file_system"), f_write_bytes, line=5)
# import lineapy
lineapy = Call(Lookup("l_import"), ["lineapy"], line=6)
# lineapy.save(lineapy.file_system, "fs")
save = Call(Lookup("getattr"), [lineapy, Literal("save")], line=7)
fs = Call(Lookup("getattr"), [lineapy, Literal("file_system")], implicit=[mutated_fs], line=7)
save_fs = Call(save, [fs, Literal("fs")], line=7)
```

This would not execute, but for this RFC, let's use this toy way of writing the graph.

This toy implementation would look something like this:

```python
class Node:
    def parents(self):
        raise NotImplementedError()


@dataclass
class Literal(Node):
    value: object
    line: Optional[int] = None

    def parents(self):
        return []


@dataclass
class Call(Node):
    fn: Node
    args: List[Node]
    implicit: List[Node] = field(default_factory=list)
    line: Optional[int] = None

    def parents(self):
        return self.args + self.implicit


@dataclass
class Lookup(Node):
    name: str
    line: Optional[int] = None


def ancestors(node):
    for p in node.parents():
        yield from ancestors(p)
    yield node

def lines_for_node(node):
    return {n.line for n in  ancestors(node) if n.line is not None }


# lineapy.save function
def save(value, name):
    # Use get_context() to get the executing node, then get the first arg
    value_node = get_context().current_node.args[0]
    sliced_lines = lines_for_node(value_node)
    return {
        "code": slice_lines(get_context().source_code, sliced_lines),
    }
```

So we can see that in our current implementation, the scoping is not explicit
in the graph. We need it to make the graph, but once we are in the graph form,
it's erased.

### Explicit Scope Behavior

Now, let's imagine how we would compile it if we had explit scoping.

Let's imagine we have a global State that looks like this:

```python
@dataclass
class State:
    # Mapping from name to value
    namespace: Dict[str, object]
    # Mapping from module name to module for all loaded modules
    modules: Dict[str, types.ModuleType]
    # Mapping from path to file contents
    fs: Dict[str, bytes]
    # Mapping from name to the value of the artifact
    artifacts: Dict[str, object]

def set_var(state, name, value):
    new_namespace = {**state.namespace, name: value}
    return replace(state, namespace=new_namespace)

def get_var(state, name):
    return state.namespace[name]

def with_state(state, fn, *args, **kwargs):
    res = fn(*args, **kwargs)
    return (, res)

def
```

We can think about our program as a function that takes in a State and returns a new State, like this:

```python

def my_program(state):
    # x = 100
    state = Call(
        Lookup("set_var"), [state, Literal("x"), Literal(100)], line=1
    )

    # y = x + 1
    res_y = Call(
        Lookup("add"),
        [
            Call(Lookup("get_var"), [state, Literal("x")]),
            Literal(1),
        ],
    )
    state = Call(Lookup("set_var"), [state, Literal("y"), res_y], line=2)

    # z = y + 1
    res_z = Call(
        Lookup("add"),
        [
            Call(Lookup("get_var"), [state, Literal("y")]),
            Literal(1),
        ],
    )
    state = Call(Lookup("set_var"), [state, Literal("z"), res_z], line=2)

    # f = open("some_path")
    res_f = Call(
        Call(Lookup("get_var"), [state, Literal("y")]),
        [Literal("some_path")],
        line=4,
    )
    state = Call(Lookup("set_var"), [state, Literal("f"), res_f], line=2)

    # f.write(bytes([y]))
    f_write = Call(
        Lookup("getattr"),
        [Call(Lookup("get_var"), [state, Literal("f")]), Literal("write")],
        line=5,
    )
    bytes_ = Call(
        Lookup("bytes"),
        [
            Call(
                Lookup("l_list"),
                [Call(Lookup("get_var"), [state, Literal("y")])],
            )
        ],
        line=5,
    )
    f_write_bytes = Call(f_write, [bytes_], line=5)
    state_and_res = Call(Lookup("with_state"), [state, f_write_bytes])
    state = Call(Lookup("getitem"), [state_and_res, Literal(0)])
    # import lineapy
    lineapy = Call(Lookup("l_import"), [Literal("lineapy")], line=6)
    state_and_res = Call(Lookup("with_state"), [state, lineapy])
    state = Call(Lookup("getitem"), [state_and_res, Literal(0)])
    # lineapy.save(lineapy.file_system, "fs")
    save = Call(
        Lookup("getattr"),
        [
            Call(Lookup("get_var"), [state, Literal("lineapy")]),
            Literal("save"),
        ],
        line=7,
    )
    fs = Call(
        Lookup("getattr"),
        [
            Call(Lookup("get_var"), [state, Literal("lineapy")]),
            Literal("file_system"),
        ],
        line=7,
    )
    # TODO: Thread state through all the getattrs? and through the call?
    save_fs = Call(save, [fs, Literal("fs")], line=7)

    return state


```

##

## Background

Guido's post on https://gvanrossum.github.io/formal/informal.html

> Think of Python execution as a combination of calculations (computing a value) and actions (having side effects).
>
> The part about computing values is relatively straightforward – e.g. we compute the value of a + b by first computing the values of a and b to serve as the operands, and then invoking some operation ADD(a, b) on these.
>
> Actions have side effects on carefully defined state. The state is divided into interpreter state, module state, frame state, and so on. Most state is stored in some namespace, which has the semantics of a Python dictionary with string keys (though most methods aren’t needed – we mostly just need **getitem**, **setitem** and **delitem**).
>
> The compiler plays an important role. It translates Python code into operations that are defined in the formal semantics. It also analyzes variable scopes.

Scopes:

https://gvanrossum.github.io/formal/scopesblog.html

> Anyway, below I will sketch a few classes that can model Python scopes. But first I need to get something fundamental out of the way: there’s a difference between scopes and namespaces.
>
> - A scope is a compile time concept, referring to a region of the source code. (The term is sometimes also used to refer to the lifetime of a variable, but in Python that’s a totally separate concept, and I will not dwell on it here.) When the compiler looks something up in a scope, it is essentially looking through a section of the source code (for example, a function body). In practice the compiler doesn’t literally search the text of the source code, but an AST (Abstract Syntax Tree).
> - A namespace is a runtime concept, you can think of it as a dictionary mapping variable names to values (objects). When the intepreter looks something up in a namespace, it is essentially looking for a key in a dictionary. Function namespaces are implemented without using an actual dictionary, but this is an implementation detail. In fact, that other namespaces are implemented using dictionaries is also an implementation detail. For the description of formal semantics, we don’t care about these implementation details – we just use the term namespace.
>
> When compiling source code, the compiler uses the scope of a variable to decide what kind of code to generate for the interpreter to look up that variable’s value or to store a value into it. This generated code refers to one or more namespaces, never to scopes (which don’t exist at runtime).

```

```
