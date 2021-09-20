#!/usr/bin/env python 
"""
Pretty prints the AST of some Python code you pass in from the CLI
"""

from astpretty import pprint
import ast
import click




@click.command()
@click.argument("code")
def linea_cli(code):
    pprint(ast.parse(code))


if __name__ == "__main__":
    linea_cli()
