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


