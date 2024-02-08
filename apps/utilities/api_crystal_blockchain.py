import requests
import logging
import json
from django.conf import settings
from pprint import pprint



api_main_url = 'https://apiexpert.crystalblockchain.com/monitor/tx/add'
api_key = settings.CRYSTAL_API_KEY
request_headers={
    "accept": "application/json",
    "X-Auth-Apikey": settings.CRYSTAL_API_KEY
}


logger = logging.getLogger('api_calls_cbc')

def new_assessment(cbc_request_data: dict)->dict:
    try:
        from apps.users.models import ConfigVariable
        api_mocking_config = ConfigVariable.objects.get(name='cbc_api_mocking_is_active')
        api_mocking_is_active = api_mocking_config.value == 'True'
    except ConfigVariable.DoesNotExist:
        api_mocking_is_active = False
    
    if api_mocking_is_active:
        print('CreditOwnerMixin.create_new_assessment. External API call is being mocked')
        from apps.chainvet.models import Assessment
        assessment_id = 'MockAssessmentID#'+str(Assessment.objects.all().count() + 1)
        json_str = '''{"data": {"address": "0x36a2c58b7af6b53a850e1ec2a201eba40ed2686e", "alert_grade": null, "alert_list": [], "alert_type": null, "amount": null, "archived": false, "changed_at": 1707327750, "counterparty": {"address": "0x36a2c58b7af6b53a850e1ec2a201eba40ed2686e"}, "created_at": 1707327750, "currency": "eth", "customer": {"name": "test_user", "token": "M56p4rHkadhB5Xp7"}, "customer_watched": false, "direction": "withdrawal", "fiat": null, "fiat_code_effective": "usd", "fiat_current": "usd", "flag_reason": ["MAX", ["IF", ["OR", ["IF", ["JUST", "#blist_in", false], ["YIELD", "#blist_in", true, true], false], ["IF", ["JUST", "#blist_out", false], ["YIELD", "#blist_out", true, true], false], ["IF", ["JUST", "#blist_out_interaction", false], ["YIELD", "#blist_out_interaction", true, true], false], false], "#flag-high", false], ["IF", ["OR", [">=", "#amount", 1000, false], ["ISNULL", "#amount", true], true], ["MAX", ["IF", [">", "#risky-amount", 0, false], ["YIELD", [">", "#risky-amount", 0, false], "#flag-high", 100], false], false], false], ["IF", ["AND", [">=", "#rscore", 0.5, false], ["=", "#direction", "deposit", false], false], ["YIELD", [">=", "#rscore", 0.5, false], "#flag-high", 100], false], ["IF", ["AND", [">=", "#rscore", 0.5, false], ["=", "#direction", "withdrawal", true], false], ["YIELD", [">=", "#rscore", 0.5, false], "#flag-high", 100], false], false], "flagged": "noflag", "id": "92abb5f", "reason": null, "riskscore": 0.304, "riskscore_profile": {"history_id": 3986, "id": 0, "name": "Default", "signals": {"atm": 0.5, "child_exploitation": 1.0, "dark_market": 1.0, "dark_service": 1.0, "enforcement_action": 0.75, "exchange_fraudulent": 1.0, "exchange_licensed": 0.1, "exchange_unlicensed": 0.6, "gambling": 0.75, "illegal_service": 1.0, "liquidity_pools": 0.5, "marketplace": 0.0, "miner": 0.0, "mixer": 1.0, "other": 0.25, "p2p_exchange_licensed": 0.1, "p2p_exchange_unlicensed": 0.6, "payment": 0.0, "ransom": 1.0, "sanctions": 1.0, "scam": 1.0, "seized_assets": 0.0, "stolen_coins": 1.0, "terrorism_financing": 1.0, "wallet": 0.25}}, "risky_volume": null, "risky_volume_fiat": null, "settings_id": 13306, "signals": {"atm": 0.0, "child_exploitation": 0.0, "dark_market": 0.0, "dark_service": 0.0, "enforcement_action": 0.0, "exchange_fraudulent": 0.0, "exchange_licensed": 0.517, "exchange_unlicensed": 0.096, "gambling": 0.0, "illegal_service": 0.0, "liquidity_pools": 0.012, "marketplace": 0.0, "miner": 0.0, "mixer": 0.0, "other": 0.102, "p2p_exchange_licensed": 0.0, "p2p_exchange_unlicensed": 0.271, "payment": 0.0, "ransom": 0.0, "sanctions": 0.0, "scam": 0.0, "seized_assets": 0.0, "stolen_coins": 0.0, "terrorism_financing": 0.0, "wallet": 0.0}, "snapshoted_at": 1707327750, "status": "ready", "time": null, "tx": null, "updated_at": 1707327750}, "meta": {"calls_left": 4995, "calls_used": 5, "error_code": 0, "error_message": "", "fiat_code": "usd", "riskscore_profile": {"id": 0, "name": "Default - equal influence"}, "server_time": 1707327751}}'''
        response_data = json.loads(json_str)
        response_data['data']['id'] = assessment_id
        return {
            'status': 'Success',
            'status_code': 200,
            'message': 'Mocking is active. No data was sent to the external API.',
            'data': response_data
        }

    response = requests.post(
        url=api_main_url,
        headers=request_headers,
        data= cbc_request_data
    )

    if response.status_code != 200:
        error_message = response.json()['meta']['error_message']
        logger.debug(f"utils.api_crystal_blockchain>new_assessment: response_code: {response.status_code}, cbc_request_data: {cbc_request_data}, response: {response.json()}")
        return {
            'status': 'Error',
            'status_code': response.status_code,
            'message': f'Unable to retrieve data from CBC API. Error message: {error_message}'
        }
    
    response_data = response.json()
    logger.debug(f"utils.api_crystal_blockchain>new_assessment: response_code: |{response.status_code}|, response: |{response_data}|, cbc_request_data: |{cbc_request_data}|")
    
    return {
        'status': 'Success',
        'status_code': 200,
        'message': 'Data was successfully retrieved from the external API.',
        'data': response_data
    }