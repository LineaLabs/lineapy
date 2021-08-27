# Transformer


## Special functions that we need to NOT capture
For `linea.publish(var_name, "optional_description")`, we need to identify what node it points to at runt time.
We have two options, one is to capture the var name and look it up in our ssa table, and the other one is to instrument the variable at run time.
We explored the options, and it seems like the latter is not possible for simple values like ints and lists (and others).
For the former, we could try to grab it at runtime (looking at the call stack), but easier just to have our transformer transform it.

