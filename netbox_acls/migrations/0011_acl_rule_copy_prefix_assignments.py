from django.db import migrations, models


def copy_prefix_assignments(apps, schema_editor):
    """
    Copy Source and Destination Prefix ForeignKey IDs to the GenericForeignKey
    fields.
    """

    db_alias = schema_editor.connection.alias
    ContentType = apps.get_model("contenttypes", "ContentType")
    Prefix = apps.get_model("ipam", "Prefix")
    ACLStandardRule = apps.get_model("netbox_acls", "ACLStandardRule")
    ACLExtendedRule = apps.get_model("netbox_acls", "ACLExtendedRule")

    prefix_ct = ContentType.objects.get_for_model(Prefix)

    ACLStandardRule.objects.using(db_alias).filter(_source_prefix__isnull=False).update(
        source_type=prefix_ct, source_id=models.F("_source_prefix_id")
    )

    # Copy source and destination independently for extended rules
    ACLExtendedRule.objects.using(db_alias).filter(_source_prefix__isnull=False).update(
        source_type=prefix_ct, source_id=models.F("_source_prefix_id")
    )
    ACLExtendedRule.objects.using(db_alias).filter(_destination_prefix__isnull=False).update(
        destination_type=prefix_ct, destination_id=models.F("_destination_prefix_id")
    )


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_acls", "0010_acl_rule_source_and_destination_objects"),
    ]

    operations = [
        # Copy over existing Prefix assignments
        migrations.RunPython(code=copy_prefix_assignments, reverse_code=migrations.RunPython.noop),
    ]
