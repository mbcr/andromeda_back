# Object-Level Permissions (OLP) Functions
from guardian.shortcuts import get_objects_for_user, get_perms_for_model
from django.contrib.contenttypes.models import ContentType

class OLP_Functions():
    def with_clearance(self, user):
        modelName = self.model.__name__
        appName = ContentType.objects.get_for_model(self.model).app_label
        permission_name = appName+'.'+'OLP_clearance_'+modelName
        return get_objects_for_user(user=user, perms=permission_name)