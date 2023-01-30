"""
Defines each django model's GUI form to add or edit objects for each django model.
"""

from dcim.models import Device, Interface, Region, Site, SiteGroup, VirtualChassis
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from ipam.models import Prefix
from netbox.forms import NetBoxModelForm
from utilities.forms import CommentField, DynamicModelChoiceField
from virtualization.models import (
    Cluster,
    ClusterGroup,
    ClusterType,
    VirtualMachine,
    VMInterface,
)

from ..choices import ACLTypeChoices
from .constants import (
    ERROR_MESSAGE_ACTION_REMARK_SOURCE_PREFIX_SET,
    ERROR_MESSAGE_NO_REMARK,
    ERROR_MESSAGE_REMARK_WITHOUT_ACTION_REMARK,
    HELP_TEXT_ACL_ACTION,
    HELP_TEXT_ACL_RULE_INDEX,
    HELP_TEXT_ACL_RULE_LOGIC,
)
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


class AccessListForm(NetBoxModelForm):
    """
    GUI form to add or edit an AccessList.
    Requires a device, a name, a type, and a default_action.
    """

    # Device selector
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

    # Virtual Chassis selector
    virtual_chassis = DynamicModelChoiceField(
        queryset=VirtualChassis.objects.all(),
        required=False,
        label="Virtual Chassis",
    )

    # Virtual Machine selector
    cluster_type = DynamicModelChoiceField(
        queryset=ClusterType.objects.all(),
        required=False,
    )

    cluster_group = DynamicModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        query_params={
            "type_id": "$cluster_type",
        },
    )

    cluster = DynamicModelChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        query_params={
            "type_id": "$cluster_type",
            "group_id": "$cluster_group",
        },
    )

    virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label="Virtual Machine",
        query_params={
            "cluster_type_id": "$cluster_type",
            "cluster_group_id": "$cluster_group",
            "cluster_id": "$cluster",
        },
    )

    comments = CommentField()

    class Meta:
        """
        Defines the Model and fields to be used by the form.
        """

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
        """
        Initializes the form
        """

        # Initialize helper selectors
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()
        if instance:
            if isinstance(instance.assigned_object, Device):
                initial["device"] = instance.assigned_object
            elif isinstance(instance.assigned_object, VirtualChassis):
                initial["virtual_chassis"] = instance.assigned_object
            elif isinstance(instance.assigned_object, VirtualMachine):
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
        # TODO: Refactor this method to fix error message logic.
        cleaned_data = super().clean()
        error_message = {}
        if self.errors.get("name"):
            return cleaned_data

        name = cleaned_data.get("name")
        acl_type = cleaned_data.get("type")

        # Check if more than one host type selected.
        host_types = self._get_host_types()

        # Check if no hosts selected.
        self._validate_host_types(host_types)

        host_type, host = host_types[0]

        # Check if duplicate entry.
        self._validate_duplicate_entry(name, host_type, host, error_message)
        # Check if Access List has no existing rules before change the Access List's type.
        self._validate_acl_type_change(acl_type, error_message)

        if error_message:
            raise forms.ValidationError(error_message)

        return cleaned_data

    def _get_host_types(self):
        """
        Get host type assigned to the Access List.
        """
        device = self.cleaned_data.get("device")
        virtual_chassis = self.cleaned_data.get("virtual_chassis")
        virtual_machine = self.cleaned_data.get("virtual_machine")
        host_types = [
            ("device", device),
            ("virtual_chassis", virtual_chassis),
            ("virtual_machine", virtual_machine),
        ]
        return [x for x in host_types if x[1]]

    def _validate_host_types(self, host_types):
        """
        Check number of host types selected.
        """
        if len(host_types) > 1:
            raise forms.ValidationError(
                "Access Lists must be assigned to one host (either a device, virtual chassis or virtual machine) at a time.",
            )
        # Check if no hosts selected.
        if not host_types:
            raise forms.ValidationError(
                "Access Lists must be assigned to a device, virtual chassis or virtual machine.",
            )

    def _validate_duplicate_entry(self, name, host_type, host, error_message):
        """
        Check if duplicate entry. (Because of GFK.)
        """
        existing_acls = AccessList.objects.filter(
            name=name, **{host_type: host}
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

    def _validate_acl_type_change(self, acl_type, error_message):
        """
        Check if Access List has no existing rules before change the Access List's type.
        """
        if self.instance.pk and (
            (
                acl_type == ACLTypeChoices.TYPE_EXTENDED
                and self.instance.aclstandardrules.exists()
            )
            or (
                acl_type == ACLTypeChoices.TYPE_STANDARD
                and self.instance.aclextendedrules.exists()
            )
        ):
            error_message["type"] = [
                "This ACL has ACL rules associated, CANNOT change ACL type.",
            ]

        if error_message:
            raise forms.ValidationError(error_message)

    def save(self, *args, **kwargs):
        """
        Set assigned object
        """
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
        # query_params={
        # Need to pass ACL device to it
        # },
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
        # query_params={
        # Need to pass ACL device to it
        # },
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

    def __init__(self, *args, **kwargs):
        """
        Initialize helper selectors
        """

        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()
        if instance:
            if isinstance(instance.assigned_object, Interface):
                initial["interface"] = instance.assigned_object
                initial["device"] = "device"
            elif isinstance(instance.assigned_object, VMInterface):
                initial["vminterface"] = instance.assigned_object
                initial["virtual_machine"] = "virtual_machine"
        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

    class Meta:
        """
        Defines the Model and fields to be used by the form.
        """

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
            - Check if neither interface nor vminterface are set.
            - Check that an interface's parent device/virtual_machine is assigned to the Access List.
            - Check that an interface's parent device/virtual_machine is assigned to the Access List.
            - Check for duplicate entry. (Because of GFK)
            - Check that the interface does not have an existing ACL applied in the direction already.
        """
        # Call the parent class's `clean` method
        cleaned_data = super().clean()

        # Get the interface types assigned to the Access List
        interface_types = self._get_interface_types()

        # Initialize an error message variable
        error_message = self._validate_interface_types(interface_types)

        if not error_message:
            assigned_object_type, assigned_object = interface_types[0]
            host_type = (
                "device" if assigned_object_type == "interface" else "virtual_machine"
            )

            # Get the parent host (device or virtual machine) of the assigned interface
            if assigned_object_type == "interface":
                host = Interface.objects.get(pk=assigned_object.pk).device
                assigned_object_id = Interface.objects.get(pk=assigned_object.pk).pk
            else:
                host = VMInterface.objects.get(pk=assigned_object.pk).virtual_machine
                assigned_object_id = VMInterface.objects.get(pk=assigned_object.pk).pk

            # Get the ContentType id for the assigned object
            assigned_object_type_id = ContentType.objects.get_for_model(
                assigned_object
            ).pk

        if not error_message:
            # Check if the parent host is assigned to the Access List
            error_message |= self._check_if_interface_parent_is_assigned_to_access_list(
                cleaned_data.get("access_list"), assigned_object_type, host_type, host
            )

        if not error_message:
            # Check for duplicate entries in the Access List
            error_message |= self._check_for_duplicate_entry(
                cleaned_data.get("access_list"),
                assigned_object_id,
                assigned_object_type_id,
                cleaned_data.get("direction"),
            )

        if not error_message:
            # Check if the interface already has an ACL applied in the specified direction
            error_message |= self._check_if_interface_already_has_acl_in_direction(
                assigned_object_id,
                assigned_object_type_id,
                cleaned_data.get("direction"),
            )

        if error_message:
            raise forms.ValidationError(error_message)
        else:
            return cleaned_data

    def _get_interface_types(self):
        """
        Get interface type/model assigned to the Access List.
        """
        interface = self.cleaned_data.get("interface")
        vminterface = self.cleaned_data.get("vminterface")
        interface_types = [
            ("interface", interface),
            ("vminterface", vminterface),
        ]
        return [x for x in interface_types if x[1]]

    def _validate_interface_types(self, interface_types):
        """
        Check if number of interface type selected is 1.
        """
        # Check if more than 1 hosts selected.
        if len(interface_types) > 1:
            return "Assignment can only be to one interface at a time (either a interface or vm_interface)."
        # Check if no hosts selected.
        elif not interface_types:
            return "No interface or vm_interface selected."
        else:
            return {}

    def _check_if_interface_parent_is_assigned_to_access_list(
        self, access_list, assigned_object_type, host_type, host
    ):
        """
        Check that an interface's parent device/virtual_machine is assigned to the Access List.
        """

        access_list_host = AccessList.objects.get(pk=access_list.pk).assigned_object

        if access_list_host != host:
            ERROR_ACL_NOT_ASSIGNED_TO_HOST = "Access List not present on selected host."
            return {
                "access_list": [ERROR_ACL_NOT_ASSIGNED_TO_HOST],
                assigned_object_type: [ERROR_ACL_NOT_ASSIGNED_TO_HOST],
                host_type: [ERROR_ACL_NOT_ASSIGNED_TO_HOST],
            }
        else:
            return {}

    def _check_for_duplicate_entry(
        self, access_list, assigned_object_id, assigned_object_type_id, direction
    ):
        """
        Check for duplicate entry. (Because of GFK)
        """

        if ACLInterfaceAssignment.objects.filter(
            access_list=access_list,
            assigned_object_id=assigned_object_id,
            assigned_object_type=assigned_object_type_id,
            direction=direction,
        ).exists():
            return {"access_list": ["Duplicate entry."]}
        else:
            return {}

    def _check_if_interface_already_has_acl_in_direction(
        self, assigned_object_id, assigned_object_type_id, direction
    ):
        """
        Check that the interface does not have an existing ACL applied in the direction already.
        """
        if not ACLInterfaceAssignment.objects.filter(
            assigned_object_id=assigned_object_id,
            assigned_object_type=assigned_object_type_id,
            direction=direction,
        ).exists():
            return {}

        error_interface_already_assigned = (
            "Interfaces can only have 1 Access List assigned in each direction."
        )
        return {
            "direction": [error_interface_already_assigned],
            assigned_object_type: [error_interface_already_assigned],
        }

    def save(self, *args, **kwargs):
        """
        Set assigned object
        """
        self.instance.assigned_object = self.cleaned_data.get(
            "interface",
        ) or self.cleaned_data.get("vminterface")
        return super().save(*args, **kwargs)


class BaseACLRuleForm(NetBoxModelForm):
    """GUI form to add or edit Access List Rules to be inherited by other classes"""

    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        query_params={
            "type": ACLTypeChoices.TYPE_STANDARD,
        },
        help_text=mark_safe(
            "<b>*Note:</b> This field will only display Standard ACLs."
        ),
        label="Access List",
    )
    source_prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        help_text=HELP_TEXT_ACL_RULE_LOGIC,
        label="Source Prefix",
    )

    fieldsets = (
        ("Access List Details", ("access_list", "description", "tags")),
        ("Rule Definition", ("index", "action", "remark", "source_prefix")),
    )

    class Meta:
        """Defines the Model and fields to be used by the form."""

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
            "action": HELP_TEXT_ACL_ACTION,
            "destination_ports": HELP_TEXT_ACL_RULE_LOGIC,
            "index": HELP_TEXT_ACL_RULE_INDEX,
            "protocol": HELP_TEXT_ACL_RULE_LOGIC,
            "remark": mark_safe(
                "<b>*Note:</b> CANNOT be set if action is not set to remark."
            ),
            "source_ports": HELP_TEXT_ACL_RULE_LOGIC,
        }

    def clean(self):
        cleaned_data = super().clean()
        error_message = {}

        # No need to check for unique_together since there is no usage of GFK

        if cleaned_data.get("action") == "remark":
            self._extracted_from_clean_20(cleaned_data, error_message, "extended")
        # Check remark set, but action not set to remark.
        elif cleaned_data.get("remark"):
            error_message["remark"] = [ERROR_MESSAGE_REMARK_WITHOUT_ACTION_REMARK]

        if error_message:
            raise forms.ValidationError(error_message)
        return cleaned_data

    def _extracted_from_clean_20(self, cleaned_data, error_message, rule_type):
        """
        Validates form inputs before submitting:
          - Check if action set to remark, but no remark set.
          - Check if action set to remark, but source_prefix set.
          - Check if action set to remark, but source_ports set.
          - Check if action set to remark, but destination_prefix set.
          - Check if action set to remark, but destination_ports set.
          - Check if action set to remark, but destination_ports set.
          - Check if action set to remark, but protocol set.
        """
        # Check if action set to remark, but no remark set.
        if not cleaned_data.get("remark"):
            error_message["remark"] = [ERROR_MESSAGE_NO_REMARK]
        # Check if action set to remark, but source_prefix set.
        if cleaned_data.get("source_prefix"):
            error_message["source_prefix"] = [
                ERROR_MESSAGE_ACTION_REMARK_SOURCE_PREFIX_SET
            ]
        if rule_type == "extended":
            # Check if action set to remark, but source_ports set.
            if cleaned_data.get("source_ports"):
                error_message["source_ports"] = [
                    "Action is set to remark, Source Ports CANNOT be set."
                ]
            # Check if action set to remark, but destination_prefix set.
            if cleaned_data.get("destination_prefix"):
                error_message["destination_prefix"] = [
                    "Action is set to remark, Destination Prefix CANNOT be set.",
                ]
            # Check if action set to remark, but destination_ports set.
            if cleaned_data.get("destination_ports"):
                error_message["destination_ports"] = [
                    "Action is set to remark, Destination Ports CANNOT be set."
                ]
            # Check if action set to remark, but protocol set.
            if cleaned_data.get("protocol"):
                error_message["protocol"] = [
                    "Action is set to remark, Protocol CANNOT be set."
                ]


class ACLStandardRuleForm(BaseACLRuleForm):
    """
    GUI form to add or edit Standard Access List.
    Requires an access_list, an index, and ACL rule type.
    See the clean function for logic on other field requirements.
    """


class ACLExtendedRuleForm(BaseACLRuleForm):
    """
    GUI form to add or edit Extended Access List.
    Requires an access_list, an index, and ACL rule type.
    See the clean function for logic on other field requirements.
    """

    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        query_params={"type": ACLTypeChoices.TYPE_EXTENDED},
        help_text=mark_safe(
            "<b>*Note:</b> This field will only display Extended ACLs.",
        ),
        label="Access List",
    )

    destination_prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        help_text=HELP_TEXT_ACL_RULE_LOGIC,
        label="Destination Prefix",
    )
    fieldsets = BaseACLRuleForm.fieldsets[:-1] + (
        (
            "Rule Definition",
            BaseACLRuleForm.fieldsets[-1][1]
            + ("source_ports", "destination_prefix", "destination_ports", "protocol"),
        ),
    )

    class Meta:
        """Defines the Model and fields to be used by the form."""

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
