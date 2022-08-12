"""
Defines each django model's GUI form to add or edit objects for each django model.
"""

from dcim.models import Device, Interface, Region, Site, SiteGroup, VirtualChassis
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from extras.models import Tag
from ipam.models import Prefix
from netbox.forms import NetBoxModelForm
from utilities.forms import (
    CommentField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
)
from virtualization.models import VirtualMachine, VMInterface

from ..models import (
    AccessList,
    ACLExtendedRule,
    ACLInterfaceAssignment,
    ACLStandardRule,
)

__all__ = (
    "AccessListForm",
    "ACLInterfaceAssignmentForm",
    "ACLStandardRuleForm",
    "ACLExtendedRuleForm",
)

# Sets a standard mark_safe help_text value to be used by the various classes
help_text_acl_rule_logic = mark_safe(
    "<b>*Note:</b> CANNOT be set if action is set to remark.",
)
# Sets a standard help_text value to be used by the various classes for acl action
help_text_acl_action = "Action the rule will take (remark, deny, or allow)."
# Sets a standard help_text value to be used by the various classes for acl index
help_text_acl_rule_index = (
    "Determines the order of the rule in the ACL processing. AKA Sequence Number."
)

# Sets a standard error message for ACL rules with an action of remark, but no remark set.
error_message_no_remark = "Action is set to remark, you MUST add a remark."
# Sets a standard error message for ACL rules with an action of remark, but no source_prefix is set.
error_message_action_remark_source_prefix_set = (
    "Action is set to remark, Source Prefix CANNOT be set."
)
# Sets a standard error message for ACL rules with an action not set to remark, but no remark is set.
error_message_remark_without_action_remark = (
    "CANNOT set remark unless action is set to remark."
)


class AccessListForm(NetBoxModelForm):
    """
    GUI form to add or edit an AccessList.
    Requires a device, a name, a type, and a default_action.
    """

    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label="Site Group",
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            "region_id": "$region",
            "group_id": "$site_group",
        },
    )
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            "region_id": "$region",
            "group_id": "$site_group",
            "site_id": "$site",
        },
    )
    virtual_chassis = DynamicModelChoiceField(
        queryset=VirtualChassis.objects.all(),
        required=False,
        label="Virtual Chassis",
    )
    virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label="Virtual Machine",
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
    )

    class Meta:
        model = AccessList
        fields = (
            "region",
            "site_group",
            "site",
            "device",
            "virtual_machine",
            "virtual_chassis",
            "name",
            "type",
            "default_action",
            "comments",
            "tags",
        )
        help_texts = {
            "default_action": "The default behavior of the ACL.",
            "name": "The name uniqueness per device is case insensitive.",
            "type": mark_safe(
                "<b>*Note:</b> CANNOT be changed if ACL Rules are assoicated to this Access List.",
            ),
        }

    def __init__(self, *args, **kwargs):

        # Initialize helper selectors
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()
        if instance:
            if type(instance.assigned_object) is Device:
                initial["device"] = instance.assigned_object
            elif type(instance.assigned_object) is VirtualChassis:
                initial["virtual_chassis"] = instance.assigned_object
            elif type(instance.assigned_object) is VirtualMachine:
                initial["virtual_machine"] = instance.assigned_object
        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

    def clean(self):
        """
        Validates form inputs before submitting:
          - Check if more than one host type selected.
          - Check if no hosts selected.
          - Check if duplicate entry. (Because of GFK.)
          - Check if Access List has no existing rules before change the Access List's type.
        """
        cleaned_data = super().clean()
        error_message = {}
        if self.errors.get("name"):
            return cleaned_data
        name = cleaned_data.get("name")
        acl_type = cleaned_data.get("type")
        device = cleaned_data.get("device")
        virtual_chassis = cleaned_data.get("virtual_chassis")
        virtual_machine = cleaned_data.get("virtual_machine")

        # Check if more than one host type selected.
        if (
            (device and virtual_chassis)
            or (device and virtual_machine)
            or (virtual_chassis and virtual_machine)
        ):
            raise forms.ValidationError(
                "Access Lists must be assigned to one host (either a device, virtual chassis or virtual machine) at a time.",
            )
        # Check if no hosts selected.
        if not device and not virtual_chassis and not virtual_machine:
            raise forms.ValidationError(
                "Access Lists must be assigned to a device, virtual chassis or virtual machine.",
            )

        if device:
            host_type = "device"
            existing_acls = AccessList.objects.filter(name=name, device=device).exists()
        elif virtual_chassis:
            host_type = "virtual_chassis"
            existing_acls = AccessList.objects.filter(
                name=name,
                virtual_chassis=virtual_chassis,
            ).exists()
        elif virtual_machine:
            host_type = "virtual_machine"
            existing_acls = AccessList.objects.filter(
                name=name,
                virtual_machine=virtual_machine,
            ).exists()

        # Check if duplicate entry.
        if (
            "name" in self.changed_data or host_type in self.changed_data
        ) and existing_acls:
            error_same_acl_name = (
                "An ACL with this name is already associated to this host."
            )
            error_message |= {
                host_type: [error_same_acl_name],
                "name": [error_same_acl_name],
            }
        # Check if Access List has no existing rules before change the Access List's type.
        if (acl_type == "extended" and self.instance.aclstandardrules.exists()) or (
            acl_type == "standard" and self.instance.aclextendedrules.exists()
        ):
            error_message["type"] = [
                "This ACL has ACL rules associated, CANNOT change ACL type.",
            ]

        if error_message:
            raise forms.ValidationError(error_message)

        return cleaned_data

    def save(self, *args, **kwargs):
        # Set assigned object
        self.instance.assigned_object = (
            self.cleaned_data.get("device")
            or self.cleaned_data.get("virtual_chassis")
            or self.cleaned_data.get("virtual_machine")
        )

        return super().save(*args, **kwargs)


