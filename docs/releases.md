# Release notes

Published releases link to their GitHub release. Dates are publication dates in UTC, and each entry lists the NetBox versions it supports.

## 2.2.0 (unreleased)

**Compatibility:** NetBox 4.7.x.

### Added

- **Reusable address groups.** Combine Aggregates, Prefixes, IP Addresses, and IP Ranges in an IPv4 or IPv6 group. Use groups as sources in Standard Rules, or as sources and destinations in Extended Rules. Groups and members support the UI, REST API, GraphQL, filtering, bulk import, and bulk edit. Members must match the group's address family, and duplicate memberships are rejected. Existing references to individual IPAM objects remain supported. ([#56](https://github.com/netbox-community/netbox-acls/issues/56), [#435](https://github.com/netbox-community/netbox-acls/pull/435))
- **ICMP types, ICMP codes, and TCP flags.** Extended Rules can match a specific ICMP type and code, with common type presets and explicit ICMPv4 and ICMPv6 protocols. TCP flags support **All** or **Any** matching. These criteria are available in forms, filters, rule details, optional table columns, CSV import, REST, and GraphQL. Existing generic `icmp` values remain valid, and the new criteria are optional. See [ICMP and TCP flags](user-guide/protocol-matching.md). ([#136](https://github.com/netbox-community/netbox-acls/issues/136), [#443](https://github.com/netbox-community/netbox-acls/pull/443))
- **Choice descriptions.** Create, edit, and bulk-edit forms show a short description beside choices such as the ACL type, protocol, and TCP flags. Filter forms keep plain choices. ([#440](https://github.com/netbox-community/netbox-acls/issues/440), [#445](https://github.com/netbox-community/netbox-acls/pull/445))
- **Documentation site.** Guides for users, administrators, and contributors, with the model, REST API, and GraphQL reference. ([#442](https://github.com/netbox-community/netbox-acls/issues/442))

### Changed

- **Forms show applicable fields.** Individual rule forms show match criteria and logging for Permit and Deny, and port fields for TCP and UDP. Assignment forms show direction only for interfaces and VM interfaces. Changing a selection refreshes the form without saving, and saving a rule clears criteria that no longer apply. ([#438](https://github.com/netbox-community/netbox-acls/issues/438), [#439](https://github.com/netbox-community/netbox-acls/pull/439))

### Fixed

- **`sqlmigrate` with squashed NetBox migrations.** The plugin's initial migrations reference NetBox's squashed `extras` and `ipam` migrations, so `manage.py sqlmigrate` no longer fails with `NodeNotFoundError`. ([#432](https://github.com/netbox-community/netbox-acls/issues/432), [#444](https://github.com/netbox-community/netbox-acls/pull/444))
- **Type and family guards with prefetched rules.** Changing the type or family of an Access List that has rules is rejected even when its rule relations were prefetched, for example by a custom script. ([#446](https://github.com/netbox-community/netbox-acls/issues/446), [#452](https://github.com/netbox-community/netbox-acls/pull/452))
- **Interface assignments without a direction.** Saving an interface or VM interface assignment with a missing or unknown direction is rejected even when validation is skipped, for example by a custom script. A host assignment saved without a direction stores `none`. ([#447](https://github.com/netbox-community/netbox-acls/issues/447), [#453](https://github.com/netbox-community/netbox-acls/pull/453))
- **Assignment direction on partial saves.** Saving an assignment with `update_fields`, for example by a custom script, keeps its direction consistent with its target. An interface assignment moved to a host stores `none`, and a host assignment moved to an interface needs `direction` in `update_fields`. ([#448](https://github.com/netbox-community/netbox-acls/issues/448), [#454](https://github.com/netbox-community/netbox-acls/pull/454))

### Upgrade

- Apply `0016_acl_address_groups` and `0017_aclextendedrule_icmp_and_tcp_flags`. Existing rules keep their address references and protocol values.
- Review permissions for the two new object types: **ACL Address Group** and **ACL Address Group Member**.
- If protocol choices are customized through `FIELD_CHOICES`, review the configuration for the new ICMPv4 and ICMPv6 choices. See [Customized protocol choices](administration/configuration.md#customized-protocol-choices).
- To roll back, restore the database backup taken before the upgrade and reinstall 2.1.x.
- Without a backup, test the reversal on a copy of the database first. Run `python manage.py migrate netbox_acls 0015` while 2.2.0 is still installed, then install 2.1.x.
- Reversing `0017` is blocked while rules use ICMP types, ICMP codes, TCP flags, or the explicit `icmpv4` or `icmpv6` protocols. Clear or replace these values first.
- Reversing `0016` is blocked while rules reference address groups. Remove or replace those references first. The reversal deletes every address group and membership.

### Known limitations

TCP flag matching requires the selected flags to be set. It cannot require a flag to be clear, and it describes packet criteria without tracking connection state. See [Limitations](features.md#limitations) for how forms refresh.

## 2.1.0 (2026-09-03)

**Compatibility:** NetBox 4.7.x. [Published release](https://github.com/netbox-community/netbox-acls/releases/tag/2.1.0).

### Added

- Per-rule logging for Standard and Extended Rules. Logging options require **Log matches** and are stored in a consistent order. Remark rules cannot enable logging.
- CSV, JSON, and YAML bulk import for Access Lists, Assignments, and both rule types. Imports accept supported natural values or numeric IDs, and IP Ranges require an ID. Interface names can be qualified by their parent, and omitted fields retain their values during partial updates.
- Standard and Extended Rule tabs on Aggregates, Prefixes, IP Addresses, and IP Ranges. Extended Rules show source, destination, or combined use.
- ACL relationships on NetBox's own GraphQL types for assignment targets and referenced IPAM objects.
- GRE, EIGRP, OSPF, and PIM protocol choices. These protocols do not accept ports.
- Assignment filtering by `assigned_object_type` or `assigned_object_type_id`.

### Changed

- Detail views and assignment controls use NetBox's declarative UI, restoring standard pagination, permissions, and queryset restrictions. Creating an assignment from an object preselects that object and returns to its tab.
- Choice filters accept multiple values while retaining single-value queries.
- Shared rule components align REST API and model validation. Invalid payloads can return revised wording or several applicable errors together.
- Removed deprecated GraphQL `StrFilterLookup` type arguments without changing the generated schema.
- Expanded generic-relation tests, cleaned release packaging, and updated dependencies, GitHub Actions, package metadata, and the Django classifier.

### Fixed

- Interface and VM interface assignments require Ingress or Egress. Device, Virtual Chassis, and Virtual Machine assignments continue to use `none`.
- Restored the Description filter on Access Lists.

### Upgrade

**Breaking:** NetBox 4.5 and 4.6 are no longer supported. Upgrade NetBox to 4.7 before upgrading the plugin.

Apply `0014_acl_rule_logging` and `0015_acl_owner_related_name`. The latter updates the owner relation for NetBox 4.7 without a database schema change.

Existing interface assignments with direction `none` are not changed automatically. They remain visible as **N/A**, but edits fail until Ingress or Egress is selected. This includes bulk edits to unrelated fields, where one invalid assignment can fail the whole operation. Correct these assignments before or shortly after upgrading.

## 2.0.3 (2026-08-16)

**Compatibility:** NetBox 4.5.x and 4.6.x. [Published release](https://github.com/netbox-community/netbox-acls/releases/tag/2.0.3).

### Fixed

- Plugin loading on NetBox 4.5.0 and 4.5.1.
- Region, Site Group, and Site filters for every assignment target. Region and Site Group filters include descendant scopes.
- Assignment scope parameters follow NetBox conventions: `region`, `site_group`, and `site` resolve slugs first, and the corresponding `_id` parameters use primary keys. Bare numeric values still fall back to a primary key when no slug matches, preserving the behavior of 2.0.0 to 2.0.2.
- Quick search matches text, complete rule sequence numbers, and comments on assignments and both rule types.
- Filtering assignments and rules by Access List name, and an invalid `name` reference in the Access List bulk-edit form.

### Changed

Expanded regression coverage for views, forms, filters, and tables. API query-count baselines were refreshed for NetBox 4.6.8.

### Upgrade

No database migrations are required.

## 2.0.2 (2026-07-28)

**Compatibility:** NetBox 4.5.x and 4.6.x. [Published release](https://github.com/netbox-community/netbox-acls/releases/tag/2.0.2).

### Fixed

- ACL renames could bypass host name and address-family validation.
- Stale device and action entries in the Access List table.
- The Extended Rule bulk-edit ACL type filter and an obsolete sequence-field reference.
- `AccessList.save()` and `ACLAssignment.save()` now honor `update_fields`.

### Changed

Optimized rule table columns and added API list-view query-count baselines.

## 2.0.1 (2026-05-25)

**Compatibility:** NetBox 4.5.x and 4.6.x. [Published release](https://github.com/netbox-community/netbox-acls/releases/tag/v2.0.1).

### Added

NetBox 4.6 support, while retaining NetBox 4.5 compatibility.

### Fixed

- The **Add Rule** button now respects rule-creation permissions for accounts that are not superusers.
- Extended Rule search results use the correct port-range fields and display readable ranges.

### Changed

Updated the Docker base image, example configuration, and screenshots, and corrected a security-policy typo.

## 2.0.0 (2026-04-02)

**Compatibility:** NetBox 4.5.x and Python 3.12 or later. [Published release](https://github.com/netbox-community/netbox-acls/releases/tag/2.0.0).

This release reworked assignments, addressing, and port matching to support broader ACL documentation.

### Added

- A unified **ACL Assignment** model supports one ACL on multiple Devices, Virtual Chassis, Virtual Machines, and interfaces. An assignments view lists these objects on the ACL, and GraphQL exposes `assigned_object` relationships.
- Rule address references support Prefixes, IP Addresses, IP Ranges, and Aggregates throughout the UI, REST API, and GraphQL.
- IPv4, IPv6, and Dual ACL families, with family-aware rule and assignment validation.
- Port ranges, normalized `source_port_terms` and `destination_port_terms` serializer helpers, and a generic IP protocol choice.
- Attached remarks on Permit and Deny rules, and parent ACL changelog entries for rule changes.
- Global search for ACLs and both rule types, native owner support, and bulk edit for all editable plugin models.
- Automatic sequence suggestions, configurable through `rule_sequence_step`.
- Read-only migration preflight checks and a squashed initial migration for fresh installations.

### Changed

- Assignment validation allows one IPv4 and one IPv6 ACL per interface and direction, while rejecting conflicting same-family or Dual assignments.
- Forms use object selectors. ACL names use Django's slug validation, and models use NetBox's default object URLs.
- Port ranges become the authoritative representation across forms, filters, tables, REST, and GraphQL.
- Updated GraphQL filters, standardized linting and formatting on Ruff, and improved migration performance through bulk operations and fewer unnecessary writes.

### Fixed

- Assignment uniqueness and preservation of the target when cloning assignments.
- Migration of Extended Rules with only one legacy prefix side populated.
- Duplicate standalone Remark rows sharing a sequence with Permit or Deny rules. Attached remarks remain supported.
- Invalid port criteria, including ports on protocols other than TCP or UDP, values outside the allowed range, and malformed range input.
- OpenAPI schema generation for the port-term helper fields.
- Unsupported actions appearing in ACL views, and the `top_level_menu` default when no setting is supplied.

### Upgrade

**Breaking:** Review API and GraphQL integrations before upgrading.

| Previous name or behavior | Replacement |
| --- | --- |
| `ACLInterfaceAssignment` | `ACLAssignment`, existing assignments are migrated |
| REST `interface-assignments` route | `assignments`, GraphQL assignment names also change |
| `source_prefix` / `destination_prefix` | Generic `source` / `destination` relations, backed by `*_type` and `*_id` |
| Rule `index` | `sequence` |
| `source_ports` / `destination_ports` | `source_port_ranges` / `destination_port_ranges` |
| ACLs without an explicit family | IPv4, IPv6, or Dual, with stricter validation |

Migrations convert existing assignments, addresses, sequence numbers, and ports, and infer an ACL family from existing rules and assignments. Preflight checks reject incompatible ACL names, orphaned generic references, and family or assignment conflicts before schema changes.

Test the upgrade on representative data, especially installations with legacy or inconsistent records. Resolve preflight findings before continuing.

## 1.9.1 (2025-09-07)

**Compatibility:** NetBox 4.3.x and 4.4.x. [Published release](https://github.com/netbox-community/netbox-acls/releases/tag/1.9.1).

### Added

NetBox 4.4 support.

## 1.9.0 (2025-08-04)

**Compatibility:** NetBox 4.3.x. [Published release](https://github.com/netbox-community/netbox-acls/releases/tag/1.9.0).

### Added

- NetBox 4.3 support and internationalization support.
- Rule filtering by ACL ID or name.
- GraphQL support for interface assignments and related rules on Access Lists.

### Changed

- Access List and interface-assignment forms use tabbed groups. Navigation items are grouped, and view registrations are simplified.
- The API's `assigned_object` serializer uses `JSONField`, and GraphQL types use `NetBoxObjectType`.
- Expanded API and model tests and updated pre-commit hooks.

## 1.8.1 (2025-02-18)

**Compatibility:** NetBox 4.2.x. [Published release](https://github.com/netbox-community/netbox-acls/releases/tag/1.8.1).

### Fixed

Corrected a packaging error, retaining NetBox 4.2 support.

## 1.8.0 (tag only)

**Compatibility:** NetBox 4.2.x. [Tagged source](https://github.com/netbox-community/netbox-acls/tree/1.8.0).

Introduced NetBox 4.2 support. This version exists as a tag without a separate GitHub release. [1.8.1](https://github.com/netbox-community/netbox-acls/releases/tag/1.8.1) followed shortly afterward with a packaging fix.

## 1.7.0 (2024-10-10)

**Compatibility:** NetBox 4.1.x. [Published release](https://github.com/netbox-community/netbox-acls/releases/tag/1.7.0).

### Added

NetBox 4.1 support.

## 1.6.1 (2024-06-13)

**Compatibility:** NetBox 4.0.2 and later 4.0 releases. [Published release](https://github.com/netbox-community/netbox-acls/releases/tag/1.6.1).

### Fixed

Filtering fixes.

## 1.6.0 (2024-06-07)

**Compatibility:** NetBox 4.0.2 and later 4.0 releases. [Published release](https://github.com/netbox-community/netbox-acls/releases/tag/1.6.0).

### Added

NetBox 4.0 support, with a minimum version of 4.0.2.

## 1.5.0 (2024-03-27)

**Compatibility:** NetBox 3.7.x. [Published release](https://github.com/netbox-community/netbox-acls/releases/tag/1.5.0).

### Added

NetBox 3.7 support.

## 1.4.0 (2024-03-27)

**Compatibility:** NetBox 3.6.x. [Published release](https://github.com/netbox-community/netbox-acls/releases/tag/1.4.0).

### Added

NetBox 3.6 support.

## 1.3.0 (2023-06-23)

**Compatibility:** NetBox 3.5.x. [Published release](https://github.com/netbox-community/netbox-acls/releases/tag/1.3.0).

### Added

NetBox 3.5 support.

### Changed

Updated project metadata to improve discovery by the netbox.dev plugin catalog.

## 1.2.2 (2023-01-25)

**Compatibility:** NetBox 3.4.x. [Published release](https://github.com/netbox-community/netbox-acls/releases/tag/1.2.2).

### Fixed

Included missing migrations for NetBox 3.4 and the plugin's v1.2 series.

## 1.2.1 (2023-01-25)

**Compatibility:** NetBox 3.4.x. [Published release](https://github.com/netbox-community/netbox-acls/releases/tag/1.2.1).

### Added

A configuration option to hide the plugin's top-level navigation.

## 1.2.0 (2023-01-23)

**Compatibility:** NetBox 3.4.x only. [Published release](https://github.com/netbox-community/netbox-acls/releases/tag/1.2.0).

### Added

NetBox 3.4 support and top-level navigation.

### Changed

Moved object cards to a view tab, refreshed the documentation, and updated initializers to use the initializer plugin's example data.

### Upgrade

NetBox 3.3 is no longer supported. Use the v1.1 series for NetBox 3.3.

## 1.1.1 (2023-01-23)

**Compatibility:** NetBox 3.3.x, the final release for this NetBox series. [Published release](https://github.com/netbox-community/netbox-acls/releases/tag/1.1.1).

### Added

- Virtual Machine filtering on the Access List form.
- Links from rule counts to their rules.
- Permissions on navigation links, allowing administrators to control access.

### Fixed

- Site filtering by Region on the Access List form.
- Missing defaults on optional fields that caused migrations to be generated again.
- A `ValueError` when an instance did not exist.
- Version values in package configuration.

### Changed

Forms use NetBox classes, installation instructions use PyPI, and development initialization uses the separate NetBox Initializers plugin after its removal from netbox-docker.

## 1.1.0 (2022-10-07)

**Compatibility:** NetBox 3.3.x. [Published release](https://github.com/netbox-community/netbox-acls/releases/tag/1.1.0).

### Added

NetBox 3.3 support.

### Upgrade

NetBox 3.2 is no longer supported. Use the v1.0 series for NetBox 3.2.

## 1.0.1 (2022-10-07)

**Compatibility:** NetBox 3.2.x. [Published release](https://github.com/netbox-community/netbox-acls/releases/tag/1.0.1).

### Fixed

Corrected form validation that caused interface ACL assignment failures and tracebacks.

## 1.0.0 (2022-10-05)

**Compatibility:** NetBox 3.2.x only. [Published release](https://github.com/netbox-community/netbox-acls/releases/tag/1.0.0).

The first release used a new project name to avoid an existing PyPI package conflict.

### Added

- Access Lists assigned to Devices, Virtual Chassis, and Virtual Machines.
- Separate Standard and Extended Rule models.
- Ingress and Egress interface assignments. In this release, the parent host also had to have the ACL assigned.
- ACL cards on supported hosts, interfaces, and VM interfaces.
- A development workflow using VS Code devcontainers, Docker Compose, and netbox-docker.
