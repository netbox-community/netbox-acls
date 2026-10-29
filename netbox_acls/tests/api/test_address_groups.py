from rest_framework import status

from ipam.models import Prefix
from utilities.testing import APIViewTestCases

from ...choices import ACLAddressFamilyChoices
from ...models import ACLAddressGroup, ACLAddressGroupMember


class ACLAddressGroupAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """
    API view test case for ACLAddressGroup.
    """

    model = ACLAddressGroup
    view_namespace = "plugins-api:netbox_acls"
    brief_fields = ["display", "id", "name", "url"]

    @classmethod
    def setUpTestData(cls):
        """Set up ACL Address Group for API view testing."""

        acl_address_groups = (
            ACLAddressGroup(
                name="group-1",
            ),
            ACLAddressGroup(
                name="group-2",
            ),
            ACLAddressGroup(
                name="group-3",
                family=ACLAddressFamilyChoices.FAMILY_IPV6,
            ),
        )
        ACLAddressGroup.objects.bulk_create(acl_address_groups)

        cls.create_data = [
            {
                "name": "group-4",
                "family": ACLAddressFamilyChoices.FAMILY_IPV4,
            },
            {
                "name": "group-5",
                "family": ACLAddressFamilyChoices.FAMILY_IPV6,
            },
            {
                "name": "group-6",
            },
        ]
        cls.bulk_update_data = {
            "comments": "Reviewed",
        }
        cls.bulk_update_invalid_data = {
            "family": "dual",
        }

    def test_family_patch_is_rejected_when_used(self):
        """Test that the API rejects a family change while the address group has members."""
        self.add_permissions("netbox_acls.change_acladdressgroup")
        group = ACLAddressGroup.objects.get(name="group-1")
        prefix = Prefix.objects.create(prefix="192.0.2.0/24")
        ACLAddressGroupMember.objects.create(address_group=group, member=prefix)
        response = self.client.patch(
            self._get_detail_url(group),
            {"family": ACLAddressFamilyChoices.FAMILY_IPV6},
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("family", response.data)

    def test_member_count_is_returned_without_a_nested_member_list(self):
        """Test that the API returns the member count instead of a nested member list."""
        self.add_permissions("netbox_acls.view_acladdressgroup")
        group = ACLAddressGroup.objects.get(name="group-1")
        prefix = Prefix.objects.create(prefix="192.0.2.0/24")
        ACLAddressGroupMember.objects.create(address_group=group, member=prefix)
        response = self.client.get(self._get_detail_url(group), **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data["member_count"], 1)
        self.assertNotIn("acladdressgroupmembers", response.data)


class ACLAddressGroupMemberAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """
    API view test case for ACLAddressGroupMember.
    """

    model = ACLAddressGroupMember
    view_namespace = "plugins-api:netbox_acls"
    brief_fields = ["address_group", "display", "id", "url"]
    user_permissions = (
        "ipam.view_prefix",
        "netbox_acls.view_acladdressgroup",
    )

    @classmethod
    def setUpTestData(cls):
        """Set up ACL Address Group Member for API view testing."""

        # Address Group
        cls.group = ACLAddressGroup.objects.create(
            name="trusted",
        )
        cls.other_group = ACLAddressGroup.objects.create(
            name="other",
        )
        cls.v6_group = ACLAddressGroup.objects.create(
            name="v6",
            family=ACLAddressFamilyChoices.FAMILY_IPV6,
        )

        # Prefix
        cls.prefixes = [Prefix.objects.create(prefix=f"10.{number}.0.0/16") for number in range(1, 8)]

        cls.members = [
            ACLAddressGroupMember.objects.create(address_group=cls.group, member=prefix) for prefix in cls.prefixes[:3]
        ]

        cls.create_data = [
            {
                "address_group": cls.group.pk,
                "member_type": "ipam.prefix",
                "member_id": prefix.pk,
            }
            for prefix in cls.prefixes[3:6]
        ]
        cls.bulk_update_data = {
            "comments": "Reviewed",
        }
        cls.bulk_update_invalid_data = {
            "address_group": cls.v6_group.pk,
        }

    def test_member_id_only_patch_refreshes_cache(self):
        """Test that patching only the member ID moves the shadow reference with it."""
        self.add_permissions("netbox_acls.change_acladdressgroupmember")
        member = self.members[0]
        response = self.client.patch(
            self._get_detail_url(member),
            {"member_id": self.prefixes[6].pk},
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_200_OK)
        member.refresh_from_db()
        self.assertEqual(member.member, self.prefixes[6])
        cached = ACLAddressGroupMember.objects.filter(pk=member.pk).values("_member_prefix").get()
        self.assertEqual(cached["_member_prefix"], self.prefixes[6].pk)

    def test_parent_only_patch_preserves_member(self):
        """Test that patching only the address group leaves the member in place."""
        self.add_permissions("netbox_acls.change_acladdressgroupmember")
        member = self.members[0]
        response = self.client.patch(
            self._get_detail_url(member),
            {"address_group": self.other_group.pk},
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_200_OK)
        member.refresh_from_db()
        self.assertEqual(member.address_group, self.other_group)
        self.assertEqual(member.member, self.prefixes[0])

    def test_unlisted_member_type_patch_is_rejected(self):
        """Test that the API rejects a member type outside the address objects."""
        self.add_permissions("netbox_acls.change_acladdressgroupmember")
        response = self.client.patch(
            self._get_detail_url(self.members[0]),
            {"member_type": "netbox_acls.acladdressgroup", "member_id": self.group.pk},
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("member_type", response.data)

    def test_unknown_member_id_patch_is_rejected(self):
        """Test that the API rejects a member ID matching no object."""
        self.add_permissions("netbox_acls.change_acladdressgroupmember")
        response = self.client.patch(
            self._get_detail_url(self.members[0]),
            {"member_id": 999999},
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("member_id", response.data)

    def test_zero_member_id_patch_is_rejected(self):
        """Test that the API rejects a member ID of zero."""
        self.add_permissions("netbox_acls.change_acladdressgroupmember")
        response = self.client.patch(
            self._get_detail_url(self.members[0]),
            {"member_id": 0},
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("member", response.data)

    def test_null_member_id_patch_is_rejected(self):
        """Test that the API rejects a null member ID."""
        self.add_permissions("netbox_acls.change_acladdressgroupmember")
        response = self.client.patch(
            self._get_detail_url(self.members[0]),
            {"member_id": None},
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("member_id", response.data)

    def test_null_member_type_patch_is_rejected(self):
        """Test that the API rejects a null member type."""
        self.add_permissions("netbox_acls.change_acladdressgroupmember")
        response = self.client.patch(
            self._get_detail_url(self.members[0]),
            {"member_type": None},
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("member_type", response.data)

    def test_duplicate_member_patch_is_rejected(self):
        """Test that the API rejects moving a member onto an object already in the group."""
        self.add_permissions("netbox_acls.change_acladdressgroupmember")
        response = self.client.patch(
            self._get_detail_url(self.members[0]),
            {"member_id": self.prefixes[1].pk},
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("address_group", response.data)
        self.assertNotIn("__all__", response.data)

    def test_family_mismatch_patch_is_rejected(self):
        """Test that the API rejects moving a member to an address group of another family."""
        self.add_permissions("netbox_acls.change_acladdressgroupmember")
        response = self.client.patch(
            self._get_detail_url(self.members[0]),
            {"address_group": self.v6_group.pk},
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("__all__", response.data)

    def test_duplicate_post_is_rejected(self):
        """Test that the API rejects a second membership of the same object in a group."""
        self.add_permissions("netbox_acls.add_acladdressgroupmember")
        response = self.client.post(
            self._get_list_url(),
            {
                "address_group": self.group.pk,
                "member_type": "ipam.prefix",
                "member_id": self.prefixes[0].pk,
            },
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("address_group", response.data)
        self.assertNotIn("__all__", response.data)
