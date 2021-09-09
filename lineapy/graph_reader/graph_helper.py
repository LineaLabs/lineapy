from lineapy.data.types import ArgumentNode

"""
Different from graph_utl to avoid circular dep
"""

# this is used for sorting positional args
MAX_ARG_POSITION = 1000


def get_arg_position(x: ArgumentNode):
    if x.positional_order is not None:
        return x.positional_order
    else:
        return MAX_ARG_POSITION
