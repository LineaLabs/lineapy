Author: Saul
Reviewer: Yifan
Date: February 15, 2022

# Black Box Analysis RFC

## Background

We currently support Python control flow, function definitions, and class definition as "black boxes". This means we save the source code as a
node in the graph and call `exec` on it to execute it.

This "works" in that we can treat of these construct as one node and chose to include it in our slice or not include it in our slice. We cannot slice inside of it,
but that issues is not the focus of this RFC.

Instead, this RFC is about how we can more accurately analyze the contents of the black boxes.

We need to analyze them, in order to understand:

1. What global variables are read from in this black box?
2. What global variables are modified in this black box?
3. What global variables are added or overwritten in this black box?
4. Are there any views added between any of the previous global variables and the new ones added?
5. Are there any side effects that are called in the black box, like writing to the filesystem?

## Current behavior

We are currently attempting to answer those questions by looking at the runtime behavior, or either assuming the best or worst case, in the following ways:

1. Reading globals: _runtime analysis_ We use a custom object for `globals()` so that we can detect whenever an object is read from it.
2. Modifying globals: _worst case assumption_ We assume that all mutable variables that are read are modified.
3. Adding globals: _runtime analysis_ We compare the `globals()` before and after the execution to see if any new keys were added or if any of the values have "changed"
   (checking based on object identity, not object value).
4. Views of globals: _worst case assumption_ We assume all mutable variables that were passed in and all that were added now are views of one another.
5. Side effects: _best case assumption_ We assume no side effects were caused in the function.

## Problems with current behavior

Obviously, the worst and best case assumption are problematic. In the worst case assumption, we will end up including pieces we don't need in the slice. Whereas in the best case assumption, we remove pieces that are actually needed.

The runtime analysis is actually also problematic, for a different reason. We often don't want to know "what variables were modified during this execution" but a broader question of "what variables _could_ be modified when we run this code in this context?" This comes up if we have behavior that is non deterministic or depends on some external state. We want to model all possibles outcomes, not only those that occur.

Before proceeding to how we could solve these problems, lets make them concrete by articulating an example that shows the problem of our current approach with each of the five areas. We also have real world use cases to cover these, but we don't use them here, because they often conflate multiple problems.

### 1. Reading globals

```python
url = "http://"
if not path.exists():
    download(url, path)
```

In this example, we download a file if the path does not exist. Currently, this won't show up as reading the `url` global if the path does exist. So this is a limitation of the current approach of runtime tracing.

### 2. Modified Globals

```python
for row in df:
    print("row", row)
```

In this example, we are iterating through a dataframe and printing out the rows. In our current approach though we assume the worst case, that the variable `df` is modified because it was read. So we will include this for loop in a slice of `df`, when in reality it does not modify it.

### 3. Adding/changing globals

```python
downloaded_file = False
if not path.exists():
    download(url, path)
    downloaded_file = True
```

In this example, the global variable `downloaded_file` is only set if the file has not already been downloaded. If it has, then we won't know that this block could influence that value. So if we sliced on it, it would not include this block.

### 4. Views of globals

```python
train_data = []
test_data = []
for i in range(10):
    train_data.append(get_train(i))
    test_data.append(get_test(i))
test_data.append(10)
```

In this loop, we load both the `train_data` and `test_data`, so we assume that they are now views of one another. Then we append to the `test_data`, so now if we slice on the `train_data` we will include this append, when we shouldn't be including it.

### 5. Side effects

```python
with TempFile() as t:
    t.write(x)
```

If we slice this on the filesystem, we won't know this block writes to it, so we won't include it, because of our best case assumptiont that blocks don't write to the file system.

## Possible Solutions

Our current way we solve these problems in the non black box analysis is a mix of runtime tracing (e.g. calling functions and observing their results) and static time analysis (analyzing the AST to determine when a variable is defined or accessed).

When we call functions, we also look them up in our manually defined annotations table, to see if calling them will do things like mutate an arg, touch the filesystem, or add a view between the argument and return value.

This table of annotations has the information we need to answer the questions above, about if a variable is mutated or a side is triggered. The answer to these questions for the whole black box is formed from some composition of the answers for all the functions called within the black box. But currently, we don't know all the functions that are called within the black box.

There are two main route we can go down to determine them. The first is adding additional **runtime tracking** to understand what functions are called. The second is to add more **static analysis** to see what functions _could_ be called given some external state (whether a file exists or not).

**Runtime tracking** could help us better resolve the problems where we currently just make an assumption (2, 4, and 5).
It wouldn't help us resolve the issues that already use runtime analysis, because we wouldn't know of paths the program didn't go down (1, and 3).

