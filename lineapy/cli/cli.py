from lineapy.utils import report_error_to_user
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
        lines = open(file_name, "r").readlines()
        original_code = "".join(lines)
        new_code = transformer.transform(original_code, file_name, one_shot=True)
        exec(new_code)
    except IOError:
        report_error_to_user("Error: File does not appear to exist.")


if __name__ == "__main__":
    linea_cli()
