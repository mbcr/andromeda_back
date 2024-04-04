import requests
import logging
import json
from django.conf import settings
from pprint import pprint



api_main_url = 'https://apiexpert.crystalblockchain.com/'
api_key = settings.CRYSTAL_API_KEY
request_headers={
    "accept": "application/json",
    "X-Auth-Apikey": settings.CRYSTAL_API_KEY
}


logger = logging.getLogger('api_calls_cbc')

def new_assessment(cbc_request_data: dict)->dict:
    specific_url = "monitor/tx/add"
    request_url = f"{api_main_url}/{specific_url}"
    try:
        from apps.users.models import ConfigVariable
        api_mocking_config = ConfigVariable.objects.get(name='cbc_api_mocking_is_active')
        api_mocking_is_active = api_mocking_config.value == 'True'
    except ConfigVariable.DoesNotExist:
        api_mocking_is_active = False
    
    if api_mocking_is_active:
        # print('CreditOwnerMixin.create_new_assessment. External API call is being mocked')
        from apps.chainvet.models import Assessment
        assessment_id = 'MockAssessmentID#'+str(Assessment.objects.last().id + 1)
        if cbc_request_data.get('direction') == 'deposit':
            json_str = '''{ "data": { "address": "TransactionAssessment0xb2bde87dd389771a19040a8c21ee9a9e33d5454c", "alert_grade": "high", "alert_list": [ [ [ ">", "#risky-amount", 0 ], "#flag-high" ] ], "alert_type": [ "amount" ], "amount": 10133177.506536, "archived": false, "changed_at": 1707299767, "counterparty": { "address": "0x24d4dcbe128923b9ee29bcc5e10c7af23d715c2b" }, "created_at": 1707299767, "currency": "eth", "customer": { "name": "test_user", "token": "M56p4rHkadhB5Xp7" }, "customer_watched": false, "direction": "deposit", "fiat": 1893, "fiat_code_effective": "usd", "fiat_current": "usd", "flag_reason": [ "MAX", [ "IF", [ "OR", [ "IF", [ "JUST", "#blist_in", false ], [ "YIELD", "#blist_in", true, true ], false ], [ "IF", [ "JUST", "#blist_out", false ], [ "YIELD", "#blist_out", true, true ], false ], [ "IF", [ "JUST", "#blist_out_interaction", false ], [ "YIELD", "#blist_out_interaction", true, true ], false ], false ], "#flag-high", false ], [ "IF", [ "OR", [ ">=", "#amount", 1000, true ], [ "ISNULL", "#amount", false ], true ], [ "MAX", [ "IF", [ ">", "#risky-amount", 0, true ], [ "YIELD", [ ">", "#risky-amount", 0, true ], "#flag-high", 100 ], 100 ], 100 ], 100 ], [ "IF", [ "AND", [ ">=", "#rscore", 0.5, false ], [ "=", "#direction", "deposit", true ], false ], [ "YIELD", [ ">=", "#rscore", 0.5, false ], "#flag-high", 100 ], false ], [ "IF", [ "AND", [ ">=", "#rscore", 0.5, false ], [ "=", "#direction", "withdrawal", false ], false ], [ "YIELD", [ ">=", "#rscore", 0.5, false ], "#flag-high", 100 ], false ], 100 ], "flagged": "flag", "id": "90ba3e5", "is_pool": false, "reason": null, "riskscore": 0.319, "riskscore_profile": { "history_id": 3986, "id": 0, "name": "Default", "signals": { "atm": 0.5, "child_exploitation": 1, "dark_market": 1, "dark_service": 1, "enforcement_action": 0.75, "exchange_fraudulent": 1, "exchange_licensed": 0.1, "exchange_unlicensed": 0.6, "gambling": 0.75, "illegal_service": 1, "liquidity_pools": 0.5, "marketplace": 0, "miner": 0, "mixer": 1, "other": 0.25, "p2p_exchange_licensed": 0.1, "p2p_exchange_unlicensed": 0.6, "payment": 0, "ransom": 1, "sanctions": 1, "scam": 1, "seized_assets": 0, "stolen_coins": 1, "terrorism_financing": 1, "wallet": 0.25 } }, "risky_volume": 1993914.84740113, "risky_volume_fiat": 372.48738647830476, "settings_id": 13306, "signals": { "atm": 0, "child_exploitation": 0, "dark_market": 0, "dark_service": 0, "enforcement_action": 0, "exchange_fraudulent": 0.028, "exchange_licensed": 0.217, "exchange_unlicensed": 0.147, "gambling": 0.003, "illegal_service": 0, "liquidity_pools": 0.003, "marketplace": 0, "miner": 0, "mixer": 0, "other": 0.27, "p2p_exchange_licensed": 0, "p2p_exchange_unlicensed": 0.153, "payment": 0.004, "ransom": 0, "sanctions": 0, "scam": 0.021, "seized_assets": 0, "stolen_coins": 0.144, "terrorism_financing": 0, "wallet": 0.008 }, "snapshoted_at": 1707299767, "status": "ready", "time": 1680821375, "token_id": 0, "tx": "0x05ea2f2ea40287343ebefbf1c14eaacb94a5ba1544446af66d19314b3d74b7e9", "updated_at": 1707299767 }, "meta": { "calls_left": 4997, "calls_used": 3, "error_code": 0, "error_message": "", "fiat_code": "usd", "riskscore_profile": { "id": 0, "name": "Default - equal influence" }, "server_time": 1707299768 } }'''
        else:
            json_str = '''{"data": {"address": "AddressAssessment0x36a2c58b7af6b53a850e1ec2a201eba40ed2686e", "alert_grade": null, "alert_list": [], "alert_type": null, "amount": null, "archived": false, "changed_at": 1707327750, "counterparty": {"address": "0x36a2c58b7af6b53a850e1ec2a201eba40ed2686e"}, "created_at": 1707327750, "currency": "eth", "customer": {"name": "test_user", "token": "M56p4rHkadhB5Xp7"}, "customer_watched": false, "direction": "withdrawal", "fiat": null, "fiat_code_effective": "usd", "fiat_current": "usd", "flag_reason": ["MAX", ["IF", ["OR", ["IF", ["JUST", "#blist_in", false], ["YIELD", "#blist_in", true, true], false], ["IF", ["JUST", "#blist_out", false], ["YIELD", "#blist_out", true, true], false], ["IF", ["JUST", "#blist_out_interaction", false], ["YIELD", "#blist_out_interaction", true, true], false], false], "#flag-high", false], ["IF", ["OR", [">=", "#amount", 1000, false], ["ISNULL", "#amount", true], true], ["MAX", ["IF", [">", "#risky-amount", 0, false], ["YIELD", [">", "#risky-amount", 0, false], "#flag-high", 100], false], false], false], ["IF", ["AND", [">=", "#rscore", 0.5, false], ["=", "#direction", "deposit", false], false], ["YIELD", [">=", "#rscore", 0.5, false], "#flag-high", 100], false], ["IF", ["AND", [">=", "#rscore", 0.5, false], ["=", "#direction", "withdrawal", true], false], ["YIELD", [">=", "#rscore", 0.5, false], "#flag-high", 100], false], false], "flagged": "noflag", "id": "92abb5f", "reason": null, "riskscore": 0.304, "riskscore_profile": {"history_id": 3986, "id": 0, "name": "Default", "signals": {"atm": 0.5, "child_exploitation": 1.0, "dark_market": 1.0, "dark_service": 1.0, "enforcement_action": 0.75, "exchange_fraudulent": 1.0, "exchange_licensed": 0.1, "exchange_unlicensed": 0.6, "gambling": 0.75, "illegal_service": 1.0, "liquidity_pools": 0.5, "marketplace": 0.0, "miner": 0.0, "mixer": 1.0, "other": 0.25, "p2p_exchange_licensed": 0.1, "p2p_exchange_unlicensed": 0.6, "payment": 0.0, "ransom": 1.0, "sanctions": 1.0, "scam": 1.0, "seized_assets": 0.0, "stolen_coins": 1.0, "terrorism_financing": 1.0, "wallet": 0.25}}, "risky_volume": null, "risky_volume_fiat": null, "settings_id": 13306, "signals": {"atm": 0.0, "child_exploitation": 0.0, "dark_market": 0.0, "dark_service": 0.0, "enforcement_action": 0.0, "exchange_fraudulent": 0.0, "exchange_licensed": 0.517, "exchange_unlicensed": 0.096, "gambling": 0.0, "illegal_service": 0.0, "liquidity_pools": 0.012, "marketplace": 0.0, "miner": 0.0, "mixer": 0.0, "other": 0.102, "p2p_exchange_licensed": 0.0, "p2p_exchange_unlicensed": 0.271, "payment": 0.0, "ransom": 0.0, "sanctions": 0.0, "scam": 0.0, "seized_assets": 0.0, "stolen_coins": 0.0, "terrorism_financing": 0.0, "wallet": 0.0}, "snapshoted_at": 1707327750, "status": "ready", "time": null, "tx": null, "updated_at": 1707327750}, "meta": {"calls_left": 4995, "calls_used": 5, "error_code": 0, "error_message": "", "fiat_code": "usd", "riskscore_profile": {"id": 0, "name": "Default - equal influence"}, "server_time": 1707327751}}'''
        response_data = json.loads(json_str)
        response_data['data']['id'] = assessment_id
        return {
            'status': 'Success',
            'status_code': 200,
            'message': 'Mocking is active. No data was sent to the external API.',
            'data': response_data
        }

    response = requests.post(
        url=request_url,
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
    logger.debug(f"utils.api_crystal_blockchain>new_assessment: cbc_request_data: |{cbc_request_data}|, response_code: |{response.status_code}|, response: |{response_data}|")
    
    return {
        'status': 'Success',
        'status_code': 200,
        'message': 'New assessment was successfully retrieved from the external API.',
        'data': response_data
    }


def check_assessment_by_id(cbc_id:str)->dict:
    specific_url = "monitor/batch/txs"
    request_url = f"{api_main_url}/{specific_url}"
    cbc_request_data = {
        "filter": {
            "id": "975b97e"
        }
    }

    response = requests.post(
        url=request_url,
        headers=request_headers,
        json= cbc_request_data,
        timeout=10,
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
    logger.debug(f"utils.api_crystal_blockchain>check_assessment_by_id: response_code: |{response.status_code}|, response: |{response_data}|, cbc_request_data: |{cbc_request_data}|")

    return {
        'status': 'Success',
        'status_code': 200,
        'message': 'Data was successfully retrieved from the external API.',
        'payload': response_data
    }