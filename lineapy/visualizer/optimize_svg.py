"""
Optimizes an SVG file to reduce the size in the notebook.
"""

import subprocess
import tempfile
from pathlib import Path

# https://github.com/scour-project/scour#usage
OPTIONS = [
    "--strip-xml-prolog",
    "--remove-titles",
    "--remove-descriptions",
    "--remove-metadata",
    "--remove-descriptive-elements",
    "--enable-comment-stripping",
    "--no-line-breaks",
    "--enable-id-stripping",
    "--shorten-ids",
    "--create-groups",
]


def optimize_svg(svg: str) -> str:
    # Calls optimize in subprocess to avoid needing to tie ourselves
    # to scours's internal Python API, which is likely less stable and not
    # documented.
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmp_dir = Path(tmpdirname)
        input_path = tmp_dir / "input.svg"
        output_path = tmp_dir / "output.svg"
        input_path.write_text(svg)
        subprocess.run(
            ["scour", "-i", str(input_path), "-o", str(output_path)] + OPTIONS,
            capture_output=True,
            check=True,
        )
        return output_path.read_text()
