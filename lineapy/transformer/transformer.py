class Transformer:
    """
    The reason why we have the transformer and the instrumentation separate is that we need runtime information when creating the nodes.
    If we created the instrumentation statically, then the node level information would be lost.
    """
