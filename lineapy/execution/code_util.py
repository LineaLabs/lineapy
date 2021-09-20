from lineapy.data.types import Node


def get_segment_from_code(code: str, node: Node) -> str:
    if node.lineno is node.end_lineno:
        return code.split("\n")[node.lineno - 1][
            node.col_offset : node.end_col_offset
        ]
    else:
        lines = code.split("\n")[node.lineno - 1 : node.end_lineno]
        lines[0] = lines[0][node.col_offset :]
        lines[-1] = lines[-1][: node.end_col_offset]
        return "\n".join(lines)


def max_col_of_code(code: str) -> int:
    lines = code.split("\n")
    max_col = 0
    for i in lines:
        if len(i) > max_col:
            max_col = len(i)

    return max_col


def replace_slice_of_code(
    code: str, new_code: str, start: int, end: int
) -> str:
    return code[:start] + new_code + code[end:]


def add_node_to_code(current_code: str, session_code: str, node: Node) -> str:
    segment = get_segment_from_code(session_code, node)
    segment_lines = segment.split("\n")
    lines = current_code.split("\n")

    # replace empty space
    if node.lineno == node.end_lineno:
        # if it's only a single line to be inserted
        lines[node.lineno - 1] = replace_slice_of_code(
            lines[node.lineno - 1],
            segment,
            node.col_offset,
            node.end_col_offset,
        )
    else:
        # if multiple lines need insertion
        lines[node.lineno - 1] = replace_slice_of_code(
            lines[node.lineno - 1],
            segment_lines[0],
            node.col_offset,
            len(lines[node.lineno - 1]),
        )

        lines[node.end_lineno - 1] = replace_slice_of_code(
            lines[node.end_lineno - 1],
            segment_lines[-1],
            0,
            node.end_col_offset,
        )

        for i in range(1, len(segment_lines) - 1):
            lines[node.lineno - 1 + i] = segment_lines[i]

    return "\n".join(lines)
