from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_acls", "0006_alter_accesslist_name"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="aclextendedrule",
            options={"ordering": ("access_list", "index", "-action")},
        ),
        migrations.AlterModelOptions(
            name="aclstandardrule",
            options={"ordering": ("access_list", "index", "-action")},
        ),
        migrations.AlterUniqueTogether(
            name="aclextendedrule",
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name="aclstandardrule",
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name="aclextendedrule",
            constraint=models.UniqueConstraint(
                fields=("access_list", "index"),
                name="netbox_acls_aclextendedrule_unique_aclrule_index",
                violation_error_message="Unique ACL rule index already exists.",
            ),
        ),
        migrations.AddConstraint(
            model_name="aclstandardrule",
            constraint=models.UniqueConstraint(
                fields=("access_list", "index"),
                name="netbox_acls_aclstandardrule_unique_aclrule_index",
                violation_error_message="Unique ACL rule index already exists.",
            ),
        ),
    ]
