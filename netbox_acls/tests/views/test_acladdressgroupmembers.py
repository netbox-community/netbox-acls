from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from netaddr import IPNetwork

from ipam.models import Prefix
from utilities.testing import ViewTestCases, create_tags

from ...models import ACLAddressGroup, ACLAddressGroupMember
from .base import PluginViewTestCase


@override_settings(SESSION_ENGINE="django.contrib.sessions.backends.signed_cookies")
class ACLAddressGroupMemberViewTestCase(PluginViewTestCase, ViewTestCases.PrimaryObjectViewTestCase):
    model = ACLAddressGroupMember
    user_permissions = ("ipam.view_prefix", "netbox_acls.view_acladdressgroup")

    @classmethod
    def setUpTestData(cls):
        cls.group = ACLAddressGroup.objects.create(name="trusted")
        cls.prefixes = [Prefix.objects.create(prefix=IPNetwork(f"10.{number}.0.0/16")) for number in range(1, 8)]
        cls.members = [
            ACLAddressGroupMember.objects.create(address_group=cls.group, member=prefix) for prefix in cls.prefixes[:3]
        ]

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "address_group": cls.group.pk,
            "member_content_type": ContentType.objects.get_for_model(Prefix).pk,
            "member_object_id": cls.prefixes[3].pk,
            "comments": "",
            "tags": [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            "comments": "Bulk edited",
        }

        cls.csv_data = (
            "address_group,member_type,member_id",
            *(f"{cls.group.name},ipam.prefix,{prefix.pk}" for prefix in cls.prefixes[4:]),
        )

        cls.csv_update_data = (
            "id,comments",
            f"{cls.members[0].pk},Updated by import",
            f"{cls.members[1].pk},Updated by import too",
        )

    def test_duplicate_edit_returns_validation_error(self):
        """Test that editing a member onto an object already in the group redisplays the form with an error."""
        self.add_permissions("netbox_acls.change_acladdressgroupmember")
        response = self.client.post(
            self._get_url("edit", self.members[0]),
            {
                "address_group": self.group.pk,
                "member_content_type": ContentType.objects.get_for_model(Prefix).pk,
                "member_object_id": self.prefixes[1].pk,
            },
        )
        self.assertHttpStatus(response, 200)
        self.assertIn("address_group", response.context["form"].errors)
