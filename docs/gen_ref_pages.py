"""Generate the code reference pages."""

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

SKIP_DIRS = ["_alembic"]

for path in sorted(Path("..", "lineapy").rglob("*.py")):
    if not set(path.parts).isdisjoint(SKIP_DIRS):
        continue

    module_path = path.relative_to("..").with_suffix("")
    doc_path = path.relative_to("..").with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = list(module_path.parts)

    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")
    elif parts[-1] == "__main__":
        continue

    nav[parts] = doc_path.as_posix()

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        identifier = ".".join(parts)
        print("::: " + identifier, file=fd)

with mkdocs_gen_files.open("reference/nav.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
