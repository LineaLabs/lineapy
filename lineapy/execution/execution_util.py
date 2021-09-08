from lineapy.data.types import Node


def get_segment_from_code(code: str, node: Node) -> str:
    lines = code.split("\n")[node.lineno - 1 : node.end_lineno]

    lines[0] = lines[0][node.col_offset :]
    lines[len(lines) - 1] = lines[len(lines) - 1][: node.end_col_offset]

    return "\n".join(lines)
