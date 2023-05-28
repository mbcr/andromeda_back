import requests
from django.conf import settings
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
# from rest_framework.response import Response

from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import HasChainVetAPIKey

from django.db import transaction
from pprint import pprint
from .models import Assessment
from .serializers import AssessmentSerializer
from apps.users.models import ChainVetAPIKey

class AssessmentView(APIView):
    permission_classes = [HasChainVetAPIKey]

    def post(self, request):
        # print("chainvet>views>AssessmentView>post>Received request.data:")
        # print(request.data)

        api_key = request.META.get("HTTP_X_API_KEY")
        try:
            api_key_instance = ChainVetAPIKey.objects.get_from_key(api_key)
            user = api_key_instance.user
            user_api_credits = user.api_credits

            if user_api_credits <= 0:
                return JsonResponse({"error": "Insufficient API credits"}, status=status.HTTP_402_PAYMENT_REQUIRED)

            if request.data['assessment_type'] == "address":
                direction = "withdrawal"
                address = request.data['address']
                name = "test_user"
                currency = request.data['currency']

                response = requests.post(
                    "https://apiexpert.crystalblockchain.com/monitor/tx/add",
                    headers={
                        "accept": "application/json",
                        "X-Auth-Apikey": settings.CRYSTAL_API_KEY
                    },
                    data= {
                        "direction": direction,
                        "address": address,
                        "name": name,
                        "currency": currency
                    }
                )
                print('chainvet>views>AssessmentView>Crystal API response:')
                pprint(response.json())

                if response.status_code != 200:
                    return JsonResponse({"error": "Unable to retrieve data from external API"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                response_data = response.json()
                with transaction.atomic():
                    user_api_credits -= 1
                    user.api_credits = user_api_credits
                    user.save()
                    new_assessment = Assessment(
                        assessment_id = response_data['data']['id'],
                        user = user,
                        type_of_assessment = "address",
                        response_data = response_data,
                        status_assessment = response_data['data']['status']
                    )
                    new_assessment.save()
                payload = {
                    "user_remaining_credits": user_api_credits,
                    "type": "address",
                    "hash": address,
                    "riskscore": response_data['data']['riskscore'],
                    "risk_signals": response_data['data']['signals']
                }

                return JsonResponse(payload, status=status.HTTP_200_OK)
                    
            elif request.data['assessment_type'] == "transaction":
                direction = "deposit"
                address = request.data['address']
                tx = request.data['transaction_hash']
                name = "test_user"
                currency = "eth"

                response = requests.post(
                    "https://apiexpert.crystalblockchain.com/monitor/tx/add",
                    headers={
                        "accept": "application/json",
                        "X-Auth-Apikey": settings.CRYSTAL_API_KEY
                    },
                    data= {
                        "direction": direction,
                        "address": address,
                        "tx": tx,
                        "name": name,
                        "currency": currency
                    }
                )
                print('chainvet>views>AssessmentView>Crystal API response:')
                pprint(response.json())
                print('...continuing...')

                if response.status_code != 200:
                    return JsonResponse({"error": "Unable to retrieve data from external API"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                response_data = response.json()
                new_assessment = Assessment(
                    assessment_id = response_data['data']['id'],
                    type_of_assessment = "address",
                    response_data = response_data,
                    status_assessment = response_data['data']['status']
                )
                new_assessment.save()
                payload = {
                    "type": "transaction",
                    "address": address,
                    "transaction_hash": tx,
                    "riskscore": response_data['data']['riskscore'],
                    "risk_signals": response_data['data']['signals']
                }

                return JsonResponse(payload, status=status.HTTP_200_OK)

            else:
                print('Invalid assessment type')
                return JsonResponse({"error": "Invalid assessment type"}, status=status.HTTP_400_BAD_REQUEST)
        
        except UserAPIKey.DoesNotExist:
            return Response({"detail": "Invalid API key."}, status=status.HTTP_403_FORBIDDEN)

        # return JsonResponse({"extra-info": "CACILDA!", "request_data": request.data}, status=status.HTTP_200_OK)

class CreateAPIKeyView(APIView):
    """
    A view that allows authenticated users to create new API keys.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        key_name = kwargs.get('api_key_name', '')
        api_key, key = ChainVetAPIKey.objects.create_key(name=key_name, user=self.request.user)
        return JsonResponse({"key": key}, status=status.HTTP_201_CREATED)


class DeleteAPIKeyView(APIView):
    """
    A view that allows authenticated users to delete an API key.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        api_key_prefix = kwargs.get('api_key_prefix', '')

        try:
            api_key = ChainVetAPIKey.objects.get(prefix=api_key_prefix, user=self.request.user)
            api_key.delete()
            return JsonResponse({},status=status.HTTP_204_NO_CONTENT)
        except ChainVetAPIKey.DoesNotExist:
            return JsonResponse({"detail": "API Key not found"}, status=status.HTTP_400_BAD_REQUEST)