class ACLInterfaceAssignmentForm(NetBoxModelForm):
    """
    GUI form to add or edit ACL Host Object assignments
    Requires an access_list, a name, a type, and a default_action.
    """

    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            # Need to pass ACL device to it
        },
    )
    interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        query_params={
            "device_id": "$device",
        },
    )
    virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label="Virtual Machine",
    )
    vminterface = DynamicModelChoiceField(
        queryset=VMInterface.objects.all(),
        required=False,
        query_params={
            "virtual_machine_id": "$virtual_machine",
        },
        label="VM Interface",
    )
    # virtual_chassis = DynamicModelChoiceField(
    #    queryset=VirtualChassis.objects.all(),
    #    required=False,
    #    label='Virtual Chassis',
    # )
    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        # query_params={
        #    'assigned_object': '$device',
        #    'assigned_object': '$virtual_machine',
        # },
        label="Access List",
        help_text=mark_safe(
            "<b>*Note:</b> Access List must be present on the device already.",
        ),
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
    )

    def __init__(self, *args, **kwargs):

        # Initialize helper selectors
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()
        if instance:
            if type(instance.assigned_object) is Interface:
                initial["interface"] = instance.assigned_object
                initial["device"] = "device"
            elif type(instance.assigned_object) is VMInterface:
                initial["vminterface"] = instance.assigned_object
                initial["virtual_machine"] = "virtual_machine"
        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

    class Meta:
        model = ACLInterfaceAssignment
        fields = (
            "access_list",
            "direction",
            "device",
            "interface",
            "virtual_machine",
            "vminterface",
            "comments",
            "tags",
        )
        help_texts = {
            "direction": mark_safe(
                "<b>*Note:</b> CANNOT assign 2 ACLs to the same interface & direction.",
            ),
        }

    def clean(self):
        """
        Validates form inputs before submitting:
          - Check if both interface and vminterface are set.
          - Check if neither interface or vminterface are set.
          - Check that an interface's parent device/virtual_machine is assigned to the Access List.
          - Check that an interface's parent device/virtual_machine is assigned to the Access List.
          - Check for duplicate entry. (Because of GFK)
          - Check that the interface does not have an existing ACL applied in the direction already.
        """
        cleaned_data = super().clean()
        error_message = {}
        access_list = cleaned_data.get("access_list")
        direction = cleaned_data.get("direction")
        interface = cleaned_data.get("interface")
        vminterface = cleaned_data.get("vminterface")
        assigned_object = cleaned_data.get("assigned_object")
        if interface:
            assigned_object = interface
            assigned_object_type = "interface"
            host_type = "device"
            host = Interface.objects.get(pk=assigned_object.pk).device
        elif vminterface:
            assigned_object = vminterface
            assigned_object_type = "vminterface"
            host_type = "virtual_machine"
            host = VMInterface.objects.get(pk=assigned_object.pk).virtual_machine
        if interface or vminterface:
            assigned_object_id = VMInterface.objects.get(pk=assigned_object.pk).pk
            assigned_object_type_id = ContentType.objects.get_for_model(
                assigned_object,
            ).pk
        access_list_host = AccessList.objects.get(pk=access_list.pk).assigned_object

        # Check if both interface and vminterface are set.
        if interface and vminterface:
            error_too_many_interfaces = "Access Lists must be assigned to one type of interface at a time (VM interface or physical interface)"
            error_too_many_hosts = "Access Lists must be assigned to one type of device at a time (VM or physical device)."
            error_message |= {
                "device": [error_too_many_hosts],
                "interface": [error_too_many_interfaces],
                "virtual_machine": [error_too_many_hosts],
                "vminterface": [error_too_many_interfaces],
            }
        # Check if neither interface or vminterface are set.
        elif not (interface or vminterface):
            error_no_interface = (
                "An Access List assignment but specify an Interface or VM Interface."
            )
            error_message |= {
                "interface": [error_no_interface],
                "vminterface": [error_no_interface],
            }
        # Check that an interface's parent device/virtual_machine is assigned to the Access List.
        elif access_list_host != host:
            error_acl_not_assigned_to_host = "Access List not present on selected host."
            error_message |= {
                "access_list": [error_acl_not_assigned_to_host],
                assigned_object_type: [error_acl_not_assigned_to_host],
                host_type: [error_acl_not_assigned_to_host],
            }
        # Check for duplicate entry.
        elif ACLInterfaceAssignment.objects.filter(
            access_list=access_list,
            assigned_object_id=assigned_object_id,
            assigned_object_type=assigned_object_type_id,
            direction=direction,
        ).exists():
            error_duplicate_entry = "An ACL with this name is already associated to this interface & direction."
            error_message |= {
                "access_list": [error_duplicate_entry],
                "direction": [error_duplicate_entry],
                assigned_object_type: [error_duplicate_entry],
            }
        # Check that the interface does not have an existing ACL applied in the direction already.
        elif ACLInterfaceAssignment.objects.filter(
            assigned_object_id=assigned_object_id,
            assigned_object_type=assigned_object_type_id,
            direction=direction,
        ).exists():
            error_interface_already_assigned = (
                "Interfaces can only have 1 Access List assigned in each direction."
            )
            error_message |= {
                "direction": [error_interface_already_assigned],
                assigned_object_type: [error_interface_already_assigned],
            }

        if error_message:
            raise forms.ValidationError(error_message)
        return cleaned_data

    def save(self, *args, **kwargs):
        # Set assigned object
        self.instance.assigned_object = self.cleaned_data.get(
            "interface",
        ) or self.cleaned_data.get("vminterface")

        return super().save(*args, **kwargs)