**Static analysis** could help us accurately answer all of our questions, but at the cost of having to re-implement and understand more of Python's behavior. At the limit, this means coming up with a formal semantics for Python (something that [even the creator of Python said
would take more effort then he could put into it](https://github.com/faster-cpython/ideas/issues/208#issuecomment-1039728796)).

One other option is to do a mix, where we evaluate at runtime different branches that might execute, passing in dummy values that don't actually do anything but let us thread through the interpreter to gain information into whats happening. This was actually similar to the first implementation of lineapy that I wrote! Unfortunately, one consequence of this is that if there are external side effects on branches
they will be run, and could disrupt the users environment. Other systems that take this approach (pytorch, jax) greatly constrain the functionality inside of the branches to manage these problems. We don't have that luxury and I think silently executing stateful code that wouldn't normally be executed is one of the worst UX experiences we could have for the user! Much worse then producing a slice that is innacurate.

---

Initially, I was leaning toward the **static analysis** path, since it is really the long term solution here (most robust, most flexible). However, now that I have wrote it all up, I am wondering if simply doing more extensive runtime tracking would be the fastest path to hit 80% of our use case. It wouldn't cover things like the if statement depending on the state of the filesystem. But that only come up once in my testing so far. What was much more common was unconditional execute of code that had side effects or mutations.

If we did go down that route, we could use something like Python's built in `sys.settrace` to "trace" the execution and understand every function that is called. Using that information, we could use our existing machinery to deduce from this what side effects happened.

I have some experience with this approach, using it in the [`python-record-api` project](https://github.com/data-apis/python-record-api) to gather information on how different libraries called libraries like NumPy or Pandas, by recording the types of every call to their APIs.

If we took this approach, we would have to track which globals ended up with which views and such, but we wouldn't have to do any formal analysis of Python or any type analysis. Out of all the examples we saw observing real notebooks, this would fix all of them besides one that was dependent on the current
state of the file system. For this one, we could at least tell users to re-run the notebook on a clean environment, if they want the slice to support that use case.

If we wanted to do runtime analysis, we could instead try to re-use our existing machinery have for the top level statements to do this. However, this would be more work than the `sys.settrace` approach, because it would require diving up the black box into a number of seperate nodes. We don't really care about that for this issue, we just want to know as a whole which variables it accessed and which ones it mutated and the side effects. So it is much less work
to not have to change our current behavior to account for things like for loops, and instead just use the `sys.settrace` approach.

One con for this approach is that it will significantly slow down the execution for very large for loops. We could have some sort of heuristic, however, if we see cases where this comes up, to stop tracing in loops after a certain point. This would not change our design much, so would be straightforward to add after.

## `sys.settrace` solution details

### `settrace` background

`sys.settrace(trace_fn)` is a builtin way to trace Python code execution.

We want to use it to see what functions are called in a black box init.

To give a flavor of how this tracing could function, I put together
a `settrace` logger from ["The unreasonable effectiveness of sys.settrace (and sys.setprofile)
CPython"](https://explog.in/notes/settrace.html) and augmented it by also printing items off the top
of the bytecode stack using the code from [this gist](https://gist.github.com/crusaderky/cf0575cfeeee8faa1bb1b3480bc4a87a).

I also changed it to only include the tracing when the code object is the same one we are evaulating.
If we don't have this, then it will continue tracing _inside_ functions that are called from our black box, which is not what we want.

The updated file looks like this:

```python
import sys
from pathlib import Path

import opcode


def clean_locals(locals: dict) -> dict:
    """
    Returns the locals with the __builtins__
    """
    return {k: v for k, v in locals.items() if k != "__builtins__"}


CURRENT_CODE_OBJECT = None


def show_trace(frame, event, arg):
    code = frame.f_code
    if code != CURRENT_CODE_OBJECT:
        return show_trace
    frame.f_trace_opcodes = True
    offset = frame.f_lasti
    print(f"| {event:10} | {str(arg):>4} |", end=" ")
    print(f"{frame.f_lineno:>4} | {frame.f_lasti:>6} |", end=" ")
    print(
        f"{opcode.opname[code.co_code[offset]]:<18} | {str(clean_locals(frame.f_locals)):<35} |"
    )
    return show_trace


def trace_exec(globals, code):
    """
    Trace some code as would would with an exec block
    """
    global CURRENT_CODE_OBJECT
    header = f"| {'event':10} | {'arg':>4} | line | offset | {'opcode':^18} | {'locals':^35} |"
    print(header)
    CURRENT_CODE_OBJECT = compile(code, "", "exec")
    sys.settrace(show_trace)
    exec(CURRENT_CODE_OBJECT, globals)
    sys.settrace(None)
```

Now we can use `trace_exec` function to try out some of our examples we listed above, and imagine how we could use their traces
to understand them.

#### Example 1

We can try execing a version of our first example, to see how we could use the results to
determine that it writes to the file system and doesn't modify it's arguments:

```python
def download(*args):
    print("downloading", args)


trace_exec(
    {
        "path": Path("non-existant-path"),
        "url": "some-url",
        "download": download,
    },
    """if not path.exists():
        download(url, path)""",
)
```

This produces this tracing output:

```
| event      | |                                 stack[0] |                                 stack[1] | line | offset |       opcode       |
| call       |                                      None |                                     None |    1 |     -1 | <0>                |
| line       |                                      None |                                     None |    1 |      0 | LOAD_NAME          |
| opcode     |                                      None |                                     None |    1 |      0 | LOAD_NAME          |
| opcode     |                         non-existant-path |                                     None |    1 |      2 | LOAD_METHOD        |
| opcode     |                         non-existant-path | <function Path.exists at 0x7fdbc8073a60> |    1 |      4 | CALL_METHOD        |
| opcode     |                                     False |                                     None |    1 |      6 | POP_JUMP_IF_TRUE   |
| line       |                                      None |                                     None |    2 |      8 | LOAD_NAME          |
| opcode     |                                      None |                                     None |    2 |      8 | LOAD_NAME          |
| opcode     |     <function download at 0x7fdbc80754c0> |                                     None |    2 |     10 | LOAD_NAME          |
| opcode     |                                  some-url |    <function download at 0x7fdbc80754c0> |    2 |     12 | LOAD_NAME          |
| opcode     |                         non-existant-path |                                 some-url |    2 |     14 | CALL_FUNCTION      |
downloading ('some-url', PosixPath('non-existant-path'))
| opcode     |                                      None |                                     None |    2 |     16 | POP_TOP            |
| opcode     |                                      None |                                     None |    2 |     18 | LOAD_CONST         |
| opcode     |                                      None |                                     None |    2 |     20 | RETURN_VALUE       |
| return     |                                      None |                                     None |    2 |     20 | RETURN_VALUE       |
```

For each bytecode instruction, we can see what is being called, the `opcode`, and we can see the top two values on the stack.

On offset 4, we can see the first method is called, `Path.exists` on the path argument. We can pass this to our side effect analysis, to know that `path.exists()` does
not modify the arg.

Then, on offset `14`, we can see the second method is called, `download` on the url and path arguments. We can pass this to our side effect analysis, and if know that `download`
updates the

### Example 4

Let's try the last example, which is writing a tempfile, and see how we can understand
we wrote to the filesystem from that trace:

```python
trace_exec(
    {"tempfile": tempfile},
    """with tempfile.TemporaryFile() as t:
    t.write(b"10")""",
)
```

In the trace, we can see that in offset 16 the `CALL_METHOD` is invoked. We don't actually see the method, since this exists farther up in the stack, but we do see the argument, the self `<_io.BufferedRandom name=4>` and the arg `b'10'`.

Looking at the third item from the top of the stack, we will see it's the `write` method and know this modifies the filesystem.

### Using settrace

Based on these examples, we can see that we have a way to use `settrace` to understand what functions are called in a block of code.

At a high level, this is how we could use that functionality to better analyze the black boxes:

1. Let's assume we have a way to enable tracing for some code, and when it is done, are returning a list of all functions called in that code, with their args and kwargs, as well as return values.
2. The `exec` hapens in the `l_exec_statement` inside of `lineabuiltins`. It's only inside this exec that we want to use this tracing. Once we enable it there, we add the list of
   functions called into the `context`, in a new field.
3. Then, in the Executor, we see once we are done if we have any function calls in the context. If we do, we need to translate those to side effects.

For 1, we have to understand every bytecode operation that triggers a function call, and correctly understand what parts of the stack are neccesary to look at to determine the arguments. One corner case
here is also around iterators which we pass with `*` into the
function. We don't want to iterate through these in the analaysis, since this is a destructive operation. So one a current workaround could be to just assume they are empty and not track their values.

For 3, we have to use the results of the side effects for each function call to come up with a composite side effect for the whole black box.

Generally, we know the Python IDs of all the objects passed in as globals. We can use object IDs to identigy which objects are passed where. So similar to our curreent state processing, but
at the end we only emit the changes to the globals passed in
or any globals that were set or any side effects.

## Ramifications for function tracing

One interesting result of this approach is that we could use it to attempt to infer the side effects inside of a function, based on its contents.

For example, let's say I have a function like this:

```python
def set_item(x, y):
    x[y] = 1
```

Unless we annotate it, we won't know that this function is mutating the `x` arg.
If we used the `set_trace` approach, we could see that a `setitem` is being called on the `x` arg, and infer this from the contents of the function.

In this way, we could limit our own hand annotations to Python functions which are written in C or are performance critical (having settrace enabled during
a function's execution will slow it down). This would allow us to cover a greate percentage of third party libraries that we see.

However, I propose holding off on using this approach more generaly, for a future PR, to minimize the size of this change.
