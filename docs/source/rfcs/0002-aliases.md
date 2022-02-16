Author: Saul
Reviewer: Yifan
Date: February 8, 2022

# Alias RFC

Currently this code will break in linea:

```python
x = 100
y = x
lineapy.save(y, "y")
```

The slice will not include the `y = x` line, beause we don't create a node for aliases. And since we don't create a node for it, it won't know to keep that
line when looking at all the nodes that are required.

## Solution

I propose a very simple/hacky solution. When we are traversing the AST, if we ever see an assign of the `NAME = NAME`, we wrap it in a `l_alias` function call.
`l_alias` is simply a no-op identity, which will have a view between its arg and the return value.
That way, when the graph is generated, there will be a node which refers to the line.

### Other solutions

One reason this bug comes about is because we don't store anything about variable assignment in the graph. By the time we create the graph, we have erased the variables.
This works in most cases, because we don't actually care about the variable names for re-execution.

So alternatively we could try to move the variable analysis into the graph that we save. We could treat variable as mutable pointers, and create a "mutate node"
whenever they change. For example,

However, this is a larger change, so until other issues with variables come up, it seems simpler to stick with the `l_alias` noop call, which adds minimal complications,
besides a special case in the AST parser.
