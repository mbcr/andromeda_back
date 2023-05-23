from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.contenttypes.fields import GenericForeignKey

# from ..clinic import models as clinic_models
# from ..corporate import models as corporate_models
from ..utilities.olpFunctions import OLP_Functions


from pprint import pprint

class CustomAccountManager(BaseUserManager):
    
    def create_superuser(self, email, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        # #Create Person object associated with this superuser
        # This functions calls create_user, which is already creating an associated Person

        return self.create_user(email, password, **other_fields)

    def create_user(self, email, password, **other_fields):
        # def create_new_organisation(organisation:dict) -> clinic_models.Clinic | corporate_models.Corporate:
        #     organisation_type = organisation['organisation_type']
        #     if organisation_type == 'corporate':
        #         if not organisation['organisation_name']:
        #             organisation['organisation_name'] = f'CorporateFrom[{email}]'
        #         #Create a corporate for the user
        #         new_organisation = corporate_models.Corporate(
        #             nome = organisation['organisation_name'],
        #             search_credits_daily = 10,
        #         )
        #         new_organisation.save()
        #     elif organisation_type == 'clinic':
        #         if not organisation['organisation_name']:
        #             organisation['organisation_name'] = f'ClinicFrom[{email}]'
        #         clinic_city_str = organisation['organisation_city']
        #         clinic_city_name = clinic_city_str.split(',')[0].strip()
        #         clinic_city_uf_str = clinic_city_str.split(',')[1].strip()
        #         clinic_city_uf = clinic_models.UnidadeFederacao.objects.get(uf=clinic_city_uf_str)
        #         clinic_city = clinic_models.Municipio.objects.get(nome=clinic_city_name, uf=clinic_city_uf)
        #         #Create a clinic for the user
        #         new_organisation = clinic_models.Clinic(
        #             nome = organisation['organisation_name'],
        #             endereco_municipio = clinic_city,
        #             endereco_uf = clinic_city_uf,
        #             email = email,
        #         )
        #         new_organisation.save()
        #     return new_organisation

        if not email:
            raise ValueError(_('You must provide an email address'))

        # organisation = other_fields.get('registration_form')
        # organisation_type = organisation['organisation_type']
        # new_organisation = create_new_organisation(organisation)

        email = self.normalize_email(email)
        user = self.model(email=email, **other_fields)
        user.set_password(password)
        
        #Save user and associated person
        user.save()
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    start_date = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    # roles = models.ManyToManyField(to='users.Role') #<---CONFIRM
    # corporate_group = models.ForeignKey(to='corporate.Corporate', on_delete=models.SET_NULL, null=True, blank=True)
    # clinic_group = models.ForeignKey(to='clinic.Clinic', on_delete=models.SET_NULL, null=True, blank=True)
    registration_form = models.JSONField(null=True, blank=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['registration_form']

    def __str__(self):
        return self.email

    def set_tier(self, tier):
        from scripts.feature_access_control import set_tier_for_target
        set_tier_for_target(self, tier)

    def tier(self):
        from scripts.feature_access_control import Tier_1, Tier_2
        tier_1_access_count = len(Tier_1().access_codes)
        tier_2_access_count = len(Tier_2().access_codes)
        user_s_authorisations = self.authorisations.all().filter(active=True)
        authorisations_count = user_s_authorisations.count()
        if authorisations_count > (tier_2_access_count+5):
            return 3
        if authorisations_count > (tier_1_access_count):
            return 2
        if authorisations_count == tier_1_access_count:
            return 1
        return 0
        
    def add_to_group(self, group_name):
        from django.contrib.auth.models import Group
        group = Group.objects.get(name=group_name)
        self.groups.add(group)
        


# class Role(models.Model):
#   '''
#   https://simpleisbetterthancomplex.com/tutorial/2018/01/18/how-to-implement-multiple-user-types-with-django.html
#   '''
#   Ghost = 0
#   Patient = 1
#   EmployeeCorporate = 2
#   EmployeeClinic = 2
#   MedicalCorporateDoctor = 3
#   MedicalClinicDoctor = 4
#   MedicalCorporateNurse = 5
#   MedicalClinicNurse = 6
#   ManagerCorporate = 7
#   ManagerClinic = 8

#   ROLE_CHOICES = (
#     (Ghost, 'Ghost'),
#     (Patient, 'Patient'),
#     (EmployeeCorporate, 'EmployeeCorporate'),
#     (ManagerCorporate, 'ManagerCorporate'),
#     (ManagerClinic, 'ManagerClinic'),
#     #   (EmployeeClinic, 'EmployeeClinic'),
#     #   (MedicalCorporateDoctor, 'MedicalCorporateDoctor'),
#     #   (MedicalClinicDoctor, 'MedicalClinicDoctor'),
#     #   (MedicalCorporateNurse, 'MedicalCorporateNurse'),
#     #   (MedicalClinicNurse, 'MedicalClinicNurse'),
#   )

#   id = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, primary_key=True)

#   def __str__(self):
#       return self.get_id_display()

# class PersonManager(models.Manager, OLP_Functions):
#     pass

# class Person(models.Model):
#     ## Independent fields
#     primeiroNome = models.CharField(max_length=32, null=True)
#     sobrenomes = models.CharField(max_length=128, null=True)
#     email = models.EmailField(null=True)
#     cpf =  models.CharField(max_length=11, null=True)
#     is_user = models.BooleanField(null=True)
#     user = models.ForeignKey(to='users.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
#     # latest_corporateGroup = models.ForeignKey(to='corporate.Corporate', on_delete=models.SET_NULL, null=True, blank=True, related_name='latest_corporateGroup')

#     ## Computed fields (refactor update_computed_and_cache_fields after any alteration)

#     ## Cache fields (refactor update_computed_and_cache_fields after any alteration)

#     ## Instance control fields
#     created_at = models.DateTimeField(auto_now_add=True)
#     created_by = models.ForeignKey(to='users.CustomUser', on_delete=models.SET_NULL, null=True, related_name='created_by')

#     objects = PersonManager()

#     def __str__(self) :
#         return f"{self.primeiroNome} {self.sobrenomes}"

#     def save(self, *args, **kwargs):
#         first_save = self.pk is None
#         if first_save:
#             self.update_computed_and_cache_fields()
#             super().save(*args, **kwargs)
#         else:
#             self.update_computed_and_cache_fields()
#             super().save(*args, **kwargs)

#     def delete(self, *args, **kwargs):
#         self.active = False
#         self.deleted_at = datetime.now()
#         self.save()
    
#     class Meta:
#         permissions = [
#             ('OLP_clearance_Person', 'Object level permission handle')
#         ]

#     def update_computed_and_cache_fields(self):
#         pass

#     def fullName(self):
#         return self.primeiroNome+' '+self.sobrenomes
