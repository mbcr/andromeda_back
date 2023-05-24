from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
import requests

from .models import Assessment
from .serializers import AssessmentSerializer

class AssessmentView(APIView):
    def post(self, request):
        print("CACILDA!")
        print(request.data)
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
        return JsonResponse({"info": "CACILDA!", "data": request.data}, status=status.HTTP_200_OK)
