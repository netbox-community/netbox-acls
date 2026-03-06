from itertools import cycle

from django.core.exceptions import ValidationError

from netbox_acls.models import AccessList

from .base import BaseTestCase


class TestAccessList(BaseTestCase):
    """
    Test AccessList model.
    """

    common_acl_params = {
        "type": "extended",
        "default_action": "permit",
    }

    def test_accesslist_standard_creation(self):
        """
        Test that AccessList Standard creation passes validation.
        """
        acl_name = "Test-ACL-Standard-Type"

        created_acl = AccessList(
            name=acl_name,
            type="standard",
            default_action="deny",
        )

        self.assertTrue(isinstance(created_acl, AccessList), True)
        self.assertEqual(created_acl.name, acl_name)
        self.assertEqual(created_acl.type, "standard")
        self.assertEqual(created_acl.default_action, "deny")

    def test_accesslist_extended_creation(self):
        """
        Test that AccessList Extended creation passes validation.
        """
        acl_name = "Test-ACL-Extended-Type"

        created_acl = AccessList(
            name=acl_name,
            type="extended",
            default_action="permit",
        )

        self.assertTrue(isinstance(created_acl, AccessList))
        self.assertEqual(created_acl.name, acl_name)
        self.assertEqual(created_acl.type, "extended")
        self.assertEqual(created_acl.default_action, "permit")

    def test_alphanumeric_plus_success(self):
        """
        Test that AccessList names with alphanumeric characters, '_', or '-' pass validation.
        """
        acl_good_name = AccessList(
            name="Test-ACL-Good_Name-1",
            **self.common_acl_params,
        )
        acl_good_name.full_clean()

    def test_duplicate_name_success(self):
        """
        Test that AccessList names can be non-unique.
        """
        acl1 = AccessList(
            name="GOOD-DUPLICATE-ACL",
            **self.common_acl_params,
        )
        acl1.full_clean()

        acl2 = AccessList(
            name="GOOD-DUPLICATE-ACL",
            **self.common_acl_params,
        )
        acl2.full_clean()

    def test_valid_acl_choices(self):
        """
        Test that AccessList action choices using VALID choices.
        """
        valid_acl_default_action_choices = ["permit", "deny"]
        valid_acl_types = ["standard", "extended"]
        if len(valid_acl_default_action_choices) > len(valid_acl_types):
            valid_acl_choices = list(zip(valid_acl_default_action_choices, cycle(valid_acl_types)))
        elif len(valid_acl_default_action_choices) < len(valid_acl_types):
            valid_acl_choices = list(zip(cycle(valid_acl_default_action_choices), valid_acl_types))
        else:
            valid_acl_choices = list(zip(valid_acl_default_action_choices, valid_acl_types))

        for default_action, acl_type in valid_acl_choices:
            valid_acl_choice = AccessList(
                name=f"TestACL_Valid_Choice_{default_action}_{acl_type}",
                type=acl_type,
                default_action=default_action,
                comments=f"VALID ACL CHOICES USED: {default_action=} {acl_type=}",
            )
            valid_acl_choice.full_clean()

    def test_invalid_acl_choices(self):
        """
        Test that AccessList action choices using INVALID choices.
        """
        valid_acl_types = ["standard", "extended"]
        invalid_acl_default_action_choice = "log"
        invalid_acl_default_action = AccessList(
            name=f"TestACL_Valid_Choice_{invalid_acl_default_action_choice}_{valid_acl_types[0]}",
            type=valid_acl_types[0],
            default_action=invalid_acl_default_action_choice,
            comments=f"INVALID ACL DEFAULT CHOICE USED: default_action='{invalid_acl_default_action_choice}'",
        )
        with self.assertRaises(ValidationError):
            invalid_acl_default_action.full_clean()

        valid_acl_default_action_choices = ["permit", "deny"]
        invalid_acl_type = "super-dupper-extended"
        invalid_acl_type = AccessList(
            name=f"TestACL_Valid_Choice_{valid_acl_default_action_choices[0]}_{invalid_acl_type}",
            type=invalid_acl_type,
            default_action=valid_acl_default_action_choices[0],
            comments=f"INVALID ACL DEFAULT CHOICE USED: type='{invalid_acl_type}'",
        )
        with self.assertRaises(ValidationError):
            invalid_acl_type.full_clean()
