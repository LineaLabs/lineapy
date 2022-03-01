Author: Saul

Date: February 18, 2022

Status: Rejected for now/draft

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

## Simple Example

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
fs = Call(
    Lookup("getattr"), [lineapy, Literal("file_system")], implicit=[mutated_fs], line=7
)
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
    return {n.line for n in ancestors(node) if n.line is not None}


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


def save_artifact(state, name, value):
    new_artifacts = {**state.artifacts, name: value}
    return replace(state, artifacts=new_artifacts)


def setitems(d, *keys_and_values):
    return {**d, **dict(keys_and_values)}
```

We can think about our program as a function that takes in a State and returns a new State, like this:

```python
def my_program(state):
    # x = 100
    state = Call(Lookup("set_var"), [state, Literal("x"), Literal(100)], line=1)

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
    state_and_fs = Call(
        Lookup("with_state"),
        [
            state,
            Call(
                Lookup("getattr"),
                [
                    Call(Lookup("get_var"), [state, Literal("lineapy")]),
                    Literal("file_system"),
                ],
                line=7,
            ),
        ],
    )
    state = Call(Lookup("getitem"), [state_and_fs, Literal(0)])
    fs = Call(Lookup("getitem"), [state_and_fs, Literal(1)])

    state_and_artifact = Call(
        Lookup("with_state"), [state, Call(save, [fs, Literal("fs")], line=7)]
    )
    state = Call(Lookup("getitem"), [state_and_artifact, Literal(0)])

    return state
```

This does look quite a bit more complicated than the previous implementation,
because we are threading the state through everything that needs it.

Before proceeding, let's rewrite it again in a more readable form, where instead
of creating the `Node`s directly, we use function application to create them.

We assume any local we use that is not defined translate to a `Lookup`. We also add
an extra `line` function to add the proper line mapping to nodes:

```python
def my_program(state):
    # x = 100
    state = set_var(state, "x", line(1, 100))

    # y = x + 1
    state = set_var(state, "y", line(2, add(get_var(state, "x"), 1)))

    # z = y + 1
    state = set_var(state, "z", line(3, add(get_var(state, "y"), 1)))

    # f = open("some_path")
    state = set_var(state, "f", line(4, get_var(state, "open")("some_path")))

    # f.write(bytes([y]))
    f_write = getattr(get_var(state, "f"), "write")
    bytes_ = bytes(l_list(get_var(state, "y")))
    f_write_bytes = line(5, f_write(bytes_))
    state = getitem(with_state(state, f_write_bytes), 0)

    # import lineapy
    state = line(6, getitem(with_state(state, l_import("lineapy")), 0))

    # lineapy.save(lineapy.file_system, "fs")
    save = getattr(get_var(state, "lineapy"), "save")
    state_and_fs = with_state(state, getattr(get_var(state, "lineapy"), "file_system"))
    state = getitem(state_and_fs, 0)
    fs = getitem(state_and_fs, 1)

    state_and_artifact = with_state(state, line(7, save(fs, "fs")))
    state = getitem(state_and_artifact, 0)

    return state
```

This format is atleast a bit more readable, but is equivalent to the previous.

After evaluating the program, we want to know what all the artifacts are. What their values are and
what nodes are needed to create them. One way we can do that is to define certain patterns which
correspond to replacements to make on the graph. By continually evaluating these
replacements whenever they match, we end up with a normalized version of the graph.

For now, we emit writing the explicit replacements, that we would need, but
can add thse if more detail is needed. After the replacements, we should end
up with a graph like this:

```python
def my_program_transformed(state):
    x = line(1, 100)
    y = line(2, add(x, 1))
    z = line(3, add(z, 1))
    f = line(4, get_var(state, "open")("some_path"))
    f_write = line(5, getattr(f, "write")(bytes(l_list(y))))
    fs = modifies_fs(
        getattr(state, "fs"),
        f_write,
    )
    return State(
        namespace=setitems(getattr(state, "namespace"), "x", x, "y", y, "z", z, "f", f),
        modules=getattr(state, "modules"),
        fs=fs,
        artifacts=setitems(getattr(state, "artifacts"), "fs", fs),
    )
```

From this representation, we can look at the `fs` artifact and see all it's ancestors
to see what lines are needed to recreate it.

This way of evaluating what lines are required to re-execute a certain artifact
differs from our current implementation by moving much of the functionality that
we have in the tracer and executor into a graph replacement framework.

## If Control Flow Example

Next, we will see how this help us deal with control flow in a consistant manner.

Let's say we start with this program:

```python
if cond:
    a = b
    c = d
else:
    a = b + 1
    c = d + 1
```

and we want to slice on `c`. We should end up with this slice:

```python
if cond:
    c = d
