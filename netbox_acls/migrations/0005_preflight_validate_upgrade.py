import re
from collections import defaultdict

from django.db import migrations

ACL_NAME_RE = re.compile(r"^[-a-zA-Z0-9_]+\Z")

ACL_DIRECTION_INGRESS = "ingress"
ACL_DIRECTION_EGRESS = "egress"

ACL_FAMILY_IPV4 = "ipv4"
ACL_FAMILY_IPV6 = "ipv6"
ACL_FAMILY_DUAL = "dual"

ERROR_LIMIT = 10


def _make_buckets():
    """Return a fresh-ordered dict of error buckets."""
    titles = [
        ("invalid_accesslist_name", "AccessList names incompatible with 0006"),
        ("orphaned_accesslist_host", "AccessLists pointing to missing host objects for 0008"),
        ("orphaned_interface_assignment_target", "ACLInterfaceAssignments pointing to missing interface objects"),
        (
            "future_interface_family_conflicts",
            "Interface assignments that will still be invalid after 0009 family inference",
        ),
    ]
    return {key: {"title": title, "count": 0, "examples": []} for key, title in titles}


def _record(buckets, key, message):
    bucket = buckets[key]
    bucket["count"] += 1
    if len(bucket["examples"]) < ERROR_LIMIT:
        bucket["examples"].append(message)


def _family_from_prefix(prefix_obj):
    if prefix_obj is None:
        return None

    version = getattr(getattr(prefix_obj, "prefix", None), "version", None)
    if version == 4:
        return ACL_FAMILY_IPV4
    if version == 6:
        return ACL_FAMILY_IPV6
    return None


def _infer_acl_families(access_lists, standard_rules, extended_rules):
    family_signals = defaultdict(set)

    for rule in standard_rules:
        family = _family_from_prefix(rule.source_prefix)
        if family:
            family_signals[rule.access_list_id].add(family)

    for rule in extended_rules:
        source_family = _family_from_prefix(rule.source_prefix)
        destination_family = _family_from_prefix(rule.destination_prefix)

        if source_family:
            family_signals[rule.access_list_id].add(source_family)
        if destination_family:
            family_signals[rule.access_list_id].add(destination_family)

    acl_families = {}
    for acl in access_lists:
        families = family_signals.get(acl["id"], set())
        if families == {ACL_FAMILY_IPV4}:
            acl_families[acl["id"]] = ACL_FAMILY_IPV4
        elif families == {ACL_FAMILY_IPV6}:
            acl_families[acl["id"]] = ACL_FAMILY_IPV6
        elif families == {ACL_FAMILY_IPV4, ACL_FAMILY_IPV6}:
            acl_families[acl["id"]] = ACL_FAMILY_DUAL
        else:
            # No rule-level signal (e.g. ACL has no rules or only remarks) =>
            # fall back to "dual" so it occupies both slots, matching the
            # behavior of migration 0009's infer_family().
            acl_families[acl["id"]] = ACL_FAMILY_DUAL

    return acl_families


