from django.db import migrations, models


def infer_family(apps, schema_editor):
    db_alias = schema_editor.connection.alias

    AccessList = apps.get_model("netbox_acls", "AccessList")
    ACLStandardRule = apps.get_model("netbox_acls", "ACLStandardRule")
    ACLExtendedRule = apps.get_model("netbox_acls", "ACLExtendedRule")

    def _get_version(prefix_obj):
        """Extract IP version from a Prefix object."""
        if prefix_obj is None:
            return None
        prefix = getattr(prefix_obj, "prefix", None)
        return getattr(prefix, "version", None) if prefix else None

    # Pre-fetch rules with only the prefix relations we need
    std_rules_by_acl = {}
    for rule in (
        ACLStandardRule.objects.using(db_alias)
        .select_related("_source_prefix")
        .only("id", "access_list_id", "_source_prefix__prefix")
        .iterator()
    ):
        std_rules_by_acl.setdefault(rule.access_list_id, []).append(rule)

    ext_rules_by_acl = {}
    for rule in (
        ACLExtendedRule.objects.using(db_alias)
        .select_related("_source_prefix", "_destination_prefix")
        .only("id", "access_list_id", "_source_prefix__prefix", "_destination_prefix__prefix")
        .iterator()
    ):
        ext_rules_by_acl.setdefault(rule.access_list_id, []).append(rule)

    # Process all ACLs
    acls_to_update = []

    for acl in AccessList.objects.using(db_alias).only("id", "type").iterator():
        has_v4 = False
        has_v6 = False

        if acl.type == "standard":
            for rule in std_rules_by_acl.get(acl.pk, []):
                version = _get_version(rule._source_prefix)
                if version == 4:
                    has_v4 = True
                elif version == 6:
                    has_v6 = True
                if has_v4 and has_v6:
                    break
        else:
            for rule in ext_rules_by_acl.get(acl.pk, []):
                for prefix_obj in (rule._source_prefix, rule._destination_prefix):
                    version = _get_version(prefix_obj)
                    if version == 4:
                        has_v4 = True
                    elif version == 6:
                        has_v6 = True
                if has_v4 and has_v6:
                    break

        if has_v4 and has_v6:
            acl.family = "dual"
        elif has_v4:
            acl.family = "ipv4"
        elif has_v6:
            acl.family = "ipv6"
        else:
            acl.family = "dual"  # Conservative default

        acls_to_update.append(acl)

    AccessList.objects.using(db_alias).bulk_update(acls_to_update, ["family"], batch_size=100)


def backfill_assignment_family(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    ACLAssignment = apps.get_model("netbox_acls", "ACLAssignment")

    assignments = list(ACLAssignment.objects.using(db_alias).select_related("access_list"))
    for a in assignments:
        a.family = a.access_list.family

    ACLAssignment.objects.using(db_alias).bulk_update(assignments, ["family"], batch_size=100)


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_acls", "0009_acl_rule_sequence_unique"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="aclassignment",
            options={"ordering": ["assigned_object_type", "assigned_object_id", "access_list", "family", "direction"]},
        ),
        migrations.AlterUniqueTogether(
            name="aclassignment",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="accesslist",
            name="family",
            field=models.CharField(db_index=True, default="ipv4", max_length=8),
        ),
        migrations.RunPython(infer_family, migrations.RunPython.noop),
        migrations.AddField(
            model_name="aclassignment",
            name="family",
            field=models.CharField(db_index=True, default="dual", editable=False, max_length=8),
            preserve_default=False,
        ),
        migrations.RunPython(backfill_assignment_family, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="aclassignment",
            constraint=models.UniqueConstraint(
                fields=("access_list", "assigned_object_type", "assigned_object_id", "direction"),
                name="netbox_acls_aclassignment_unique_object_direction_family_per_access_list",
                violation_error_message="ACL Assignment for the given object and direction.",
            ),
        ),
        migrations.AddConstraint(
            model_name="aclassignment",
            constraint=models.UniqueConstraint(
                condition=models.Q(("direction", "none"), _negated=True),
                fields=("assigned_object_type", "assigned_object_id", "direction", "family"),
                name="netbox_acls_aclassignment_unique_object_direction_family_interface_only",
                violation_error_message="ACL Assignment for the given object, direction and family exists.",
            ),
        ),
    ]
