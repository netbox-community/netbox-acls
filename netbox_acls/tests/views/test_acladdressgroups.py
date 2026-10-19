from django.test import override_settings

from utilities.testing import ViewTestCases, create_tags

from ...choices import ACLAddressFamilyChoices
from ...models import ACLAddressGroup
from .base import PluginViewTestCase


@override_settings(SESSION_ENGINE="django.contrib.sessions.backends.signed_cookies")
class ACLAddressGroupViewTestCase(PluginViewTestCase, ViewTestCases.PrimaryObjectViewTestCase):
    model = ACLAddressGroup

    @classmethod
    def setUpTestData(cls):
        cls.groups = [ACLAddressGroup.objects.create(name=f"group-{number}") for number in range(1, 4)]

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "group-4",
            "family": ACLAddressFamilyChoices.FAMILY_IPV6,
            "description": "Trusted clients",
            "comments": "",
            "tags": [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            "description": "Bulk edited",
        }

        cls.csv_data = (
            "name,family,description",
            "import-1,ipv4,First group",
            "import-2,ipv6,Second group",
            "import-3,ipv4,Third group",
        )

        cls.csv_update_data = (
            "id,description",
            f"{cls.groups[0].pk},Updated by import",
            f"{cls.groups[1].pk},Updated by import too",
        )
