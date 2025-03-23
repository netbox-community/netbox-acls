from itertools import cycle

from dcim.models import Device
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from ipam.models import Prefix
from virtualization.models import VirtualMachine

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
    # device = Device.objects.first()

    def test_wrong_assigned_object_type_fail(self):
        """
        Test that AccessList cannot be assigned to an object type other than Device, VirtualChassis, VirtualMachine, or Cluster.
        """
        acl_bad_gfk = AccessList(
            name="TestACL_Wrong_GFK",
            assigned_object_type=ContentType.objects.get_for_model(Prefix),
            assigned_object_id=Prefix.objects.first(),
            **self.common_acl_params,
        )
        with self.assertRaises(ValidationError):
            acl_bad_gfk.full_clean()

    def test_alphanumeric_plus_success(self):
        """
        Test that AccessList names with alphanumeric characters, '_', or '-' pass validation.
        """
        acl_good_name = AccessList(
            name="Testacl-Good_Name-1",
            assigned_object_type=ContentType.objects.get_for_model(Device),
            assigned_object_id=1,  # TODO - replace with Device.objects.first()
            **self.common_acl_params,
        )
        acl_good_name.full_clean()
        # TODO: test_alphanumeric_plus_success - VirtualChassis, VirtualMachine & Cluster

    def test_duplicate_name_success(self):
        """
        Test that AccessList names can be non-unique if associated with different devices.
        """
        AccessList.objects.create(
            name="GOOD-DUPLICATE-ACL",
            assigned_object_type=ContentType.objects.get_for_model(Device),
            assigned_object_id=1,  # TODO - replace with Device.objects.first()
            **self.common_acl_params,
        )
        vm_acl = AccessList(
            name="GOOD-DUPLICATE-ACL",
            assigned_object_type=ContentType.objects.get_for_model(VirtualMachine),
            assigned_object_id=1,  # TODO - replace with VirtualMachine.objects.first().id,
            **self.common_acl_params,
        )
        vm_acl.full_clean()
        # TODO: test_duplicate_name_success - VirtualChassis, VirtualMachine & Cluster
        # vc_acl = AccessList(
        #    "name": "GOOD-DUPLICATE-ACL",
        #    assigned_object_type=ContentType.objects.get_for_model(VirtualChassis),
        #    **self.common_acl_params,
        # )
        # vc_acl.full_clean()

    def test_alphanumeric_plus_fail(self):
        """
        Test that AccessList names with non-alphanumeric (excluding '_' and '-') characters fail validation.
        """
        non_alphanumeric_plus_chars = " !@#$%^&*()[]{};:,./<>?\|~=+"

        for i, char in enumerate(non_alphanumeric_plus_chars, start=1):
            bad_acl_name = AccessList(
                name=f"Testacl-bad_name_{i}_{char}",
                assigned_object_type=ContentType.objects.get_for_model(Device),
                comments=f'ACL with "{char}" in name',
                **self.common_acl_params,
            )
            with self.assertRaises(ValidationError):
                bad_acl_name.full_clean()

    def test_duplicate_name_fail(self):
        """
        Test that AccessList names must be unique per device.
        """
        params = {
            "name": "FAIL-DUPLICATE-ACL",
            "assigned_object_type": ContentType.objects.get_for_model(Device),
            **self.common_acl_params,
            "assigned_object_id": 1,  # TODO - replace with Device.objects.first()
        }
        acl_1 = AccessList.objects.create(**params)
        acl_1.save()
        acl_2 = AccessList(**params)
        with self.assertRaises(ValidationError):
            acl_2.full_clean()
        # TODO: test_duplicate_name_fail - VirtualChassis & Cluster

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
                comments=f"VALID ACL CHOICES USED: {default_action=} {acl_type=}",
                type=acl_type,
                default_action=default_action,
                assigned_object_type=ContentType.objects.get_for_model(Device),
                assigned_object_id=1,  # TODO - replace with Device.objects.first()
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
            comments=f"INVALID ACL DEFAULT CHOICE USED: default_action='{invalid_acl_default_action_choice}'",
            type=valid_acl_types[0],
            default_action=invalid_acl_default_action_choice,
            assigned_object_type=ContentType.objects.get_for_model(Device),
            assigned_object_id=1,  # TODO - replace with Device.objects.first()
        )
        with self.assertRaises(ValidationError):
            invalid_acl_default_action.full_clean()

        valid_acl_default_action_choices = ["permit", "deny"]
        invalid_acl_type = "super-dupper-extended"
        invalid_acl_type = AccessList(
            name=f"TestACL_Valid_Choice_{valid_acl_default_action_choices[0]}_{invalid_acl_type}",
            comments=f"INVALID ACL DEFAULT CHOICE USED: type='{invalid_acl_type}'",
            type=invalid_acl_type,
            default_action=valid_acl_default_action_choices[0],
            assigned_object_type=ContentType.objects.get_for_model(Device),
            assigned_object_id=1,  # TODO - replace with Device.objects.first()
        )
        with self.assertRaises(ValidationError):
            invalid_acl_type.full_clean()
