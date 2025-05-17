from django.urls import reverse
from rest_framework import status
from utilities.testing import APITestCase


class AppTest(APITestCase):
    def test_root(self):
        """Test the API root view."""
        url = reverse("plugins-api:netbox_acls-api:api-root")
        response = self.client.get(f"{url}?format=api", **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
