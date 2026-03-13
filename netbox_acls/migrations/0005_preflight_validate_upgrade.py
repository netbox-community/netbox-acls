from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("extras", "0128_tableconfig"),
        ("ipam", "0081_remove_service_device_virtual_machine_add_parent_gfk_index"),
        ("netbox_acls", "0004_netbox_acls"),
    ]

    operations = [
        migrations.RunPython(code=migrations.RunPython.noop, reverse_code=migrations.RunPython.noop),
    ]
