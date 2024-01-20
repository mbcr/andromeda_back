from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response


from apps.users.permissions import HasChainVetAPIKey
from .models import Assessment
from .serializers import AssessmentSerializer, AssessmentListSerializer, OrderSerializer
from apps.users.models import ChainVetAPIKey
from apps.users import models as user_models

from pprint import pprint
from datetime import datetime
import requests
import logging

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

# eth
# 0x05ea2f2ea40287343ebefbf1c14eaacb94a5ba1544446af66d19314b3d74b7e9
# 0xb2bde87dd389771a19040a8c21ee9a9e33d5454c
class AssessmentCreateWIthUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # print("chainvet>views>AssessmentView>post>Received request.data:")
        # pprint(request.data)

        def assessment_already_exists(bcb_request_data: dict) -> bool:
            # print('chainvet>views>AssessmentView>assessment_already_exists>Checking if assessment already exists')
            # pprint(bcb_request_data)
            if request.data['assessment_type'] == "address":
                request_transaction_hash = None
            else:
                request_transaction_hash = bcb_request_data['tx']

            if Assessment.objects.filter(
                    user = request.user,
                    type_of_assessment = request.data['assessment_type'],
                    address_hash = bcb_request_data['address'],
                    currency = bcb_request_data['currency'],
                    transaction_hash = request_transaction_hash
                ).exists():
                return True
            else:
                return False

        api_key = request.META.get("HTTP_X_API_KEY")
        user = request.user
        user_api_credits = user.api_credits

        if user_api_credits <= 0:
            return JsonResponse({"error_message": "Insufficient API credits"}, status=status.HTTP_402_PAYMENT_REQUIRED)

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
            # print('Invalid assessment type')
            return JsonResponse({"error_message": "Invalid assessment type."}, status=status.HTTP_400_BAD_REQUEST)

        if assessment_already_exists(bcb_request_data):
            # print('A coisa já existe. Returning 400 with message')
            return JsonResponse({"error_message": f"Risk assessment for the {request.data['assessment_type']} already exists. Please check the dashboard's assessment table."}, status=status.HTTP_400_BAD_REQUEST)
        # print('A coisa não existe. Continuando...'	)
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


@api_view(['POST'])
def create_new_order(request):    
    # Check if necessary data is present
    if not request.data.get('number_of_credits'):
        return Response({"detail": "Missing number_of_credits parameter"}, status=status.HTTP_400_BAD_REQUEST)
    if not request.data.get('crypto_coin'):
        return Response({"detail": "Missing crypto_coin parameter"}, status=status.HTTP_400_BAD_REQUEST)
    if request.data.get('order_is_for_self') == None:
        return Response({"detail": "Missing order_is_for_self parameter"}, status=status.HTTP_400_BAD_REQUEST)

    # Identify who's making the request (must have a valid API Key OR be authenticated)
    api_key = request.META.get("HTTP_X_API_KEY")
    if api_key: # WITH APIKey
        try:
            api_key_instance = ChainVetAPIKey.objects.get_from_key(api_key)
            if api_key_instance.revoked:
                return Response({"detail": "Invalid API key."}, status=status.HTTP_403_FORBIDDEN)
            requesting_user_type = api_key_instance.owner_type
            if requesting_user_type == "User":
                requesting_user = api_key_instance.user
            elif requesting_user_type == "AccessCode":
                requesting_user = api_key_instance.access_code
            else:
                return Response({"detail": "User not identified by APIKey"}, status=status.HTTP_403_FORBIDDEN)
        except ChainVetAPIKey.DoesNotExist:
            return Response({"detail": "Invalid API key."}, status=status.HTTP_403_FORBIDDEN)
    else: # WITHOUT APIKey
        if request.user.is_authenticated:
            requesting_user_type = "User"
            requesting_user = request.user
        else:
            return Response({"detail": "Invalid credentials. Please log in"}, status=status.HTTP_403_FORBIDDEN)

    # Identify who the order is for
    order_is_for_self = request.data.get('order_is_for_self')
    if order_is_for_self:
        target_user = requesting_user
    else: # Check if the access code exists, and create a new one if it doesn't
        access_code = request.data.get('access_code')
        if access_code:
            try:
                target_user = user_models.AccessCode.objects.get(code=access_code).user
            except user_models.AccessCode.DoesNotExist:
                return Response({"detail": "Invalid access code"}, status=status.HTTP_400_BAD_REQUEST)
        else: # Create new access code
            new_access_code = user_models.AccessCode.objects.create()
            target_user = new_access_code

    try: # Create the new order from the target user's entity and return payload
        new_order = target_user.create_new_order_v1(
            number_of_credits = request.data.get('number_of_credits'),
            crypto_coin = request.data.get('crypto_coin')
        )
        payload = OrderSerializer(new_order).data
        return Response(payload, status=status.HTTP_201_CREATED)
    except Exception as e: # Log and return
        error_logger = logging.getLogger('error_logger') 
        log_data = {key: request.data[key] for key in ['number_of_credits', 'crypto_coin', 'order_is_for_self', 'access_code'] if key in request.data}
        error_logger.debug(f'apps.chainvet.views: create_new_order; error location code: HY58S; request.data: {log_data}; error message: {str(e)}')
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