class ACLStandardRuleForm(NetBoxModelForm):
    """
    GUI form to add or edit Standard Access List.
    Requires an access_list, an index, and ACL rule type.
    See the clean function for logic on other field requirements.
    """

    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        query_params={
            "type": "standard",
        },
        help_text=mark_safe(
            "<b>*Note:</b> This field will only display Standard ACLs.",
        ),
        label="Access List",
    )
    source_prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        help_text=help_text_acl_rule_logic,
        label="Source Prefix",
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
    )

    fieldsets = (
        ("Access List Details", ("access_list", "description", "tags")),
        ("Rule Definition", ("index", "action", "remark", "source_prefix")),
    )

    class Meta:
        model = ACLStandardRule
        fields = (
            "access_list",
            "index",
            "action",
            "remark",
            "source_prefix",
            "tags",
            "description",
        )
        help_texts = {
            "index": help_text_acl_rule_index,
            "action": help_text_acl_action,
            "remark": mark_safe(
                "<b>*Note:</b> CANNOT be set if source prefix OR action is set.",
            ),
        }

    def clean(self):
        """
        Validates form inputs before submitting:
          - Check if action set to remark, but no remark set.
          - Check if action set to remark, but source_prefix set.
          - Check remark set, but action not set to remark.
        """
        cleaned_data = super().clean()
        error_message = {}

        # No need to check for unique_together since there is no usage of GFK

        if cleaned_data.get("action") == "remark":
            # Check if action set to remark, but no remark set.
            if not cleaned_data.get("remark"):
                error_message["remark"] = [error_message_no_remark]
            # Check if action set to remark, but source_prefix set.
            if cleaned_data.get("source_prefix"):
                error_message["source_prefix"] = [
                    error_message_action_remark_source_prefix_set,
                ]
        # Check remark set, but action not set to remark.
        elif cleaned_data.get("remark"):
            error_message["remark"] = [error_message_remark_without_action_remark]

        if error_message:
            raise forms.ValidationError(error_message)
        return cleaned_data


