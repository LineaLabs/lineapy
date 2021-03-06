#!/usr/bin/env python
"""
Pretty prints the AST of some Python code you pass in from the CLI
"""

import ast
import dis

import click
from astpretty import pprint


@click.command()
@click.argument("code")
def linea_cli(code):

    ast_ = ast.parse(code)
    print("*** AST ***")
    pprint(ast_)
    print("\n*** TRACER ***")
    # print(astor.to_source(NodeTransformer("dummy").visit(ast_)))
    print("\n*** Bytecoce ***")
    dis.dis(code)


if __name__ == "__main__":
    linea_cli()