def validate_v2_preflight_data(apps, schema_editor):
    db_alias = schema_editor.connection.alias

    ContentType = apps.get_model("contenttypes", "ContentType")
    AccessList = apps.get_model("netbox_acls", "AccessList")
    ACLInterfaceAssignment = apps.get_model("netbox_acls", "ACLInterfaceAssignment")
    ACLStandardRule = apps.get_model("netbox_acls", "ACLStandardRule")
    ACLExtendedRule = apps.get_model("netbox_acls", "ACLExtendedRule")

    buckets = _make_buckets()

    # -------------------------------------------------------------------------
    # Resolve content types for GFK targets.  Only dcim and virtualization
    # provide valid hosts (Device, VirtualChassis, VirtualMachine) and
    # interfaces (Interface, VMInterface).  GFKs have no DB-level FK
    # constraint, so orphaned references are possible after deletions.
    # -------------------------------------------------------------------------
    ct_rows = list(
        ContentType.objects.using(db_alias)
        .filter(app_label__in=["dcim", "virtualization"])
        .values("id", "app_label", "model")
    )
    ct_meta = {row["id"]: (row["app_label"], row["model"]) for row in ct_rows}

    host_ct_models = {
        ("dcim", "device"),
        ("dcim", "virtualchassis"),
        ("virtualization", "virtualmachine"),
    }
    interface_ct_models = {
        ("dcim", "interface"),
        ("virtualization", "vminterface"),
    }

    ct_model_map = {}
    for ct_id, (app_label, model_name) in ct_meta.items():
        try:
            ct_model_map[ct_id] = apps.get_model(app_label, model_name)
        except LookupError:
            ct_model_map[ct_id] = None

    access_lists = list(
        AccessList.objects.using(db_alias).values(
            "id",
            "name",
            "assigned_object_type_id",
            "assigned_object_id",
        )
    )
    acl_by_id = {acl["id"]: acl for acl in access_lists}

    interface_assignments = list(
        ACLInterfaceAssignment.objects.using(db_alias).values(
            "id",
            "access_list_id",
            "direction",
            "assigned_object_type_id",
            "assigned_object_id",
        )
    )

    # Bulk existence checks for all GFK targets.
    target_ids_by_ct = defaultdict(set)

    for acl in access_lists:
        target_ids_by_ct[acl["assigned_object_type_id"]].add(acl["assigned_object_id"])

    for assignment in interface_assignments:
        target_ids_by_ct[assignment["assigned_object_type_id"]].add(assignment["assigned_object_id"])

    existing_ids_by_ct = {}
    for ct_id, object_ids in target_ids_by_ct.items():
        model = ct_model_map.get(ct_id)
        if model is None:
            existing_ids_by_ct[ct_id] = set()
            continue

        existing_ids_by_ct[ct_id] = set(
            model.objects.using(db_alias).filter(pk__in=object_ids).values_list("pk", flat=True)
        )

    #
    # 0006 preflight: v1.9.1 allows any CharField value for names; 0006
    # tightens this to a slug-like pattern.
    #
    for acl in access_lists:
        if not ACL_NAME_RE.fullmatch(acl["name"] or ""):
            _record(
                buckets,
                "invalid_accesslist_name",
                "AccessList id={id} name={name!r} does not satisfy the v2 slug validator.".format(
                    id=acl["id"],
                    name=acl["name"],
                ),
            )

    #
    # 0008 preflight: GFK host/interface references have no DB-level FK, so
    # orphans are possible when the target object has been deleted.
    #
    for acl in access_lists:
        ct_key = ct_meta.get(acl["assigned_object_type_id"])
        if ct_key not in host_ct_models:
            continue

        if acl["assigned_object_id"] not in existing_ids_by_ct.get(acl["assigned_object_type_id"], set()):
            _record(
                buckets,
                "orphaned_accesslist_host",
                "AccessList id={id} name={name!r} points to missing host {app}.{model}#{obj_id}.".format(
                    id=acl["id"],
                    name=acl["name"],
                    app=ct_key[0],
                    model=ct_key[1],
                    obj_id=acl["assigned_object_id"],
                ),
            )

    for assignment in interface_assignments:
        ct_key = ct_meta.get(assignment["assigned_object_type_id"])
        if ct_key not in interface_ct_models:
            continue

        if assignment["assigned_object_id"] not in existing_ids_by_ct.get(assignment["assigned_object_type_id"], set()):
            acl = acl_by_id.get(assignment["access_list_id"])
            _record(
                buckets,
                "orphaned_interface_assignment_target",
                "ACLInterfaceAssignment id={id} acl_id={acl_id} acl_name={acl_name!r} "
                "points to missing interface {app}.{model}#{obj_id}.".format(
                    id=assignment["id"],
                    acl_id=assignment["access_list_id"],
                    acl_name=acl["name"] if acl else None,
                    app=ct_key[0],
                    model=ct_key[1],
                    obj_id=assignment["assigned_object_id"],
                ),
            )

    #
    # Load rules for family inference.
    #
    standard_rules = list(ACLStandardRule.objects.using(db_alias).select_related("source_prefix").all())
    extended_rules = list(
        ACLExtendedRule.objects.using(db_alias).select_related("source_prefix", "destination_prefix").all()
    )

    #
    # 0009 preflight: v1.9.1 allows multiple ACLs per interface per
    # direction.  v2 enforces at most one ACL per IP-family slot per
    # direction.  A "dual" ACL occupies both the IPv4 and IPv6 slots.
    #
    acl_families = _infer_acl_families(access_lists, standard_rules, extended_rules)

    grouped_interface_assignments = defaultdict(list)
    for assignment in interface_assignments:
        if assignment["direction"] not in {ACL_DIRECTION_INGRESS, ACL_DIRECTION_EGRESS}:
            continue

        acl = acl_by_id.get(assignment["access_list_id"])
        if acl is None:
            continue

        grouped_interface_assignments[
            (
                assignment["assigned_object_type_id"],
                assignment["assigned_object_id"],
                assignment["direction"],
            )
        ].append(
            {
                "assignment_id": assignment["id"],
                "access_list_id": assignment["access_list_id"],
                "acl_name": acl["name"],
                "family": acl_families.get(assignment["access_list_id"], ACL_FAMILY_DUAL),
            }
        )

    for (ct_id, object_id, direction), entries in grouped_interface_assignments.items():
        family_counts = defaultdict(int)
        for entry in entries:
            family_counts[entry["family"]] += 1

        # A "dual" ACL occupies both the IPv4 and the IPv6 slot, so count
        # it towards both totals.
        ipv4_total = family_counts[ACL_FAMILY_IPV4] + family_counts[ACL_FAMILY_DUAL]
        ipv6_total = family_counts[ACL_FAMILY_IPV6] + family_counts[ACL_FAMILY_DUAL]

        conflicts = []
        if ipv4_total > 1:
            conflicts.append(f"{ipv4_total} ACLs competing for the IPv4 slot")
        if ipv6_total > 1:
            conflicts.append(f"{ipv6_total} ACLs competing for the IPv6 slot")

        if not conflicts:
            continue

        ct_key = ct_meta.get(ct_id, ("unknown", str(ct_id)))
        occupants = ", ".join(
            "assignment_id={assignment_id}, acl_id={access_list_id}, acl_name={acl_name!r}, "
            "inferred_family={family}".format(**entry)
            for entry in entries
        )
        _record(
            buckets,
            "future_interface_family_conflicts",
            (
                f"{ct_key[0]}.{ct_key[1]}#{object_id} direction={direction}: "
                f"{'; '.join(conflicts)}. Assignments: {occupants}"
            ),
        )

    # -------------------------------------------------------------------------
    # Build the final error report.
    # -------------------------------------------------------------------------
    has_errors = any(b["count"] > 0 for b in buckets.values())
    if not has_errors:
        return

    sections = []
    for bucket in buckets.values():
        if not bucket["count"]:
            continue

        lines = ["- " + example for example in bucket["examples"]]
        remaining = bucket["count"] - len(bucket["examples"])
        if remaining > 0:
            lines.append(f"- ... {remaining} more")

        sections.append(
            "{title} ({count})\n{details}".format(
                title=bucket["title"],
                count=bucket["count"],
                details="\n".join(lines),
            )
        )

    raise RuntimeError(
        "Pre-flight validation for the v2.0 ACL migrations failed.\n\n"
        "Please fix the legacy data below while still on the pre-v2 schema, then rerun the migration.\n\n"
        "The checks cover the data touched by the current dev migration chain: "
        "0006 name validation, 0008 ACLAssignment migration, "
        "and 0009 family inference/assignment constraints.\n\n" + "\n\n".join(sections)
    )


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("extras", "0128_tableconfig"),
        ("ipam", "0081_remove_service_device_virtual_machine_add_parent_gfk_index"),
        ("netbox_acls", "0004_netbox_acls"),
    ]

    operations = [
        migrations.RunPython(validate_v2_preflight_data, migrations.RunPython.noop),
    ]
