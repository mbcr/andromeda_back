from django.shortcuts import render

from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view

from ..users import models as userModels
# from ..corporate import models as corporateModels
from ..logManager.handlers import log_request

from pprint import pprint

@api_view(['GET','PUT'])
def UserDetails(request):
    if request.method == 'GET':
        customUser = None
        if request and hasattr(request, "user"):
            customUser = request.user
            # customUser = userModels.CustomUser.objects.get(pk = request.query_params.get('userPK'))
            # Fetch the Person associated with the User
            person = userModels.Person.objects.get(user = customUser) #customUser already qualifies the query regarding permissions
            # Initiate response package
            responsePackage = {}
            # Add Person details to response package
            responsePackage['person'] = {
                'first_name': person.primeiroNome,
                'surnames': person.sobrenomes,
                'personalEmail': person.email,
                'cpf': person.cpf,
                'id': person.id,
            }
            # Add User details to response package
            responsePackage['user'] = {
                'first_name': customUser.first_name,
                'last_name': customUser.last_name,
                'email': customUser.email,
                'start_date': f'{str(customUser.start_date.day)}/{str(customUser.start_date.month)}/{str(customUser.start_date.year)}',
                'tier': customUser.tier(),
            }
            log_request(request, 200)
            return JsonResponse(responsePackage, safe=True, status=200)
        else:
            print('No user registered in the request. ERROR CODE: DT8784 sent with response.')
            returnMessage = 'A solicitação não inclui um usuário. Favor realizar o login com credenciais adequadas. Código Erro: DT8784'
            log_request(request, 204)
            return JsonResponse(returnMessage, safe=True, status=204)
    if request.method == 'PUT':
        # Get the data from the request
        requestData = request.data
        # pprint(requestData)
        new_firstName = requestData['person']['first_name']
        new_lastName = requestData['user']['last_name']
        new_personalEmail = requestData['person']['personalEmail']
        new_corporateEmail = requestData['user']['email']
        new_cpf = requestData['person']['cpf']
        # Update the CustomUser model with the new data
        customUser = request.user
        # print('CustomUser: ', customUser)
        customUser.first_name = new_firstName
        customUser.last_name = new_lastName
        customUser.email = new_corporateEmail
        customUser.save()
        # Update the Person model with the new data
        person = userModels.Person.objects.get(user = customUser)
        person.primeiroNome = new_firstName
        person.sobrenomes = new_lastName
        person.email = new_personalEmail
        person.cpf = new_cpf
        person.save()
        # Return the updated data
        responsePackage = {}
        responsePackage['person'] = {
            'first_name': person.primeiroNome,
            'surnames': person.sobrenomes,
            'personalEmail': person.email,
            'cpf': person.cpf,
            'id': person.id,
        }
        responsePackage['user'] = {
            'first_name': customUser.first_name,
            'last_name': customUser.last_name,
            'email': customUser.email,
            'start_date': customUser.start_date,
        }
        log_request(request, 200)
        return JsonResponse(responsePackage, safe=True, status=200)

@api_view(['GET'])
def UserTier(request):
    try:
        user = request.user
    except:
        responsePackage = {
            'user_has_tier': False,
        }
        log_request(request, 204)
        return JsonResponse(responsePackage, safe=True, status=204)
    
    user_tier = user.tier()
    responsePackage = {
        'user_has_tier': True,
        'tier': user_tier
    }
    log_request(request, 200)
    return JsonResponse(responsePackage, safe=True, status=200)