class ACLExtendedRuleForm(NetBoxModelForm):
    """
    GUI form to add or edit Extended Access List.
    Requires an access_list, an index, and ACL rule type.
    See the clean function for logic on other field requirements.
    """

    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        query_params={
            "type": "extended",
        },
        help_text=mark_safe(
            "<b>*Note:</b> This field will only display Extended ACLs.",
        ),
        label="Access List",
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
    )
    source_prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        help_text=help_text_acl_rule_logic,
        label="Source Prefix",
    )
    destination_prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        help_text=help_text_acl_rule_logic,
        label="Destination Prefix",
    )
    fieldsets = (
        ("Access List Details", ("access_list", "description", "tags")),
        (
            "Rule Definition",
            (
                "index",
                "action",
                "remark",
                "source_prefix",
                "source_ports",
                "destination_prefix",
                "destination_ports",
                "protocol",
            ),
        ),
    )

    class Meta:
        model = ACLExtendedRule
        fields = (
            "access_list",
            "index",
            "action",
            "remark",
            "source_prefix",
            "source_ports",
            "destination_prefix",
            "destination_ports",
            "protocol",
            "tags",
            "description",
        )
        help_texts = {
            "action": help_text_acl_action,
            "destination_ports": help_text_acl_rule_logic,
            "index": help_text_acl_rule_index,
            "protocol": help_text_acl_rule_logic,
            "remark": mark_safe(
                "<b>*Note:</b> CANNOT be set if action is not set to remark.",
            ),
            "source_ports": help_text_acl_rule_logic,
        }

    def clean(self):
        """
        Validates form inputs before submitting:
          - Check if action set to remark, but no remark set.
          - Check if action set to remark, but source_prefix set.
          - Check if action set to remark, but source_ports set.
          - Check if action set to remark, but destination_prefix set.
          - Check if action set to remark, but destination_ports set.
          - Check if action set to remark, but destination_ports set.
          - Check if action set to remark, but protocol set.
          - Check remark set, but action not set to remark.
        """
        cleaned_data = super().clean()
        error_message = {}

        # No need to check for unique_together since there is no usage of GFK

        if cleaned_data.get("action") == "remark":
            # Check if action set to remark, but no remark set.
            if not cleaned_data.get("remark"):
                error_message["remark"] = [error_message_no_remark]
            # Check if action set to remark, but source_prefix set.
            if cleaned_data.get("source_prefix"):
                error_message["source_prefix"] = [
                    error_message_action_remark_source_prefix_set,
                ]
            # Check if action set to remark, but source_ports set.
            if cleaned_data.get("source_ports"):
                error_message["source_ports"] = [
                    "Action is set to remark, Source Ports CANNOT be set.",
                ]
            # Check if action set to remark, but destination_prefix set.
            if cleaned_data.get("destination_prefix"):
                error_message["destination_prefix"] = [
                    "Action is set to remark, Destination Prefix CANNOT be set.",
                ]
            # Check if action set to remark, but destination_ports set.
            if cleaned_data.get("destination_ports"):
                error_message["destination_ports"] = [
                    "Action is set to remark, Destination Ports CANNOT be set.",
                ]
            # Check if action set to remark, but protocol set.
            if cleaned_data.get("protocol"):
                error_message["protocol"] = [
                    "Action is set to remark, Protocol CANNOT be set.",
                ]
        # Check if action not set to remark, but remark set.
        elif cleaned_data.get("remark"):
            error_message["remark"] = [error_message_remark_without_action_remark]

        if error_message:
            raise forms.ValidationError(error_message)
        return cleaned_data
