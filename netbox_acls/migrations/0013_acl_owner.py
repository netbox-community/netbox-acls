import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_acls", "0012_aclextendedrule_port_ranges"),
        ("users", "0015_owner"),
    ]

    operations = [
        migrations.AddField(
            model_name="accesslist",
            name="description",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="accesslist",
            name="owner",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="users.owner"
            ),
        ),
        migrations.AddField(
            model_name="aclassignment",
            name="owner",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="users.owner"
            ),
        ),
        migrations.AddField(
            model_name="aclextendedrule",
            name="comments",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="aclextendedrule",
            name="owner",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="users.owner"
            ),
        ),
        migrations.AddField(
            model_name="aclstandardrule",
            name="comments",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="aclstandardrule",
            name="owner",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="users.owner"
            ),
        ),
    ]
