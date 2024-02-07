from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, ChainVetAPIKey, AccessCode, Affiliate, ConfigVariable

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as origGroupAdmin
from django.contrib.auth.models import Group, User


class GroupAdminForm(forms.ModelForm):
    """
    ModelForm that adds an additional multiple select field for managing
    the users in the group.
    """
    users = forms.ModelMultipleChoiceField(
        CustomUser.objects.all(),
        widget=admin.widgets.FilteredSelectMultiple('Users', False),
        required=False,
        )


    def __init__(self, *args, **kwargs):
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            initial_users = self.instance.user_set.values_list('pk', flat=True)
            self.initial['users'] = initial_users


    def save(self, *args, **kwargs):
        kwargs['commit'] = True
        return super(GroupAdminForm, self).save(*args, **kwargs)


    def save_m2m(self):
        self.instance.user_set.clear()
        self.instance.user_set.add(*self.cleaned_data['users'])

class GroupAdmin(origGroupAdmin):
    """
    Customized GroupAdmin class that uses the customized form to allow
    management of users within a group.
    """
    form = GroupAdminForm

# Register the modified GroupAdmin with the admin site
admin.site = admin.AdminSite(name='my_admin')
# admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
admin.site.register(AccessCode)
admin.site.register(ChainVetAPIKey)
admin.site.register(Affiliate)
admin.site.register(ConfigVariable)

# class RoleAdminForm(forms.ModelForm):
# ''' Attempt to make role alternatives to be displayed. It didn't work.'''
#     class Meta:
#         model = Role
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         forms.ModelForm.__init__(self, *args, **kwargs)
#         self.fields['roles'].queryset = Role.objects.all()


class UserAdminConfig(UserAdmin):
    model = CustomUser
    search_fields = ('email',)
    list_filter = ('email', 'is_active', 'is_staff')
    ordering = ('-start_date',)
    list_display = ('email',
                    'is_active', 'is_staff',)
    # form = RoleAdminForm # Attempt to make role alternatives to be displayed. It didn't work.

    fieldsets = (
        (None, 
        {'fields': ('email','credits_available')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_active', 'is_staff'),
            'list': ('roles',),
            }
         ),
    )
admin.site.register(CustomUser, UserAdminConfig)