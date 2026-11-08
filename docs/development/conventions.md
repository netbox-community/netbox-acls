# Development conventions

Follow the existing NetBox integration and keep changes close to the code they
affect. Use [Contributing](contributing.md) for setup and required checks.

## File placement

Paths are relative to `netbox_acls/`.

| Responsibility | Location |
|---|---|
| Models and shared model behavior | `models/access_lists.py`, `models/access_list_rules.py`, `models/address_groups.py`, `models/mixins.py`, `models/managers.py` |
| Forms | `forms/models.py`, `forms/bulk_edit.py`, `forms/bulk_import.py`, `forms/filtersets.py` |
| UI views and routing | `views.py`, `urls.py`, `navigation.py`, `object_actions.py` |
| Detail panels and attributes | `ui/panels.py`, `ui/attrs.py` |
| REST | `api/serializers.py`, `api/views.py`, `api/urls.py` |
| GraphQL | `graphql/`, with extensions to NetBox's own types in `graphql_extensions/` |
| Filtering, tables, and search | `filtersets.py`, `tables/`, `search.py` |
| Tests | `tests/`, grouped by layer |

Export new public classes through the appropriate package and keep `__all__`
alphabetized. Discuss larger reorganizations separately from feature work.

## Validation and data changes

Put shared business validation on models and preserve NetBox's validation path
in forms and serializers. Code creating objects directly should call
`full_clean()` before `save()`, since saving alone does not run every model validator.

Extended rules collect field errors through `_validate_remark()`,
`_validate_ports()`, `_validate_icmp()`, `_validate_tcp_flags()`, and
`_validate_logging()`. Keep checks focused and preserve remark-specific errors.
These are private implementation helpers. Choice changes must retain the
underlying protocol and family checks. Only NetBox's
`utilities.forms.fields.ChoiceField`, `TypedChoiceField`, and
`MultipleChoiceField` render a choice's description. Django's own classes drop it.

Keep normalization consistent across write paths. REST has explicit validators
for logging options and TCP flags. Do not assume model normalization is copied
back into serializer data.

Preserve generic-reference shadow foreign keys and deletion protection.
Queryset updates bypass model methods, so callers must maintain those invariants.
Use historical models in data migrations and test affected upgrade paths,
including reverse guards.

## Review and tests

Cover zero versus unset ICMP values, family conflicts, protocol changes,
canonical flag order, remarks, cloning, and explicit clearing in partial and
bulk updates. Use the existing model, form, API, filter, UI, and view tests.
Check permissions and query growth when related objects are affected.

Ruff configuration lives in `ruff.toml`, including the target Python version, line
length, quote style, and line endings. Hook settings live in
`.pre-commit-config.yaml`. Keep those sources authoritative, and run
`pre-commit install` so the hooks check each commit.
