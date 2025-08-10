"""
Defines each django model's GUI form to add or edit objects for each django model.
"""

from dcim.models import Device, Interface, Region, Site, SiteGroup, VirtualChassis
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from ipam.models import Prefix
from netbox.forms import NetBoxModelForm
from utilities.forms import (
    get_field_value,
)
from utilities.forms.fields import (
    CommentField,
    ContentTypeChoiceField,
    DynamicModelChoiceField,
)
from utilities.forms.rendering import FieldSet, TabbedGroups
from utilities.forms.widgets import HTMXSelect
from utilities.templatetags.builtins.filters import bettertitle
from virtualization.models import (
    Cluster,
    ClusterGroup,
    ClusterType,
    VirtualMachine,
    VMInterface,
)

from ..choices import ACLTypeChoices
from ..constants import ACL_RULE_SOURCE_DESTINATION_MODELS
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
help_text_acl_rule_index = "Determines the order of the rule in the ACL processing. AKA Sequence Number."


class AccessListForm(NetBoxModelForm):
    """
    GUI form to add or edit an AccessList.
    Requires a device, a name, a type, and a default_action.
    """

    # Device selector
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            "sites": "$site",
        },
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label="Site Group",
        initial_params={"sites": "$site"},
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={"region_id": "$region", "group_id": "$site_group"},
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
        query_params={"type_id": "$cluster_type"},
    )
    cluster = DynamicModelChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        query_params={"type_id": "$cluster_type", "group_id": "$cluster_group"},
    )

    virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        query_params={
            "cluster_id": "$cluster",
            "cluster_type_id": "$cluster_type",
            "cluster_group_id": "$cluster_group",
        },
    )
    comments = CommentField()

    fieldsets = (
        FieldSet(
            "name",
            "type",
            "default_action",
            "tags",
            name=_("Access List Details"),
        ),
        FieldSet(
            TabbedGroups(
                FieldSet(
                    "region",
                    "site_group",
                    "site",
                    "device",
                    name=_("Device"),
                ),
                FieldSet(
                    "virtual_chassis",
                    name=_("Virtual Chassis"),
                ),
                FieldSet(
                    "cluster_type",
                    "cluster_group",
                    "cluster",
                    "virtual_machine",
                    name=_("Virtual Machine"),
                ),
            ),
            name=_("Host Assignment"),
        ),
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
                "<b>*Note:</b> CANNOT be changed if ACL Rules are associated to this Access List.",
            ),
        }

    def __init__(self, *args, **kwargs):
        # Initialize helper selectors
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()
        if instance:
            if isinstance(instance.assigned_object, Device):
                initial["device"] = instance.assigned_object
                if instance.assigned_object.site:
                    initial["site"] = instance.assigned_object.site
                    if instance.assigned_object.site.group:
                        initial["site_group"] = instance.assigned_object.site.group

                    if instance.assigned_object.site.region:
                        initial["region"] = instance.assigned_object.site.region
            elif isinstance(instance.assigned_object, VirtualMachine):
                initial["virtual_machine"] = instance.assigned_object
                if instance.assigned_object.cluster:
                    initial["cluster"] = instance.assigned_object.cluster
                    if instance.assigned_object.cluster.group:
                        initial["cluster_group"] = instance.assigned_object.cluster.group

                    if instance.assigned_object.cluster.type:
                        initial["cluster_type"] = instance.assigned_object.cluster.type
            elif isinstance(instance.assigned_object, VirtualChassis):
                initial["virtual_chassis"] = instance.assigned_object

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
        super().clean()

        if self.errors.get("name"):
            return

        name = self.cleaned_data.get("name")
        acl_type = self.cleaned_data.get("type")
        device = self.cleaned_data.get("device")
        virtual_chassis = self.cleaned_data.get("virtual_chassis")
        virtual_machine = self.cleaned_data.get("virtual_machine")

        # Check if more than one host type selected.
        if (device and virtual_chassis) or (device and virtual_machine) or (virtual_chassis and virtual_machine):
            raise ValidationError(
                {
                    "__all__": (
                        "Access Lists must be assigned to one host at a time. Either a device, virtual chassis or "
                        "virtual machine."
                    ),
                },
            )

        # Check if no hosts selected.
        if not device and not virtual_chassis and not virtual_machine:
            raise ValidationError(
                {"__all__": "Access Lists must be assigned to a device, virtual chassis or virtual machine."}
            )

        existing_acls = None
        host_type = None
        if device:
            host_type = "device"
            existing_acls = AccessList.objects.filter(name=name, device=device).exists()
        elif virtual_machine:
            host_type = "virtual_machine"
            existing_acls = AccessList.objects.filter(name=name, virtual_machine=virtual_machine).exists()
        elif virtual_chassis:
            host_type = "virtual_chassis"
            existing_acls = AccessList.objects.filter(name=name, virtual_chassis=virtual_chassis).exists()

        # Check if duplicate entry.
        if ("name" in self.changed_data or host_type in self.changed_data) and existing_acls:
            error_same_acl_name = "An ACL with this name is already associated to this host."
            raise ValidationError({host_type: [error_same_acl_name], "name": [error_same_acl_name]})

        # Check if Access List has no existing rules before change the Access List's type.
        if self.instance.pk and (
            (acl_type == ACLTypeChoices.TYPE_EXTENDED and self.instance.aclstandardrules.exists())
            or (acl_type == ACLTypeChoices.TYPE_STANDARD and self.instance.aclextendedrules.exists())
        ):
            raise ValidationError({"type": ["This ACL has ACL rules associated, CANNOT change ACL type."]})

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

    fieldsets = (
        FieldSet(
            "access_list",
            "direction",
            "tags",
            name=_("Access List Details"),
        ),
        FieldSet(
            TabbedGroups(
                FieldSet(
                    "device",
                    "interface",
                    name=_("Device"),
                ),
                FieldSet(
                    "virtual_machine",
                    "vminterface",
                    name=_("Virtual Machine"),
                ),
            ),
            name=_("Interface Assignment"),
        ),
    )

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
        super().clean()

        error_message = {}
        access_list = self.cleaned_data.get("access_list")
        direction = self.cleaned_data.get("direction")
        interface = self.cleaned_data.get("interface")
        vminterface = self.cleaned_data.get("vminterface")

        # Check if both interface and vminterface are set.
        if interface and vminterface:
            error_too_many_interfaces = (
                "Access Lists must be assigned to one type of interface at a time (VM interface or physical interface)"
            )
            error_message |= {
                "interface": [error_too_many_interfaces],
                "vminterface": [error_too_many_interfaces],
            }
        elif not (interface or vminterface):
            error_no_interface = "An Access List assignment but specify an Interface or VM Interface."
            error_message |= {
                "interface": [error_no_interface],
                "vminterface": [error_no_interface],
            }
        else:
            # Define assigned_object, assigned_object_type, host_type, and host based on interface or vminterface
            if interface:
                assigned_object = interface
                assigned_object_type = "interface"
                host_type = "device"
                host = Interface.objects.get(pk=assigned_object.pk).device
            else:
                assigned_object = vminterface
                assigned_object_type = "vminterface"
                host_type = "virtual_machine"
                host = VMInterface.objects.get(pk=assigned_object.pk).virtual_machine

            assigned_object_id = assigned_object.pk
            assigned_object_type_id = ContentType.objects.get_for_model(assigned_object).pk
            access_list_host = AccessList.objects.get(pk=access_list.pk).assigned_object

            # Check that an interface's parent device/virtual_machine is assigned to the Access List.
            if access_list_host != host:
                error_acl_not_assigned_to_host = "Access List not present on selected host."
                error_message |= {
                    "access_list": [error_acl_not_assigned_to_host],
                    assigned_object_type: [error_acl_not_assigned_to_host],
                    host_type: [error_acl_not_assigned_to_host],
                }

            # Check for duplicate entry and existing ACL in the direction.
            existing_acl = ACLInterfaceAssignment.objects.filter(
                access_list=access_list,
                assigned_object_id=assigned_object_id,
                assigned_object_type=assigned_object_type_id,
                direction=direction,
            )
            if existing_acl.exists():
                error_duplicate_entry = "An ACL with this name is already associated to this interface & direction."
                error_message |= {
                    "access_list": [error_duplicate_entry],
                    "direction": [error_duplicate_entry],
                    assigned_object_type: [error_duplicate_entry],
                }

            if ACLInterfaceAssignment.objects.filter(
                assigned_object_id=assigned_object_id,
                assigned_object_type=assigned_object_type_id,
                direction=direction,
            ).exists():
                error_interface_already_assigned = "Interfaces can only have 1 Access List assigned in each direction."
                error_message |= {
                    "direction": [error_interface_already_assigned],
                    assigned_object_type: [error_interface_already_assigned],
                }

        if error_message:
            raise ValidationError(error_message)

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
            "type": ACLTypeChoices.TYPE_STANDARD,
        },
        help_text=mark_safe(
            "<b>*Note:</b> This field will only display Standard ACLs.",
        ),
        label="Access List",
    )

    # Source
    source_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        widget=HTMXSelect(),
        label=_("Source Type"),
        help_text=help_text_acl_rule_logic,
    )
    source = DynamicModelChoiceField(
        queryset=Prefix.objects.none(),  # Initial queryset
        selector=True,
        required=False,
        label=_("Source"),
        help_text=help_text_acl_rule_logic,
        disabled=True,
    )

    fieldsets = (
        FieldSet(
            "access_list",
            "description",
            "tags",
            name=_("Access List Details"),
        ),
        FieldSet(
            "index",
            "action",
            name=_("Rule Definition"),
        ),
        FieldSet(
            "remark",
            name=_("Remark"),
        ),
        FieldSet(
            "source_type",
            "source",
            name=_("Source Definition"),
        ),
    )

    class Meta:
        model = ACLStandardRule
        fields = (
            "access_list",
            "index",
            "action",
            "remark",
            "source_type",
            "tags",
            "description",
        )

        help_texts = {
            "index": help_text_acl_rule_index,
            "action": help_text_acl_action,
            "remark": mark_safe(
                "<b>*Note:</b> CANNOT be set if source OR action is set.",
            ),
        }

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the ACLStandardRuleForm.
        """

        # Initialize fields with initial values
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()

        if instance is not None and instance.source:
            # Initialize the source object field
            initial["source"] = instance.source

        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

        if source_type_id := get_field_value(self, "source_type"):
            try:
                # Retrieve the ContentType model class based on the source type
                source_type = ContentType.objects.get(pk=source_type_id)
                source_model = source_type.model_class()

                # Configure the queryset and label for the source field
                self.fields["source"].queryset = source_model.objects.all()
                self.fields["source"].widget.attrs["selector"] = source_model._meta.label_lower
                self.fields["source"].disabled = False
                self.fields["source"].label = _("Source " + bettertitle(source_model._meta.verbose_name))
            except ObjectDoesNotExist:
                pass

            # Clears the source field if the selected type changes
            if self.instance and self.instance.pk and source_type_id != self.instance.source_type_id:
                self.initial["source"] = None

    def clean(self):
        """
        Validate form fields for the ACL Standard Rule form.
        """
        super().clean()

        # Ensure the selected source object gets assigned
        self.instance.source = self.cleaned_data.get("source")


class ACLExtendedRuleForm(NetBoxModelForm):
    """
    GUI form to add or edit Extended Access List.
    Requires an access_list, an index, and ACL rule type.
    See the clean function for logic on other field requirements.
    """

    access_list = DynamicModelChoiceField(
        queryset=AccessList.objects.all(),
        query_params={
            "type": ACLTypeChoices.TYPE_EXTENDED,
        },
        help_text=mark_safe(
            "<b>*Note:</b> This field will only display Extended ACLs.",
        ),
        label="Access List",
    )

    # Source
    source_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        widget=HTMXSelect(),
        label=_("Source Type"),
        help_text=help_text_acl_rule_logic,
    )
    source = DynamicModelChoiceField(
        queryset=Prefix.objects.none(),  # Initial queryset
        selector=True,
        required=False,
        label=_("Source"),
        help_text=help_text_acl_rule_logic,
        disabled=True,
    )

    # Destination
    destination_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS),
        required=False,
        widget=HTMXSelect(),
        label=_("Destination Type"),
        help_text=help_text_acl_rule_logic,
    )
    destination = DynamicModelChoiceField(
        queryset=Prefix.objects.none(),  # Initial queryset
        selector=True,
        required=False,
        label=_("Destination"),
        help_text=help_text_acl_rule_logic,
        disabled=True,
    )

    fieldsets = (
        FieldSet(
            "access_list",
            "description",
            "tags",
            name=_("Access List Details"),
        ),
        FieldSet(
            "index",
            "action",
            name=_("Rule Definition"),
        ),
        FieldSet(
            "remark",
            name=_("Remark"),
        ),
        FieldSet(
            "protocol",
            name=_("Protocol"),
        ),
        FieldSet(
            "source_type",
            "source",
            "source_ports",
            name=_("Source Definition"),
        ),
        FieldSet(
            "destination_type",
            "destination",
            "destination_ports",
            name=_("Destination Definition"),
        ),
    )

    class Meta:
        model = ACLExtendedRule
        fields = (
            "access_list",
            "index",
            "action",
            "remark",
            "source_type",
            "source_ports",
            "destination_type",
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

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the ACLExtendedRuleForm.
        """

        # Initialize fields with initial values
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()

        if instance is not None and instance.source:
            # Initialize the source object field
            initial["source"] = instance.source
        if instance is not None and instance.destination:
            # Initialize the destination object field
            initial["destination"] = instance.destination

        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

        # Source
        if source_type_id := get_field_value(self, "source_type"):
            try:
                # Retrieve the ContentType model class based on the source type
                source_type = ContentType.objects.get(pk=source_type_id)
                source_model = source_type.model_class()

                # Configure the queryset and label for the source field
                self.fields["source"].queryset = source_model.objects.all()
                self.fields["source"].widget.attrs["selector"] = source_model._meta.label_lower
                self.fields["source"].disabled = False
                self.fields["source"].label = _("Source " + bettertitle(source_model._meta.verbose_name))
            except ObjectDoesNotExist:
                pass

            # Clears the source field if the selected type changes
            if self.instance and self.instance.pk and source_type_id != self.instance.source_type_id:
                self.initial["source"] = None

        # Destination
        if destination_type_id := get_field_value(self, "destination_type"):
            try:
                # Retrieve the ContentType model class based on the destination type
                destination_type = ContentType.objects.get(pk=destination_type_id)
                destination_model = destination_type.model_class()

                # Configure the queryset and label for the destination field
                self.fields["destination"].queryset = destination_model.objects.all()
                self.fields["destination"].widget.attrs["selector"] = destination_model._meta.label_lower
                self.fields["destination"].disabled = False
                self.fields["destination"].label = _("Destination " + bettertitle(destination_model._meta.verbose_name))
            except ObjectDoesNotExist:
                pass

            # Clears the destination field if the selected type changes
            if self.instance and self.instance.pk and destination_type_id != self.instance.destination_type_id:
                self.initial["destination"] = None

    def clean(self):
        """
        Validate form fields for the ACL Extended Rule form.
        """
        super().clean()

        # Ensure the selected source object gets assigned
        self.instance.source = self.cleaned_data.get("source")

        # Ensure the selected destination object gets assigned
        self.instance.destination = self.cleaned_data.get("destination")
