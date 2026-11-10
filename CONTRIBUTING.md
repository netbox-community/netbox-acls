# Contributing

## How We Work: Issue-First → Assignment → PR

To avoid wasted effort and keep the project coherent, we follow an issue-first
workflow:

1. **Open an issue** first, using the matching issue template.
2. A maintainer **triages** it. If it is viable, the maintainer marks it
   **accepted**.
3. The issue's author or another volunteer **offers to own it** by commenting.
4. A maintainer **assigns** the issue to the owner.
5. The owner opens a **pull request** that resolves the issue.

**Please do not open pull requests without an accepted, assigned issue.**
Unassigned pull requests may be closed to keep the queue focused. Draft pull
requests are welcome **after** an issue is accepted and assigned.

## Reporting Bugs

* First, ensure that you're running the [latest stable version](https://github.com/netbox-community/netbox/releases)
of NetBox or this plugin is at [latest stable version](https://github.com/netbox-community/netbox-acls/releases).
If you're running an older version, it's possible that the bug has already been fixed,
or that your plugin version was not tested with your NetBox version. See the
[compatibility matrix](https://github.com/netbox-community/netbox-acls#compatibility).

* Next, check the GitHub [issues list](https://github.com/netbox-community/netbox-acls/issues)
to see if the bug you've found has already been reported. If you think you may
be experiencing a reported issue that hasn't already been resolved, please
click "add a reaction" in the top right corner of the issue and add a thumbs
up (+1). You might also want to add a comment describing how it's affecting your
installation. This will allow us to prioritize bugs based on how many users are
affected.

* When submitting an issue, please be as descriptive as possible. Be sure to
provide all information requested in the issue template, including:

  * The environment in which NetBox is running
  * The exact steps that can be taken to reproduce the issue
  * Expected and observed behavior
  * Any error messages generated
  * Screenshots (if applicable)

## Feature Requests

* First, check the GitHub [issues list](https://github.com/netbox-community/netbox-acls/issues)
to see if the feature you're requesting is already listed. (Be sure to search
closed issues as well, since some feature requests have been rejected.) If the
feature you'd like to see has already been requested and is open, click "add a
reaction" in the top right corner of the issue and add a thumbs up (+1). This
ensures that the issue has a better chance of receiving attention. Also feel
free to add a comment with any additional justification for the feature.
(However, note that comments with no substance other than a "+1" will be
deleted. Please use GitHub's reactions feature to indicate your support.)

* Good feature requests are very narrowly defined. Be sure to thoroughly
describe the functionality and data model(s) being proposed. The more effort
you put into writing a feature request, the better its chance is of being
implemented. Overly broad feature requests will be closed.

* When submitting a feature request on GitHub, be sure to include all
information requested by the issue template, including:

  * A detailed description of the proposed functionality
  * A use case for the feature: who would use it and what value it would add
    to NetBox
  * A rough description of changes necessary to the database schema (if
    applicable)
  * Any third-party libraries or other resources which would be involved

## Submitting Pull Requests

* Follow the issue-first workflow above. Discuss your idea in the issue before
beginning work. This will help prevent wasting time on something that we might
not be able to implement. When suggesting a new feature, also make sure it won't
conflict with any work that's already in progress.

* Link the accepted, assigned issue in the pull request, using `Fixes #NNN` or
`Closes #NNN`.

* All new functionality must include relevant tests where applicable, and
user-facing changes must update the documentation.

* When submitting a pull request, target the branch that matches the kind of
change you are making. This project follows the same branch model as NetBox
itself. `main` is the default branch and holds the current stable line, so
fixes to the released version go there. `feature` accumulates work for the next
minor release and is merged into `main` when that release is cut.

* Do not bump versions or edit the release notes. A maintainer takes care of
release bookkeeping when the PR is merged, which avoids merge conflicts between
PRs submitted at the same time.

* All code submissions should meet the following criteria (CI will enforce
these checks):

  * `ruff check netbox_acls/` reports no violations
  * `ruff format --check netbox_acls/` reports no changes
  * `python manage.py makemigrations netbox_acls --check` reports no missing
    migrations, so any model change must ship its migration
  * The full test suite passes
  * The documentation builds with `zensical build --clean --strict`

## Documentation

Write for the page's audience: users need tasks and outcomes, administrators need
configuration and recovery guidance, and developers need contracts and examples.
Keep guides free of release-specific state. Versions belong in the release
notes, in upgrade notes beside the feature they affect, and in the README
compatibility matrix. Link to shared explanations instead of repeating them.

From the plugin repository root:

```bash
python -m pip install -e '.[docs]'
zensical build --clean --strict
```

Use `zensical serve` to preview the site. The contribution page of the site
includes this file, so keep its links absolute.

## Commenting

Only comment on an issue if you are sharing a relevant idea or constructive
feedback. **Do not** comment on an issue just to show your support (add a thumbs
up reaction to the top post instead) or ask for an ETA. These comments will be deleted to
reduce noise in the discussion.

## Development Workflow / Tooling

Development with this plugin leverages:

* VS Code
* VS Code devcontainer
* NetBox-Docker
* Docker-Compose
* Makefile for spin up of testing NetBox setup

In the dev container, `make all` installs the plugin, applies its migrations and
starts NetBox, and `make test` runs the test suite. `./test.sh` runs the same
suite in its own Docker Compose stack, as CI does.

## Releasing (maintainers)

See [Releasing](https://netbox-community.github.io/netbox-acls/development/releasing/)
in the documentation.
