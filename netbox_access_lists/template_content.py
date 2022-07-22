
from django.contrib.contenttypes.models import ContentType
from extras.plugins import PluginTemplateExtension

from .models import AccessList, ACLInterfaceAssignment

__all__ = (
    'AccessLists',
    "ACLInterfaceAssignments",
    'DeviceAccessLists',
    'VirtualChassisAccessLists',
    'VMAccessLists',
    'DeviceACLInterfaceAssignments',
    'VMAACLInterfaceAssignments',
)


class ACLInterfaceAssignments(PluginTemplateExtension):

    def right_page(self):
        obj = self.context['object']

        acl_interface_assignments = None
        ctype = ContentType.objects.get_for_model(obj)
        if ctype.model == 'interface':
            acl_interface_assignments = ACLInterfaceAssignment.objects.filter(assigned_object_id=obj.pk, assigned_object_type=ctype)
        elif ctype.model == 'vminterface':
            acl_interface_assignments = ACLInterfaceAssignment.objects.filter(assigned_object_id=obj.pk, assigned_object_type=ctype)

        return self.render('inc/assigned_interface/access_lists.html', extra_context={
            'acl_interface_assignments': acl_interface_assignments,
            'type': ctype.model if ctype.model == 'device' else ctype.name.replace(' ', '_'),
        })


class AccessLists(PluginTemplateExtension):

    def right_page(self):
        obj = self.context['object']

        access_lists = None
        ctype = ContentType.objects.get_for_model(obj)
        if ctype.model == 'device':
            access_lists = AccessList.objects.filter(assigned_object_id=obj.pk, assigned_object_type=ctype)
        elif ctype.model == 'virtualchassis':
            access_lists = AccessList.objects.filter(assigned_object_id=obj.pk, assigned_object_type=ctype)
        elif ctype.model == 'virtualmachine':
            access_lists = AccessList.objects.filter(assigned_object_id=obj.pk, assigned_object_type=ctype)

        return self.render('inc/assigned_host/access_lists.html', extra_context={
            'access_lists': access_lists,
            'type': ctype.model if ctype.model == 'device' else ctype.name.replace(' ', '_'),
        })


class DeviceAccessLists(AccessLists):
    model = 'dcim.device'


class VirtualChassisAccessLists(AccessLists):
    model = 'dcim.virtualchassis'


class VMAccessLists(AccessLists):
    model = 'virtualization.virtualmachine'


class DeviceACLInterfaceAssignments(ACLInterfaceAssignments):
    model = 'dcim.interface'


class VMAACLInterfaceAssignments(ACLInterfaceAssignments):
    model = 'virtualization.vminterface'


template_extensions = [DeviceAccessLists, VirtualChassisAccessLists, VMAccessLists, DeviceACLInterfaceAssignments, VMAACLInterfaceAssignments]
