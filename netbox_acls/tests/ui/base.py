"""Shared base test case for the declarative UI unit tests."""

from django.contrib.auth.context_processors import PermWrapper
from django.test import RequestFactory

from utilities.testing import TestCase


class UITestCase(TestCase):
    """Base for panel, attribute and action unit tests.

    A panel or action renders from a plain context dict rather than
    through a view round trip. self.user is created per test by
    utilities.testing.TestCase.setUp(), so grant permissions with
    self.add_permissions(...) before calling get_context().
    """

    factory = RequestFactory()

    def get_context(self, obj, **extra):
        """Return a request, object and perms context for a panel or action."""
        request = self.factory.get("/")
        request.user = self.user
        return {
            "request": request,
            "object": obj,
            "perms": PermWrapper(self.user),
            **extra,
        }
