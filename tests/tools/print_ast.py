#!/usr/bin/env python
"""
Pretty prints the AST of some Python code you pass in from the CLI
"""

from astpretty import pprint
import ast
import click
from lineapy.transformer.node_transformer import NodeTransformer
import astor


@click.command()
@click.argument("code")
def linea_cli(code):
    ast_ = ast.parse(code)
    print("*** AST ***")
    pprint(ast_)
    print("\n*** TRACER ***")
    print(astor.to_source(NodeTransformer("dummy").visit(ast_)))


if __name__ == "__main__":
    linea_cli()