else:
    c = d + 1
```

To create a graph for this, we start by adding an `if_` ternary operator:

```python
def if_(cond, true_branch, false_branch):
    return true_branch if cond else false_branch
```

Since we can now treat our program state as a value, we can use this functional
operator to create a graph for our program:

```python
line_2_state = set_var(state, "a", line(2, get_var(state, "b")))
line_3_state = set_var(line_2_state, "c", line(3, get_var(line_2_state, "d")))

line_5_state = set_var(state, "a", line(5, add(get_var(state, "b")), 1))
line_6_state = set_var(line_6_state, "c", line(6, get_var(line_6_state, "d")))


state = if_(
    line(1, get_var(state, "cond")),
    line_3_state,
    line_6_state,
)
```

Running our transforms to deal with `get_var` and `set_var` we end up with this resulting graph:

```python
a_true = line(2, get_var(state, "b"))
c_true = line(3, get_var(state, "d"))

a_false = line(5, add(get_var(state, "b"), 1))
c_false = line(6, add(get_var(state, "d"), 1))

state = if_(
    line(1, get_var(state, "cond")),
    replace(
        state,
        namespace=setitems(
            getattr(state, "namespace"),
            "a",
            a_true,
            "c",
            c_true,
        ),
    ),
    replace(
        state,
        namespace=setitems(
            getattr(state, "namespace"),
            "a",
            a_false_,
            "c",
            c_false_,
        ),
    ),
)
```

Now, we can use this property that `if_(cond, f(x), f(y)) == f(if_(cond, x, y))` to
move the if statement inside the state:

```python
a_true = line(2, get_var(state, "b"))
c_true = line(3, get_var(state, "d"))

a_false = line(5, add(get_var(state, "b"), 1))
c_false = line(6, add(get_var(state, "d"), 1))

state = replace(
    state,
    namespace=if_(
        line(1, get_var(state, "cond")),
        setitems(
            getattr(state, "namespace"),
            "a",
            a_true,
            "c",
            c_true,
        ),
        setitems(
            getattr(state, "namespace"),
            "a",
            a_false_,
            "c",
            c_false_,
        ),
    ),
)
```

Since the setitems is also mostly the same in both branches, we can move
the `if_` into the assignment statements:

```python
cond = line(1, get_var(state, "cond"))

a_true = line(2, get_var(state, "b"))
c_true = line(3, get_var(state, "d"))

a_false = line(5, add(get_var(state, "b"), 1))
c_false = line(6, add(get_var(state, "d"), 1))

state = replace(
    state,
    namespace=setitems(
        getattr(state, "namespace"),
        "a",
        if_(cond, a_true, a_false),
        "c",
        if_(cond, b_true, b_false),
    ),
)
```

From there, if we get the `c` variable, we see that it will not include the
value for the a definitions.

## While control flow example

We can also show how this could work with a `while` loop, which any for loop can
be transformed into.

Let's say we have this code:

```python
s = 0
i = 0
while i < 10:
    i += 1
    print("Loop", i)
    s += xs[i]
```

We want to slice it to remove the `print` statement. We can assume this print statement changes our state, by adding to some `stdout` variable, or something like that.

Alternatively, we also might want to slice just for the standard out, and remove the actual summing!

To transform this, let's add a functional `while_` which keeps calling
a function on data to transform it, till the stopping condition is reached:

```python
T = TypeVar("T")


def while_(value: T, cond: Callable[[T], bool], body: Callable[[T], T]) -> T:
    """
    Keeps calling the `body` function on `value` until the cond returns false.
    """
    while cond(value):
        value = body(value)
    return value
```

```python
state = line(1, set_var(state, "s", 0))
state = line(2, set_var(state, "i", 0))


def cond(state):
    return line(3, less(get_var(state, "i"), 10))


def body(state):
    state = set_var(state, "i", line(4, add(get_var(state, "i"), 1)))
    state = with_state(state, line(5, print_("Loop", get_var(state, "i"))))[0]
    return set_var(
        state,
        "s",
        line(
            6,
            add(
                get_var(state, "s"),
                getitem(get_var(state, "xs"), get_var(state, "i")),
            ),
        ),
    )


state = while_(state, cond, loop)
```

Now, similar to the `if` example, let's first normalize with respect to the variables
and other state modifications, before trying to look in the loop:

```python
state = replace(
    state,
    namespace=setitems(
        getattr(state, "namespace"),
        "s",
        line(
            1,
            0,
        ),
        "i",
        line(
            2,
            0,
        ),
    ),
)


def cond(state):
    return line(3, less(get_var(state, "i"), 10))


