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

1. Reading globals: *runtime analysis* We use a custom object for `globals()` so that we can detect whenever an object is read from it.
2. Modifying globals: *worst case assumption* We assume that all mutable variables that are read are modified.
3. Adding globals: *runtime analysis* We compare the `globals()` before and after the execution to see if any new keys were added or if any of the values have "changed"
   (checking based on object identity, not object value).
4. Views of globals: *worst case assumption* We assume all mutable variables that were passed in and all that were added now are views of one another.
5. Side effects: *best case assumption* We assume no side effects were caused in the function.

## Problems with current behavior

Obviously, the worst and best case assumption are problematic. In the worst case assumption, we will end up including pieces we don't need in the slice. Whereas in the best case assumption, we remove pieces that are actually needed.

The runtime analysis is actually also problematic, for a different reason. We often don't want to know "what variables were modified during this execution" but a broader question of "what variables *could* be modified when we run this code in this context?" This comes up if we have behavior that is non deterministic or depends on some external state. We want to model all possibles outcomes, not only those that occur. 


## Example problems

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
