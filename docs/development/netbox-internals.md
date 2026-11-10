# NetBox internals

Preserve these contracts when changing how the plugin integrates with NetBox.

## Integration contracts

| Area | Contract to preserve | Verification |
|---|---|---|
| Model views | `register_model_view()` registers object and child views, and `get_model_urls()` supplies their routes. | View and navigation tests. |
| Detail pages | `SimpleLayout`, NetBox panels, and plugin attributes render `generic/object.html`. | `tests/ui/` and table tests. |
| Generic selectors | `GenericObjectFormMixin` manages object-type selection, and HTMX refreshes dependent forms. | Add, edit, invalid submission, and action/protocol changes. |
| Validation | NetBox forms and serializers call model validation. Custom overrides must retain their parent implementation. | Form, API, and model tests. |
| Cached references | `CachedGenericReferenceMixin` mirrors generic references into typed shadow foreign keys used for lookup and deletion protection. | Cached-reference and deletion tests. |
| Related tabs | Child querysets apply `restrict(user, "view")`. Permitted access to a parent does not replace child permissions. | Restricted-user view tests. |
| GraphQL extensions | Relationships on NetBox's own types use registered type extensions, lazy plugin type references, and restricted prefetching. | `tests/graphql/test_type_extensions.py`. |

## Rule edits across write paths

`ACLRuleFormMixin` removes fields that do not apply to the selected action or
protocol and resets their instance values before model validation. Preserve
that behavior when adding criteria. Hidden inputs must not leave stale values
behind. Test both initial edits and HTMX redraws.

REST partial updates retain omitted fields. A protocol change must explicitly
clear incompatible criteria, since model validation rejects combinations left behind.
The serializer also normalizes TCP flags independently of model validation.

## Python import order and performance

Keep the extensions of NetBox's GraphQL types in `graphql_extensions/`. Avoid
importing NetBox's GraphQL modules there during startup, and preserve lazy type references to prevent
cycles.

Use `select_related()` for suitable foreign keys and prefetch generic references
and collections based on rendered fields. Preserve permission filtering.

## Compatibility changes

Review version bounds, Python requirements, container images, forms, UI, APIs,
and migrations together. Run affected tests against the intended NetBox release.
