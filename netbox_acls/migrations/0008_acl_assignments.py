import django.db.models.deletion
from django.db import migrations, models


def copy_host_assignments(apps, schema_editor):
    """
    Copies host assignments from the AccessList model to ACLAssignment model.
    """

    db_alias = schema_editor.connection.alias
    AccessList = apps.get_model("netbox_acls", "AccessList")
    ACLAssignment = apps.get_model("netbox_acls", "ACLAssignment")

    assignments = [
        ACLAssignment(
            access_list=acl,
            assigned_object_type_id=acl.assigned_object_type_id,
            assigned_object_id=acl.assigned_object_id,
            direction="none",
        )
        for acl in AccessList.objects.using(db_alias).only("id", "assigned_object_type_id", "assigned_object_id")
    ]

    ACLAssignment.objects.using(db_alias).bulk_create(assignments, batch_size=100)


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_acls", "0007_acl_rule_sequence_unique"),
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
