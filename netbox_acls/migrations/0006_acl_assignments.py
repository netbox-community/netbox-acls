import django.db.models.deletion
from django.db import migrations, models


def copy_host_assignments(apps, schema_editor):
    """
    Copies host assignments from the AccessList model to ACLAssignment model.
    """

    db_alias = schema_editor.connection.alias
    AccessList = apps.get_model("netbox_acls", "AccessList")
    ACLAssignment = apps.get_model("netbox_acls", "ACLAssignment")

    for acl in AccessList.objects.using(db_alias).all():
        ACLAssignment.objects.using(db_alias).create(
            access_list=acl,
            assigned_object_type=acl.assigned_object_type,
            assigned_object_id=acl.assigned_object_id,
            direction="none",
        )


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_acls", "0005_acl_rule_source_and_destination_objects"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="ACLInterfaceAssignment",
            new_name="ACLAssignment",
        ),
        migrations.AlterModelOptions(
            name="accesslist",
            options={"ordering": ("name",)},
        ),
        migrations.AlterUniqueTogether(
            name="accesslist",
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name="aclassignment",
            name="access_list",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="aclassignments",
                to="netbox_acls.accesslist",
            ),
        ),
        migrations.AlterField(
            model_name="aclassignment",
            name="assigned_object_type",
            field=models.ForeignKey(
                limit_choices_to=models.Q(
                    models.Q(
                        models.Q(("app_label", "dcim"), ("model__in", ("device", "interface", "virtualchassis"))),
                        models.Q(("app_label", "virtualization"), ("model__in", ("virtualmachine", "vminterface"))),
                        _connector="OR",
                    ),
                ),
                on_delete=django.db.models.deletion.PROTECT,
                to="contenttypes.contenttype",
            ),
        ),
        # Copy over existing Host assignments
        migrations.RunPython(code=copy_host_assignments, reverse_code=migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="accesslist",
            name="assigned_object_id",
        ),
        migrations.RemoveField(
            model_name="accesslist",
            name="assigned_object_type",
        ),
    ]
