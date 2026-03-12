from django.db import migrations, models


def infer_family(apps, schema_editor):
    db_alias = schema_editor.connection.alias

    AccessList = apps.get_model("netbox_acls", "AccessList")
    ACLStandardRule = apps.get_model("netbox_acls", "ACLStandardRule")
    ACLExtendedRule = apps.get_model("netbox_acls", "ACLExtendedRule")

    def _add_family_from_obj(fams, obj):
        """Append 'ipv4' or 'ipv6' to fams based on common NetBox IPAM shapes."""
        if obj is None:
            return

        version = (
            getattr(obj, "family", None)
            or getattr(getattr(obj, "prefix", None), "version", None)
            or getattr(getattr(obj, "address", None), "version", None)
            or getattr(getattr(obj, "start_address", None), "version", None)
        )
        if version == 4:
            fams.add("ipv4")
            return
        if version == 6:
            fams.add("ipv6")
            return
        return

    # Pull all ACLs
    for acl in AccessList.objects.using(db_alias).all().iterator():
        fams = set()

        # Standard rules (cached FKs)
        if acl.type == "standard":
            std_qs = (
                ACLStandardRule.objects.using(db_alias)
                .filter(access_list_id=acl.pk)
                .select_related(
                    "_source_prefix",
                    "_source_ipaddress",
                    "_source_iprange",
                    "_source_aggregate",
                )
                .only(  # keep it light
                    "id",
                    "_source_prefix__prefix",
                    "_source_ipaddress__address",
                    "_source_iprange__start_address",
                    "_source_aggregate__prefix",
                )
            )
            for r in std_qs.iterator():
                # Source side (one of the cached FKs should be set)
                for attr in ("_source_prefix", "_source_ipaddress", "_source_iprange", "_source_aggregate"):
                    obj = getattr(r, attr, None)
                    if obj:
                        _add_family_from_obj(fams, obj)
                        break  # only one will be set
                if len(fams) == 2:
                    break

        # Extended rules (cached FKs)
        else:
            ext_qs = (
                ACLExtendedRule.objects.using(db_alias)
                .filter(access_list_id=acl.pk)
                .select_related(
                    "_source_prefix",
                    "_source_ipaddress",
                    "_source_iprange",
                    "_source_aggregate",
                    "_destination_prefix",
                    "_destination_ipaddress",
                    "_destination_iprange",
                    "_destination_aggregate",
                )
                .only(
                    "id",
                    "_source_prefix__prefix",
                    "_source_ipaddress__address",
                    "_source_iprange__start_address",
                    "_source_aggregate__prefix",
                    "_destination_prefix__prefix",
                    "_destination_ipaddress__address",
                    "_destination_iprange__start_address",
                    "_destination_aggregate__prefix",
                )
            )
            for r in ext_qs.iterator():
                # Source
                for attr in ("_source_prefix", "_source_ipaddress", "_source_iprange", "_source_aggregate"):
                    obj = getattr(r, attr, None)
                    if obj:
                        _add_family_from_obj(fams, obj)
                        break
                # Destination
                for attr in (
                    "_destination_prefix",
                    "_destination_ipaddress",
                    "_destination_iprange",
                    "_destination_aggregate",
                ):
                    obj = getattr(r, attr, None)
                    if obj:
                        _add_family_from_obj(fams, obj)
                        break
                if len(fams) == 2:
                    break

        # Decide
        if fams == {"ipv4"}:
            acl.family = "ipv4"
        elif fams == {"ipv6"}:
            acl.family = "ipv6"
        elif fams == {"ipv4", "ipv6"}:
            acl.family = "dual"
        else:
            # No signal (no rules or 'any') — conservative default
            acl.family = "dual"

        acl.save(update_fields=["family"])


def backfill_assignment_family(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    ACLAssignment = apps.get_model("netbox_acls", "ACLAssignment")
    for a in ACLAssignment.objects.using(db_alias).select_related("access_list").all().iterator():
        a.family = a.access_list.family
        a.save(update_fields=["family"])


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
