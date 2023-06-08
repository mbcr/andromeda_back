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
from .models import Assessment
from .serializers import AssessmentSerializer, AssessmentListSerializer
from apps.users.models import ChainVetAPIKey

from pprint import pprint
from datetime import datetime

class AssessmentCreateWIthAPIKeyView(APIView):
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

            name = "test_user"
            address = request.data['address']
            currency = request.data['currency']

            if request.data['assessment_type'] == "address":
                direction = "withdrawal"
                bcb_request_data = {
                    "direction": direction,
                    "address": address,
                    "name": name,
                    "currency": currency
                }
            elif request.data['assessment_type'] == "transaction":
                direction = "deposit"
                tx = request.data['transaction_hash']
                bcb_request_data = {
                    "direction": direction,
                    "address": address,
                    "tx": tx,
                    "name": name,
                    "currency": currency                
                }
            else:
                print('Invalid assessment type')
                return JsonResponse({"error": "Invalid assessment type"}, status=status.HTTP_400_BAD_REQUEST)

            response = requests.post(
                "https://apiexpert.crystalblockchain.com/monitor/tx/add",
                headers={
                    "accept": "application/json",
                    "X-Auth-Apikey": settings.CRYSTAL_API_KEY
                },
                data= bcb_request_data
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
                updated_at_datetime = datetime.utcfromtimestamp(response_data['data']['updated_at'])
                new_assessment = Assessment(
                    assessment_updated_at = updated_at_datetime,
                    currency = currency,
                    address_hash = address,
                    user = user,
                    type_of_assessment = "address",
                    response_data = response_data,

                    risk_grade = response_data['data']['alert_grade'],
                    risk_score = response_data['data']['riskscore'],
                    risk_signals = response_data['data']['signals'],
                    status_assessment = response_data['data']['status'],
                    assessment_id = response_data['data']['id'],
                )
                if request.data['assessment_type'] == "transaction":
                    new_assessment.type_of_assessment = "transaction"
                    new_assessment.transaction_hash = tx
                    new_assessment.transaction_volume_coin = response_data['data']['amount']
                    new_assessment.transaction_volume_fiat = response_data['data']['fiat']
                    new_assessment.transaction_volume_fiat_currency_code = response_data['data']['fiat_code_effective']
                    new_assessment.risk_volume_coin = response_data['data']['risky_volume']
                    new_assessment.risk_volume_fiat = response_data['data']['risky_volume_fiat']
                new_assessment.save()
            payload = {
                "user_remaining_credits": user_api_credits,
                "type": "address",
                "hash": address,
                "assessment_status": response_data['data']['status'],
                "risk_grade": response_data['data']['alert_grade'],
                "risk_score": response_data['data']['riskscore'],
                "risk_signals": response_data['data']['signals']
            }
            if request.data['assessment_type'] == "transaction":
                payload['type'] = "transaction"
                payload['transaction_hash'] = tx
                payload['risk_volume_coin'] = response_data['data']['risky_volume']
                payload['risk_volume_fiat'] = response_data['data']['risky_volume_fiat']
                payload['risk_volume_fiat_currency_code'] = response_data['data']['fiat_code_effective']

            return JsonResponse(payload, status=status.HTTP_200_OK)
        
        except ChainVetAPIKey.DoesNotExist:
            return Response({"detail": "Invalid API key."}, status=status.HTTP_403_FORBIDDEN)

class AssessmentCreateWIthUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # print("chainvet>views>AssessmentView>post>Received request.data:")
        # print(request.data)

        api_key = request.META.get("HTTP_X_API_KEY")
        user = request.user
        user_api_credits = user.api_credits

        if user_api_credits <= 0:
            return JsonResponse({"error": "Insufficient API credits"}, status=status.HTTP_402_PAYMENT_REQUIRED)

        name = 'test_user'
        address = request.data['address']
        currency = request.data['currency']

        if request.data['assessment_type'] == "address":
            direction = "withdrawal"
            bcb_request_data = {
                "direction": direction,
                "address": address,
                "name": name,
                "currency": currency
            }
        elif request.data['assessment_type'] == "transaction":
            direction = "deposit"
            tx = request.data['transaction_hash']
            bcb_request_data = {
                "direction": direction,
                "address": address,
                "tx": tx,
                "name": name,
                "currency": currency                
            }
        else:
            print('Invalid assessment type')
            return JsonResponse({"error": "Invalid assessment type"}, status=status.HTTP_400_BAD_REQUEST)

        response = requests.post(
            "https://apiexpert.crystalblockchain.com/monitor/tx/add",
            headers={
                "accept": "application/json",
                "X-Auth-Apikey": settings.CRYSTAL_API_KEY
            },
            data= bcb_request_data
        )
        print('chainvet>views>AssessmentView>Crystal API response:')
        pprint(response.json())

        if response.status_code != 200:
            error_message = response.json()['meta']['error_message']
            return JsonResponse({"error": "Unable to retrieve data from external API", "error_message": error_message}, status=status.HTTP_400_BAD_REQUEST)
        
        response_data = response.json()
        with transaction.atomic():
            user_api_credits -= 1
            user.api_credits = user_api_credits
            user.save()
            updated_at_datetime = datetime.utcfromtimestamp(response_data['data']['updated_at'])
            new_assessment = Assessment(
                assessment_updated_at = updated_at_datetime,
                currency = currency,
                address_hash = address,
                user = user,
                type_of_assessment = "address",
                response_data = response_data,

                risk_grade = response_data['data']['alert_grade'],
                risk_score = response_data['data']['riskscore'],
                risk_signals = response_data['data']['signals'],
                status_assessment = response_data['data']['status'],
                assessment_id = response_data['data']['id'],
            )
            if request.data['assessment_type'] == "transaction":
                new_assessment.transaction_hash = tx
                new_assessment.transaction_volume_coin = response_data['data']['amount']
                new_assessment.transaction_volume_fiat = response_data['data']['fiat']
                new_assessment.transaction_volume_fiat_currency_code = response_data['data']['fiat_code_effective']
                new_assessment.risk_volume_coin = response_data['data']['risky_volume']
                new_assessment.risk_volume_fiat = response_data['data']['risky_volume_fiat']
            new_assessment.save()
        payload = {
            "user_remaining_credits": user_api_credits,
            "type": "address",
            "hash": address,
            "assessment_status": response_data['data']['status'],
            "risk_grade": response_data['data']['alert_grade'],
            "risk_score": response_data['data']['riskscore'],
            "risk_signals": response_data['data']['signals']
        }
        if request.data['assessment_type'] == "transaction":
            payload['type'] = "transaction"
            payload['transaction_hash'] = tx
            payload['risk_volume_coin'] = response_data['data']['risky_volume']
            payload['risk_volume_fiat'] = response_data['data']['risky_volume_fiat']
            payload['risk_volume_fiat_currency_code'] = response_data['data']['fiat_code_effective']

        return JsonResponse(payload, status=status.HTTP_200_OK)

class AssessmentListView(APIView):
    serializer_class = AssessmentListSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        assessments = Assessment.objects.filter(user=user)
        serializer = AssessmentListSerializer(assessments, many=True)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)

# class AssessmentDetailView(APIView):
#     serializer_class = AssessmentSerializer
#     permission_classes = (IsAuthenticated,)

#     def get_object(self):
#         obj = get_object_or_404(Assessment, assessment_id=self.kwargs["assessment_id"], user=self.request.user)
#         return obj


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



