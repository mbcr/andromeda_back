from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
import requests
from django.conf import settings

from pprint import pprint
from .models import Assessment
from .serializers import AssessmentSerializer

class AssessmentView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("chainvet>views>AssessmentView>post>Received request.data:")
        print(request.data)
        print(settings.CRYSTAL_API_KEY)

        if request.data['assessment_type'] == "address":
            direction = "withdrawal"
            address = request.data['hash']
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
                    "name": name,
                    "currency": currency
                }
            )
            print('chainvet>views>AssessmentView>Crystal API response:')
            pprint(response.json())
            print('...continuing...')

            if response.status_code == 200:
                response_data = response.json()
                new_assessment = Assessment(
                    assessment_id = response_data['data']['id'],
                    type_of_assessment = "address",
                    response_data = response_data,
                    status_assessment = response_data['data']['status']
                )
                new_assessment.save()
                payload = {
                    "type": "address",
                    "hash": address,
                    "riskscore": response_data['data']['riskscore'],
                    "risk_signals": response_data['data']['signals']
                }

                return JsonResponse(payload, status=status.HTTP_200_OK)
            else:
                return JsonResponse({"error": "Unable to retrieve data from external API"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif request.data.assessment_type == "transaction":
            print('Transaction check is not implemented yet')
            return JsonResponse({"error": "Address check is not implemented yet"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            print('Invalid assessment type')
            return JsonResponse({"error": "Invalid assessment type"}, status=status.HTTP_400_BAD_REQUEST)
        # serializer = AssessmentSerializer(data=request.data)

        # if serializer.is_valid():
        #     data = serializer.validated_data
        #     api_key = data['user']
        #     hash_value = data['response']['hash']  # assuming 'hash' is part of response

        #     # Make a POST request to the external API
        #     response = requests.post(
        #         "https://apiexpert.crystalblockchain.com/",
        #         headers={"Apikey": api_key},
        #         json={"type": data['type_of_assessment'], "hash": hash_value}
        #     )

        #     if response.status_code == 200:
        #         # If request to external API is successful, save the instance
        #         serializer.save()

        #         # Prepare and return the response
        #         return_data = {
        #             "type": data['type_of_assessment'],
        #             "hash": hash_value,
        #             "riskscore": response.json()['riskscore'],  # assuming 'riskscore' is part of API response
        #             "risk_signals": response.json()['risk_signals']  # assuming 'risk_signals' is part of API response
        #         }

        #         return JsonResponse(return_data, status=status.HTTP_200_OK)
            
        #     return JsonResponse({"error": "Unable to retrieve data from external API"}, status=status.HTTP_400_BAD_REQUEST)

        # return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse({"extra-info": "CACILDA!", "request_data": request.data}, status=status.HTTP_200_OK)
