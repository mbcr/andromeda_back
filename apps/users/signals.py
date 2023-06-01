from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import Group

from . import models as userModels

from guardian.shortcuts import assign_perm
from guardian.core import ObjectPermissionChecker

#This Signal was removed as it demanded a connection of the person to a corporate before the employment existed. For this, I had initially created a new
#field in the Person model, but that generated a circular dependency between the Person and Corporate models. So I removed the signal and added the
#permission in the Employment's save method instead.
# @receiver(post_save, sender=userModels.Person)
# def addOLPermission_to_Person(sender, instance, **kwargs):
#     permissionBaseStr = 'OLP_clearance'
#     permissionName = permissionBaseStr+'_Person'
#     try:
#         corporate = instance.employments.first().businessUnit.company.corporateGroup
#     except:
#         try:
#             corporate = instance.user.corporate_group
#         except:
#             corporate = instance.latest_corporateGroup
#     groupName = 'client_'+corporate.nome.replace(' ','_').replace('C','c')
#     group = Group.objects.get(name=groupName)
#     permission_checker = ObjectPermissionChecker(group)
#     if not permission_checker.has_perm(permissionName, instance):
#         # print('adding permission to PastExam')
#         assign_perm(permissionName, group, instance)

@receiver(post_save, sender=userModels.CustomUser)
def notifySystemManagerOfNewUser(sender, instance, created, **kwargs):
    if created:
        from django.core.mail import send_mail
        from django.conf import settings
        subject = ('New user registration on Andromea')
        html_message = f'A new user ({instance.email}) has registered on Andromeda. \nPlease check the admin panel to issue correct permissions.\nhttps://andromeda-backend.herokuapp.com/admin/'
        plain_message = html_message
        from_email = settings.EMAIL_HOST_USER
        to = [settings.EMAIL_HOST_USER]
        send_mail(subject, plain_message, from_email, to, html_message=html_message)

