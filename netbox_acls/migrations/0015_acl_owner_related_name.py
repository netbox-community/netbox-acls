import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_acls", "0014_acl_rule_logging"),
        ("users", "0015_owner"),
    ]

    operations = [
        migrations.AlterField(
            model_name="accesslist",
            name="owner",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="+", to="users.owner"
            ),
        ),
        migrations.AlterField(
            model_name="aclassignment",
            name="owner",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="+", to="users.owner"
            ),
        ),
        migrations.AlterField(
            model_name="aclextendedrule",
            name="owner",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="+", to="users.owner"
            ),
        ),
        migrations.AlterField(
            model_name="aclstandardrule",
            name="owner",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="+", to="users.owner"
            ),
        ),
    ]