def body(state):
    new_i = line(
        4,
        add(
            get_var(state, "i"),
            1,
        ),
    )
    return replace(
        state,
        namespace=setitems(
            getattr(state, "namespace"),
            "i",
            new_i,
            "s",
            line(
                6,
                add(
                    get_var(state, "s"),
                    getitem(get_var(state, "xs"), new_i),
                ),
            ),
        ),
        stdout=modify_stdout(
            getattr(state, "stdout"),
            print_("Loop", new_i),
        ),
    )


state = while_(state, cond, loop)
```

Finally, we have to create a transformation so that the while loop moves
inside of the state, both for the stdout and for the namespaces. At this point, we can see which nodes are
required to produce the stdout side effects as opposed to those needed to updates the namespace variables:

```python
# We split the while loop into two while loops, one which updates the state
# and one which updates the stdout, so that we can slice on each

# The inital state for the namespace loop just has the namesapce
namespace_init = setitems(
    getattr(state, "namespace"),
    "s",
    line(
        1,
        0,
    ),
    "i",
    line(
        2,
        0,
    ),
)

# The namespace conditional gets the "i" variable from the namesapce
def namespace_cond(state):
    return line(3, less(getitem(state, "i"), 10))


# The namespace body updates only the namespace
def namespace_body(state):
    new_i = line(
        4,
        add(
            get_var(state, "i"),
            1,
        ),
    )
    return setitems(
        getattr(state, "namespace"),
        "i",
        new_i,
        "s",
        line(
            6,
            add(
                get_var(state, "s"),
                getitem(get_var(state, "xs"), new_i),
            ),
        ),
    )


namespace = (while_(namespace_init, namespace_cond, namespace_body),)


# The stdout only needs the `i` variable in the namespace, not the `s`

stdout_init = reaplce(
    state,
    namespace=setitems(
        getattr(state, "namespace"),
        "i",
        line(
            2,
            0,
        ),
    ),
)

# The stdout conditional gets the "i" variable from the namespace from the state
def namespace_cond(state):
    return line(3, less(get_var(state, "i"), 10))


# The stdout body updates the `i` as well as the `stdout`.
def stdout_body(state):
    new_i = line(
        4,
        add(
            get_var(state, "i"),
            1,
        ),
    )
    return replace(
        state,
        namespace=setitems(
            getattr(state, "namespace"),
            "i",
            new_i,
        ),
        stdout=modify_stdout(
            getattr(state, "stdout"),
            print_("Loop", new_i),
        ),
    )


# We compute the stdout loop with includes the full state, then get the
# stdout
stdout = getattr(
    while_(init_stdout_state, cond, stdout_body),
    "stdout",
)

state = replace(
    state,
    namespace=namespace,
    stdout=stdout,
)
```

It is unclear to me at this time though how we can do this type of transformation in a rigorous manner,
so I am unclear in general if there are ways we can use graph replacement to normalize the graph in some manner, to create
a form that is ameanable to program slicing.

---

Now this is really turning into more of an exploration than an RFC, but I wanted to share a few others thoughts I had on the problem from reading a couple of recent papers this weekend.

To re-orient, where we left is that we were having trouble figuring out to how to take a while loop with updates both the local namespace and to the IO (stdout),
and sepearete those changes, so that we can see which parts of the while loop touch IO and which touch the namespace.

The strategy is to re-formulate the imperative while loop in a functional form.

The paper ["Modular, Compositional, and Executable Formal Semantics for LLVM IR"](https://perso.ens-lyon.fr/yannick.zakowski/papers/vellvm_design.pdf), published last year, ends up solving a similar problem. They are trying to come up with a formal semantics for LLVM IR in order to prove the correctness of certain IR level transformations. At the core of their reasoning, is the ability to understand whether two LLVM IRs are semantically equivalent. This is similar to our end goal, of being able to understand if removing a line from a file will result in the same semantics, with respect to certain behaviors.

They use the technique of ["Interaction Trees"](https://arxiv.org/abs/1906.00046), which they use to represent in a (monadic) functional form the state transitions of LLVM. Like in our case, they have events which impact the environment in different way, such as writing/reading from global state, or causing IO. The ITrees interface lets them decompose these effects:

> Importantly, since ITrees themselves form a monad, we do not have to interpret the whole interface at once: for instance, the state monad transformer StateT 𝑆 allows us to interpret the state events StE𝑆 of an ITree of type itree(E ⊕ StES ⊕ F) A into StateT 𝑆 (itree (𝐸 ⊕ 𝐹 ) ) AÐthe state events are interpreted in isolation.

So although we are not interested in a formally proving the correctness of our understanding of Python, it seems possible that we could gain by trying to use similar tools to those being developed in the formal theorum proving world, to model and reason about imperative stateful language behavior.

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
