import django.db.models.deletion
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

    ACLStandardRule.objects.using(db_alias).filter(_source_prefix__isnull=False).update(
        source_type=ContentType.objects.get_for_model(Prefix),
        source_id=models.F("_source_prefix_id"),
    )
    ACLExtendedRule.objects.using(db_alias).filter(_source_prefix__isnull=False).filter(
        _destination_prefix__isnull=False
    ).update(
        source_type=ContentType.objects.get_for_model(Prefix),
        source_id=models.F("_source_prefix_id"),
        destination_type=ContentType.objects.get_for_model(Prefix),
        destination_id=models.F("_destination_prefix_id"),
    )


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("extras", "0128_tableconfig"),
        ("ipam", "0081_remove_service_device_virtual_machine_add_parent_gfk_index"),
        ("netbox_acls", "0004_netbox_acls"),
    ]

    operations = [
        migrations.RenameField(
            model_name="aclextendedrule",
            old_name="destination_prefix",
            new_name="_destination_prefix",
        ),
        migrations.RenameField(
            model_name="aclextendedrule",
            old_name="source_prefix",
            new_name="_source_prefix",
        ),
        migrations.RenameField(
            model_name="aclstandardrule",
            old_name="source_prefix",
            new_name="_source_prefix",
        ),
        migrations.AddField(
            model_name="aclextendedrule",
            name="_destination_aggregate",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="_%(class)s_destinations",
                to="ipam.aggregate",
            ),
        ),
        migrations.AddField(
            model_name="aclextendedrule",
            name="_destination_ipaddress",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="_%(class)s_destinations",
                to="ipam.ipaddress",
            ),
        ),
        migrations.AddField(
            model_name="aclextendedrule",
            name="_destination_iprange",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="_%(class)s_destinations",
                to="ipam.iprange",
            ),
        ),
        migrations.AddField(
            model_name="aclextendedrule",
            name="_source_aggregate",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="_%(class)s_sources",
                to="ipam.aggregate",
            ),
        ),
        migrations.AddField(
            model_name="aclextendedrule",
            name="_source_ipaddress",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="_%(class)s_sources",
                to="ipam.ipaddress",
            ),
        ),
        migrations.AddField(
            model_name="aclextendedrule",
            name="_source_iprange",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="_%(class)s_sources",
                to="ipam.iprange",
            ),
        ),
        migrations.AddField(
            model_name="aclextendedrule",
            name="destination_id",
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="aclextendedrule",
            name="destination_type",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to=models.Q(
                    models.Q(("app_label", "ipam"), ("model__in", ("aggregate", "ipaddress", "iprange", "prefix")))
                ),
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AddField(
            model_name="aclextendedrule",
            name="source_id",
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="aclextendedrule",
            name="source_type",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to=models.Q(
                    models.Q(("app_label", "ipam"), ("model__in", ("aggregate", "ipaddress", "iprange", "prefix")))
                ),
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AddField(
            model_name="aclstandardrule",
            name="_source_aggregate",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="_%(class)s_sources",
                to="ipam.aggregate",
            ),
        ),
        migrations.AddField(
            model_name="aclstandardrule",
            name="_source_ipaddress",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="_%(class)s_sources",
                to="ipam.ipaddress",
            ),
        ),
        migrations.AddField(
            model_name="aclstandardrule",
            name="_source_iprange",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="_%(class)s_sources",
                to="ipam.iprange",
            ),
        ),
        migrations.AddField(
            model_name="aclstandardrule",
            name="source_id",
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="aclstandardrule",
            name="source_type",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to=models.Q(
                    models.Q(("app_label", "ipam"), ("model__in", ("aggregate", "ipaddress", "iprange", "prefix")))
                ),
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AlterField(
            model_name="aclextendedrule",
            name="_destination_prefix",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="_%(class)s_destinations",
                to="ipam.prefix",
            ),
        ),
        migrations.AlterField(
            model_name="aclextendedrule",
            name="_source_prefix",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="_%(class)s_sources",
                to="ipam.prefix",
            ),
        ),
        migrations.AlterField(
            model_name="aclstandardrule",
            name="_source_prefix",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="_%(class)s_sources",
                to="ipam.prefix",
            ),
        ),
        migrations.AddIndex(
            model_name="aclextendedrule",
            index=models.Index(
                fields=["destination_type", "destination_id", "source_type", "source_id"],
                name="netbox_acls_destina_8f93b4_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="aclstandardrule",
            index=models.Index(fields=["source_type", "source_id"], name="netbox_acls_source__01d2fa_idx"),
        ),
        # Copy over existing Prefix assignments
        migrations.RunPython(code=copy_prefix_assignments, reverse_code=migrations.RunPython.noop),
    ]
