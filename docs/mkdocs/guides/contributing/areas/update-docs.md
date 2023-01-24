# Updating Project Documentation

!!! info

    LineaPy's project documentation is built with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
    and deployed with [Netlify](https://www.netlify.com/).

## Pre-requisites

Ensure that you have the requirements needed to build docs installed. 
`pip install -r requirements.txt` from the `docs/` subdirectory.

## Instructions

To add or update project documentation, take the following steps:

1. Add or update a Markdown file in `docs/` folder. Check existing files or
this [reference](https://squidfunk.github.io/mkdocs-material/reference/) for available features for technical writing.

2. Update `mkdocs.yml` file's `nav` section to surface the new/updated page. For instance,
to add a new page under `Concepts` section:

    ```yaml title="mkdocs.yml"
    nav:
    ...
      - Concepts:
        - Artifact: concepts/artifact.md
        - Artifact Store: concepts/artifact-store.md
        ...
        - New Page Title: concepts/new-page.md
    ```

3. Preview the update by starting a built-in dev-server:

    ```bash
    # Run from docs/
    mkdocs serve
    ```

4. Once satisfied with the change(s), open a PR.

## Updating API Reference

For code documentation, first add or update docstrings using the
[NumPy style](https://numpydoc.readthedocs.io/en/latest/format.html).

!!! warning

    Docstrings with a different style (e.g., Google) may not render properly.

Then, run:

```bash
# Run from docs/
python gen_ref_pages.py
```

This will automatically generate or update Markdown file(s) for API reference.

Finally, open a PR with the changes.

## Publishing Updates

!!! note

    To effectively manage different versions of documentation, the project limits publication capacity
    to a few select members. Please contact the LineaPy core team on [Slack](../../support.md#community)
    for relevant questions or requests.

LineaPy keeps a separate branch for each version of the package (e.g., `v0.2.x`).
This means each version’s documentation should be built from its own branch,
which makes sense because the `main` branch may include changes that are not yet
ready for public release and use.

Accordingly, to build/update documentation for a particular version, run the following
***on the corresponding version branch*** (e.g., `v0.2.x`):

=== "Update Existing Version"

    ```bash
    # Run from docs/
    mike deploy --push <version_number>
    ```

=== "Create New Version"

    ```bash
    # Run from docs/
    mike deploy --push --update-aliases <version_number> latest
    ```

where `<version_number>` is formatted `<major>.<minor>` (e.g., `0.2`) as defined in
[semantic versioning](https://semver.org/#summary).

!!! info

    LineaPy uses [`mike`](https://github.com/jimporter/mike) to build and maintain versioned documentation.
    Specifically, it compiles different versions of the documentation into static files and commits them
    to the `gh-pages` branch, which is continuously deployed by [Netlify](https://www.netlify.com/).
