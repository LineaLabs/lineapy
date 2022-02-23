# Alias RFC

Currently this code will break in linea:

```python
x = 100
y = x
lineapy.save(y, "y")
```

We can see this in the graph that is created as well. There is no node created for the alias line, since we by the time we get to the graph, all of the scoping has been erased:

<img width="1511" alt="Screen Shot 2022-02-23 at 1 02 58 PM" src="https://user-images.githubusercontent.com/1186124/155382719-b876ec29-fe3f-473f-9c7d-cb96dc8a98c1.png">


This pattern might seem silly, but it did show up in [a Tensorflow tutorial](https://www.tensorflow.org/tutorials/images/transfer_learning_with_hub#download_the_classifier).

The slice will not include the `y = x` line, beause we don't create a node for aliases. And since we don't create a node for it, it won't know to keep that
line when looking at all the nodes that are required.

## Solution

I propose a very simple/hacky solution. When we are traversing the AST, if we ever see an assign of the `NAME = NAME`, we wrap it in a `l_alias` function call.
`l_alias` is simply a no-op identity, which will have a view between its arg and the return value.
That way, when the graph is generated, there will be a node which refers to the line.


Concretely, this would entail:

1. Adding a `l_alias` noop function that takes one arg and returns it to `lineabuiltins.py`.
2. Creating an `l_alias` node in the `node_transform.py` logic to handle assignment, whenever the assignments target is a simple name and its value is also a simple name.

### Other solutions

One reason this bug comes about is because we don't store anything about variable assignment in the graph. By the time we create the graph, we have erased the variables.
This works in most cases, because we don't actually care about the variable names for re-execution.

So alternatively we could try to move the variable analysis into the graph that we save. We could treat variable as mutable pointers, and create a "mutate node"
whenever they change. For example, 

However, this is a larger change, so until other issues with variables come up, it seems simpler to stick with the `l_alias` noop call, which adds minimal complications,
besides a special case in the AST parser.
