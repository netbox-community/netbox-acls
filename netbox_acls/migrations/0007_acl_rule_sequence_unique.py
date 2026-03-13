from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_acls", "0006_alter_accesslist_name"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="aclextendedrule",
            options={"ordering": ("access_list", "sequence", "-action")},
        ),
        migrations.AlterModelOptions(
            name="aclstandardrule",
            options={"ordering": ("access_list", "sequence", "-action")},
        ),
        migrations.AlterUniqueTogether(
            name="aclextendedrule",
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name="aclstandardrule",
            unique_together=set(),
        ),
        migrations.RenameField(
            model_name="aclextendedrule",
            old_name="index",
            new_name="sequence",
        ),
        migrations.RenameField(
            model_name="aclstandardrule",
            old_name="index",
            new_name="sequence",
        ),
        migrations.AddConstraint(
            model_name="aclextendedrule",
            constraint=models.UniqueConstraint(
                fields=("access_list", "sequence"),
                name="netbox_acls_aclextendedrule_unique_aclrule_sequence",
                violation_error_message="Unique ACL rule sequence already exists.",
            ),
        ),
        migrations.AddConstraint(
            model_name="aclstandardrule",
            constraint=models.UniqueConstraint(
                fields=("access_list", "sequence"),
                name="netbox_acls_aclstandardrule_unique_aclrule_sequence",
                violation_error_message="Unique ACL rule sequence already exists.",
            ),
        ),
    ]
