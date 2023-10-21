from ..featureAccessControl.models import Authorisation
from django.http import HttpResponseForbidden

def feature_access_required(view_func):
    '''This is a custom wrapper function that is used to wrap views in a Django web application.
    The purpose of this wrapper is to provide a layer of security and access control to the views it wraps.
    The wrapper checks whether the user accessing the view has the appropriate authorization to access the feature, either by having the permission themselves
    or by belonging to a corporate group that has the permission.
    The access codes should be stored in the database in the FeatureAccessCode model, and authorisation instances saved for each connection.
    '''

    def wrapped_view(request, *args, **kwargs):
        view_name = view_func.__name__
        request_method = request.method
        feature_access_code = f"{view_func.__module__.split('.')[1]}_{view_name}_{request_method}"
        
        user = request.user
        corporate_group = user.corporate_group if hasattr(user, 'corporate_group') else None
        
        user_has_access = user.authorisations.filter(feature_code__code=feature_access_code, active=True).count() > 0
        if corporate_group:
            company_has_access = corporate_group.authorisations.filter(feature_code__code=feature_access_code, active=True).count() > 0
        else:
            company_has_access = False
        access_granted = user_has_access or company_has_access
        
        if not access_granted:
            print(f'User does not have the access code required to use this feature: {feature_access_code}')
            return HttpResponseForbidden()
        return view_func(request, *args, **kwargs)
    return wrapped_view

def feature_access_required_v2(view_has_access_control_function:bool=False, access_control_settings:dict=None):
    '''This is a custom wrapper function that is used to wrap views in a Django web application.
    It takes two arguments to process quantitative access control functions (quotas, credits, time-limitation).
    The wrapper checks whether the user accessing the view has the appropriate authorization to access the feature, then calls the access control function if it exists to grant access or not.
    The access codes for the feature access should be stored in the database in the FeatureAccessCode model, and authorisation instances saved for each connection.
    The models and functions to control access can be existing apps, or a new app to centralise the access control functions.
    '''

    def wrap(view_func):
        def wrapped_view(request, *args, **kwargs):
            view_name = view_func.__name__
            request_method = request.method
            feature_access_code = f"{view_func.__module__.split('.')[1]}_{view_name}_{request_method}"
            
            user = request.user
            corporate_group = user.corporate_group if hasattr(user, 'corporate_group') else None
            
            user_has_access = user.authorisations.filter(feature_code__code=feature_access_code, active=True).count() > 0
            if corporate_group:
                company_has_access = corporate_group.authorisations.filter(feature_code__code=feature_access_code, active=True).count() > 0
            else:
                company_has_access = False
            access_granted = user_has_access or company_has_access
            
            if not access_granted:
                print(f'User does not have the access code required to use this feature: {feature_access_code}')
                return HttpResponseForbidden()
            
            if view_has_access_control_function:
                if access_control_settings is None:
                    print(f'The view {view_name} has credit controls imposed, but no credit control settings were provided.')
                    return HttpResponseForbidden()

                access_processing_function = access_control_settings['access_processing_function']
                ap_function_settings = access_control_settings['ap_function_settings']
                ap_function_granted_access = access_processing_function(request, *ap_function_settings)
                if not ap_function_granted_access:
                    print(f'User was not granted access to use this feature by the Access Control Function of The view {view_name}.')
                    return HttpResponseForbidden()
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return wrap


