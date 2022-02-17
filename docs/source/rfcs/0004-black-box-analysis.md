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

If we did go down that route, we could use something like Python's built in `sys.set_trace` to "trace" the execution and understand every function that is called. Using that information, we could use our existing machinery to deduce from this what side effects happened.

I have some experience with this approach, using it in the [`python-record-api` project](https://github.com/data-apis/python-record-api) to gather information on how different libraries called libraries like NumPy or Pandas, by recording the types of every call to their APIs.

If we took this approach, we would have to track which globals ended up with which views and such, but we wouldn't have to do any formal analysis of Python or any type analysis.
