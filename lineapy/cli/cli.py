import click
from lineapy.transformer.transformer import Transformer

"""
We are using click because our package will likely already have a dependency on flask and it's fairly well-starred.
"""

import click


@click.command()
@click.option("--mode", default="dev", help="Either dev or production mode")
@click.argument("file_name")
def linea_cli(mode, file_name):
    transformer = Transformer()
    try:
        f = open("file.txt", "r").readlines()
        lines = f
        new_code = transformer.transform(lines, one_shot=True)
        exec(new_code)
    except IOError:
        print("Error: File does not appear to exist.")


if __name__ == "__main__":
    linea_cli()
