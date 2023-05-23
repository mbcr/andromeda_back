from pprint import pprint

from apps.featureAccessControl.models import FeatureAccessCode, Authorisation
from apps.users.models import CustomUser
from apps.corporate.models import Corporate

#----------------- Functions for handling feature access permission START -----------------#

def add_all_access_codes_to(target:CustomUser)->None:
    if not isinstance(target, CustomUser):
        raise ValueError("The target argument must be a CustomUser instance.")

    try:
        handler = CustomUser.objects.get(email='marcos.ramos@crcapital.com.br')
    except CustomUser.DoesNotExist:
        raise ValueError("The user appointed to be the handler of the function does not exist.")
    
    try:
        access_codes = FeatureAccessCode.objects.all()
    except FeatureAccessCode.DoesNotExist:
        raise ValueError("No FeatureAccessCode instances exist in the database.")

    for access_code in access_codes:
        Authorisation.objects.get_or_create(
            feature_code=access_code,
            user=target if isinstance(target, CustomUser) else None,
            # company=target if isinstance(target, Corporate) else None,
            created_by = handler
        )

def add_list_of_codes_to(target:CustomUser, codes:list)->None:
    if not isinstance(target, CustomUser):
        raise ValueError("The target argument must be a CustomUser instance.")

    try:
        handler = CustomUser.objects.get(email='marcos@cliquemed.app')
    except CustomUser.DoesNotExist:
        raise ValueError("The user appointed to be the handler of the function does not exist.")
    
    try:
        access_codes = FeatureAccessCode.objects.filter(code__in=codes)
    except FeatureAccessCode.DoesNotExist:
        raise ValueError("No FeatureAccessCode instances exist in the database.")
    
    for access_code in access_codes:
        Authorisation.objects.get_or_create(
            feature_code=access_code,
            user=target if isinstance(target, CustomUser) else None,
            # company=target if isinstance(target, Corporate) else None,
            active=True,
            created_by = handler
        )

def create_feature_access_codes_for_all_view_functions():
    import os

    from apps.featureAccessControl.models import FeatureAccessCode
    from apps.users.models import CustomUser

    def get_function_names(directory: str) -> list:
        function_names = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('views.py'):
                    file_path = os.path.join(root, file)
                    app_name = file_path.split("\\")[-2]
                    # app_name = file_path.split("/")[-2] # For Linux Systems
                    with open(os.path.join(root, file)) as f:
                        for line in f:
                            if line.startswith('def'):
                                function_name = line.split('(')[0].split()[1]
                                function_names.append(f'{app_name}_{function_name}')
        return function_names

    def extend_function_names_with_methods(function_names: list)-> list:
        method_names = ['GET','POST','PUT','DELETE']
        extended_function_names = []
        for function_name in function_names:
            for method_name in method_names:
                extended_function_names.append(f'{function_name}_{method_name}')
        return extended_function_names

    def create_non_existing_access_codes(access_codes:list)->None:
        user = CustomUser.objects.get(email='marcos.ramos@crcapital.com.br')
        for access_code in access_codes:
            get_or_create = FeatureAccessCode.objects.get_or_create(
                code=access_code,
                created_by = user,
            )
            if get_or_create[1]:
                print(f'Created access code {access_code}')

    # Get the absolute path to the directory containing the manage.py file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(script_dir, '..')
    # Join the base directory with the name of the "apps" folder
    apps_directory = os.path.join(base_dir, 'apps')

    # For Linux Systems
    # apps_directory = os.path.join(script_dir, 'apps')

    function_names = get_function_names(apps_directory)
    functions_to_remove = [
        'logManager_log_landing_page_usage',
        'medicalRequests_get_testing_object',
    ]
    function_names = [function_name for function_name in function_names if function_name not in functions_to_remove]
    access_codes = extend_function_names_with_methods(function_names)
    create_non_existing_access_codes(access_codes)

def delete_all_authorisations_from(target:CustomUser)->None:
    target_s_authorisations = target.authorisations.all()
    for authorisation in target_s_authorisations:
        authorisation.delete()
    
def print_access_codes_for(target:CustomUser)->None:
    target_s_authorisations = target.authorisations.all().filter(active=True)
    if target_s_authorisations.count() == 0:
        print(f'The target {target} has no access codes.')
        return
    for authorisation in target_s_authorisations:
        print(authorisation.feature_code.code)

def set_tier_for_target(target:CustomUser, tier: int)->None:

    tier_handling = {
        1: Tier_1().access_codes,
        2: Tier_2().access_codes,
        3: Tier_3().access_codes(),
    }

    def set_tier(tier):
        delete_all_authorisations_from(target)
        add_list_of_codes_to(target, tier_handling[tier])
    
    if tier in tier_handling.keys():
        set_tier(tier)
    else:
        raise ValueError(f'The tier {tier} does not exist.')

#----------------- Functions for handling feature access permission END -----------------#


#----------------- Classes to organise tiers START -----------------#
class Tier_1:
    access_codes = [
        'clinic_get_all_standard_exams_GET',
        'clinic_get_results_for_exam_search_GET',

        'corporate_CorporateEntitiesInfo_GET',
        'corporate_ExamPlanner_WorkForce_GET',
        'corporate_ExamPlanner_ExamsAndBudget_GET',
        'corporate_preLoadCatalogue_GET',

        'userCreditControl_get_search_credits_v1_GET',
    ]

class Tier_2:
    access_codes = [
        'clinic_get_all_standard_exams_GET',
        'clinic_get_results_for_exam_search_GET',
        'clinic_public_exams_from_clinic_pk_GET',

        'corporate_CorporateEntitiesInfo_GET',
        'corporate_ExamPlanner_WorkForce_GET',
        'corporate_ExamPlanner_ExamsAndBudget_GET',
        'corporate_preLoadCatalogue_GET',

        'corporate_BusinessUnitView2_GET',
        'corporate_WorkAreaView_GET',
        'corporate_WorkAreaFuncionariosView_GET',
        'corporate_WorkAreaExamesView_GET',
        'corporate_EmployeesView_GET',
        'corporate_EmployeeDetailView_GET',
        'corporate_EmployeePastExams_GET',
        'medicalRequests_appointments_api_v1_GET',
        'medicalRequests_examRequests_api_v1_GET',
        'medicalRequests_medicalRequests_api_v1_GET',
        'medicalRequests_medicalRequests_api_v1_POST',

        'userCreditControl_get_search_credits_v1_GET',
    ]

class Tier_3:
    def access_codes(self):
        all_access_codes = FeatureAccessCode.objects.all()
        access_codes = []
        for access_code in all_access_codes:
            access_codes.append(access_code.code)
        return access_codes
#----------------- Classes to organise tiers END -----------------#


#-------------------------------------- RUN --------------------------------------#
def run():
    # create_feature_access_codes_for_all_view_functions()
    target = CustomUser.objects.get(email='marcos@cliquemed.app')
    print(f'Target {target} has tier {target.tier()}.')
    set_tier_for_target(target,3)
    print(f'Target {target} has tier {target.tier()}.')

    print('.')
    print('.')
    print('.')
    print('Finished!')