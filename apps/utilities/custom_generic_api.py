from django.db.models import Q
from django.http import JsonResponse
from ..logManager.handlers import log_request
from rest_framework import status

class CustomAPI:
    '''This class is meant to be used as a handle for its inner methods in order to facilitate the creation of APIs views.
    It should take a request object and a settings dictionary as arguments, and then it should be able to handle the request
    through its methods.
    The settings object should have the following format:
    {
        'api_name': str 'viewName',
        'object_name_from_front_end': 'examOfferPK' (used in the query_params of the request object)),
        'target_model': DataBase Model,
        'single_object_fetch_service': services.py function returning a {'data': object, 'status': int} object},
        'list_object_fetch_service': services.py function returning a list of objects,
        'model_form_fields_preparation_service': services.py function returning a list of objects with field data,
        'instance_creation_service': services.py function returning the new instance after creation,
        'handle_instance_update_service': services.py function returning nothing,
        'handle_instance_delete_service': services.py function returning nothing
    }'''

    def __init__(self, request, settings: dict):
        self.request = request
        self.settings = settings
        # print(f'CustomAPI.__init__ called with settings: {self.settings}')

    def get(self):
        if self.settings['object_name_from_front_end'] not in self.request.query_params:
            # Logic for a list of objects
            return_package = self.settings['list_object_fetch_service'](self.request)
            log_request(self.request,return_package['status'])
            return JsonResponse(return_package['data'], safe=False, status=return_package['status'])
        else:
            # Logic for a single object
            return_package = self.settings['single_object_fetch_service'](self.request)
            log_request(self.request,return_package['status'])
            return JsonResponse(return_package['data'], safe=False, status=return_package['status'])

    def post(self):
        if 'queryFormFields' in self.request.data: #Create response in case the post request is done for querying fields
            # print('clinic.views.get_available_exams_for_user_s_clinic API received POST request on queryFormFields mode.')
            # print('request.data:',self.request.data)
            model_form_fields = self.settings['model_form_fields_preparation_service'](self.request)
            #Add id field to all formFields, to act as a front-end handle (v-for)
            fieldCounter = 0
            for field in model_form_fields:
                field['id'] = fieldCounter
                fieldCounter+=1
            log_request(self.request,200)
            return JsonResponse(model_form_fields, status=200, safe=False)
        else: #Perform normal POST operations
            # print('Corporate_views_WorkAreaView received POST request.data:',request.data)
            new_instance = self.settings['instance_creation_service'](self.request)
            if new_instance == None:
                return JsonResponse({'data': 'Erro ao tentar salvar nova instância.'}, status=status.HTTP_400_BAD_REQUEST)
                
            try: 
                new_instance.save()
                return_package = self.settings['target_model_serializer'](new_instance)
                return JsonResponse(return_package, safe=False, status=201)
            except Exception as e:
                print('Error while trying to save new instance:',e)
                return JsonResponse({'data': 'Erro ao tentar salvar nova instância.'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self):
        return_package = self.settings['handle_instance_update_service'](self.request)
        log_request(self.request,return_package['status'])
        return JsonResponse(return_package['data'], safe=False, status=return_package['status'])

    def delete(self):
        print(f'clinic.views.{self.settings["api_name"]} received DELETE request.data:',self.request.query_params)
        if self.settings['object_name_from_front_end'] not in self.request.query_params:
            print(f'clinic.views.{self.settings["api_name"]} received DELETE request without the {self.settings["object_name_from_front_end"]} parameter.')
            return JsonResponse({'data': 'Nenhum exame foi excluído!'}, status=status.HTTP_400_BAD_REQUEST)
        
        service_return_package = self.settings['handle_instance_delete_service'](self.request)
        log_request(self.request,204)
        return JsonResponse({'data': service_return_package['data']}, status=service_return_package['status'])

    

    