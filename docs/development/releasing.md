# Releasing

Maintainers publish releases from `main`. Use a **bare version tag**, such as
`2.2.0`, without a `v` prefix.

## Prepare the release

1. Merge the accepted pull requests. Fixes for the current release go into
   `main`, and work for the next minor release goes into `feature`. For a minor
   release, merge the completed `feature` branch into `main`.
2. Confirm CI passes. Run the documentation build and rehearse any affected
   migration paths.
3. In the release pull request, set the release date of the entry in
   [Release notes](../releases.md), keep only shipped changes in it, and verify
   its compatibility and upgrade guidance. Add the release to the README
   compatibility matrix.
4. Update `[project].version` in `pyproject.toml`. The plugin reads its version
   from installed package metadata, so there is no separate version constant
   to update in `netbox_acls/__init__.py`.
5. Build the package, validate its metadata, and check that the wheel
   contains the templates and migrations:

    ```sh
    rm -rf dist/
    python -m build
    python -m twine check --strict dist/*
    python -m zipfile -l dist/*.whl
    ```

    Install the `build` and `twine` tools first if your release environment
    lacks them.

## Publish and verify

Create the GitHub release from the prepared `main` commit with the bare version
tag. Publishing it triggers `.github/workflows/python-publish.yml`, which builds
the package and publishes it to PyPI.

Check the workflow result, the package version on
[PyPI](https://pypi.org/project/netbox-acls/), and installation in a clean test
deployment. Verify migrations, plugin startup, and the final documentation
links.

The Docs workflow publishes the site on pushes to `main`, independently of
the PyPI release workflow. Deployment requires
the repository's Pages source to be **GitHub Actions**, as the header of
`.github/workflows/docs.yml` notes. Finalize release wording before merging the
release into `main`.
