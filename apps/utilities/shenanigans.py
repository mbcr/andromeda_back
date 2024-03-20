from pprint import pprint


def assess_risk_grade():
    weights = {
                "atm": 0.5,
                "child_exploitation": 1,
                "dark_market": 1,
                "dark_service": 1,
                "enforcement_action": 0.75,
                "exchange_fraudulent": 1,
                "exchange_licensed": 0.1,
                "exchange_unlicensed": 0.6,
                "gambling": 0.75,
                "illegal_service": 1,
                "liquidity_pools": 0.5,
                "marketplace": 0,
                "miner": 0,
                "mixer": 1,
                "other": 0.25,
                "p2p_exchange_licensed": 0.1,
                "p2p_exchange_unlicensed": 0.6,
                "payment": 0,
                "ransom": 1,
                "sanctions": 1,
                "scam": 1,
                "seized_assets": 0,
                "stolen_coins": 1,
                "terrorism_financing": 1,
                "wallet": 0.25
            }
    signals = {
                "atm": 0,
                "child_exploitation": 0,
                "dark_market": 0,
                "dark_service": 0,
                "enforcement_action": 0,
                "exchange_fraudulent": 0.028,
                "exchange_licensed": 0.217,
                "exchange_unlicensed": 0.147,
                "gambling": 0.003,
                "illegal_service": 0,
                "liquidity_pools": 0.003,
                "marketplace": 0,
                "miner": 0,
                "mixer": 0,
                "other": 0.27,
                "p2p_exchange_licensed": 0,
                "p2p_exchange_unlicensed": 0.153,
                "payment": 0.004,
                "ransom": 0,
                "sanctions": 0,
                "scam": 0.021,
                "seized_assets": 0,
                "stolen_coins": 0.144,
                "terrorism_financing": 0,
                "wallet": 0.008
            }

    ## Risk thresholds are derived from sampling of assessments.
    # For the lower bound (delineating Low and Middle grades), sample transactions that have gone through, and get the maximum of each category.
    # For the upper bound (delineating Middle and High grades), sample transactions that have been halted due to AML, and get the lower of each triggering category. <-- This has not been done yet (arbitrary)
    risk_thresholds = {
        "atm": (0.01, 1),
        "child_exploitation": (0.002, 0.01),
        "dark_market": (0.006, 0.015),
        "dark_service": (0.006, 0.015),
        "enforcement_action": (0.012, 0.036),
        "exchange_fraudulent": (0.006, 0.02),
        "exchange_unlicensed": (0.8, 1.0),
        "gambling": (0.02, 0.04),
        "illegal_service": (0.006, 0.015),
        "liquidity_pools": (0.02, 0.04),
        "mixer": (0.003, 0.012),
        "p2p_exchange_unlicensed": (0.35, 1),
        "ransom": (0.001, 0.005),
        "sanctions": (0.001, 0.005),
        "scam": (0.001, 0.005),
        "stolen_coins": (0.001, 0.005),
        "terrorism_financing": (0.001, 0.005),
    }

    weighed_signals = {}

    aggregator = 0
    for key, value in weights.items():
        # print(key, value, signals[key])
        specific_risk = signals[key] * value
        aggregator += specific_risk
        weighed_signals[key] = specific_risk
        

    print(f'Total: {aggregator}')
    pprint(weighed_signals)


def get_low_risk_thresholds():
    low_risk_thresholds = {}

    signals_sampling_from_successful_transactions = [
        {"atm": 0.0, "scam": 0.0, "miner": 0.0, "mixer": 0.0, "other": 0.0, "ransom": 0.0, "wallet": 0.0, "payment": 0.0, "gambling": 0.0, "sanctions": 0.0, "dark_market": 0.0, "marketplace": 0.0, "dark_service": 0.0, "stolen_coins": 0.0, "seized_assets": 0.0, "illegal_service": 0.0, "liquidity_pools": 0.0, "exchange_licensed": 0.0, "child_exploitation": 0.0, "enforcement_action": 0.0, "exchange_fraudulent": 0.0, "exchange_unlicensed": 1.0, "terrorism_financing": 0.0, "p2p_exchange_licensed": 0.0, "p2p_exchange_unlicensed": 0.0},
        {"atm": 0.0, "scam": 0.0, "miner": 0.0, "mixer": 0.0, "other": 0.0, "ransom": 0.0, "wallet": 0.0, "payment": 0.0, "gambling": 0.0, "sanctions": 0.0, "dark_market": 0.0, "marketplace": 0.0, "dark_service": 0.0, "stolen_coins": 0.0, "seized_assets": 0.0, "illegal_service": 0.0, "liquidity_pools": 0.0, "exchange_licensed": 0.0, "child_exploitation": 0.0, "enforcement_action": 0.0, "exchange_fraudulent": 0.0, "exchange_unlicensed": 1.0, "terrorism_financing": 0.0, "p2p_exchange_licensed": 0.0, "p2p_exchange_unlicensed": 0.0},
        {"atm": 0.0, "scam": 0.0, "miner": 0.0, "mixer": 0.0, "other": 0.0, "ransom": 0.0, "wallet": 0.0, "payment": 0.042, "gambling": 0.013, "sanctions": 0.0, "dark_market": 0.0, "marketplace": 0.0, "dark_service": 0.0, "stolen_coins": 0.0, "seized_assets": 0.0, "illegal_service": 0.0, "liquidity_pools": 0.0, "exchange_licensed": 0.932, "child_exploitation": 0.0, "enforcement_action": 0.0, "exchange_fraudulent": 0.0, "exchange_unlicensed": 0.01, "terrorism_financing": 0.0, "p2p_exchange_licensed": 0.0, "p2p_exchange_unlicensed": 0.0},
        {"atm": 0.0, "scam": 0.0, "miner": 0.003, "mixer": 0.003, "other": 0.014, "ransom": 0.0, "wallet": 0.083, "payment": 0.092, "gambling": 0.001, "sanctions": 0.0, "dark_market": 0.0, "marketplace": 0.0, "dark_service": 0.0, "stolen_coins": 0.0, "seized_assets": 0.0, "illegal_service": 0.0, "liquidity_pools": 0.0, "exchange_licensed": 0.766, "child_exploitation": 0.0, "enforcement_action": 0.0, "exchange_fraudulent": 0.0, "exchange_unlicensed": 0.034, "terrorism_financing": 0.0, "p2p_exchange_licensed": 0.001, "p2p_exchange_unlicensed": 0.0},
        {"atm": 0.001, "scam": 0.0, "miner": 0.007, "mixer": 0.003, "other": 0.011, "ransom": 0.0, "wallet": 0.011, "payment": 0.027, "gambling": 0.02, "sanctions": 0.0, "dark_market": 0.006, "marketplace": 0.0, "dark_service": 0.0, "stolen_coins": 0.001, "seized_assets": 0.0, "illegal_service": 0.0, "liquidity_pools": 0.0, "exchange_licensed": 0.769, "child_exploitation": 0.0, "enforcement_action": 0.012, "exchange_fraudulent": 0.0, "exchange_unlicensed": 0.122, "terrorism_financing": 0.0, "p2p_exchange_licensed": 0.003, "p2p_exchange_unlicensed": 0.003},
        {"atm": 0.0, "scam": 0.001, "miner": 0.003, "mixer": 0.0, "other": 0.004, "ransom": 0.0, "wallet": 0.013, "payment": 0.033, "gambling": 0.002, "sanctions": 0.0, "dark_market": 0.0, "marketplace": 0.0, "dark_service": 0.0, "stolen_coins": 0.0, "seized_assets": 0.0, "illegal_service": 0.0, "liquidity_pools": 0.0, "exchange_licensed": 0.63, "child_exploitation": 0.0, "enforcement_action": 0.001, "exchange_fraudulent": 0.0, "exchange_unlicensed": 0.257, "terrorism_financing": 0.0, "p2p_exchange_licensed": 0.047, "p2p_exchange_unlicensed": 0.006},
        {"atm": 0.0, "scam": 0.0, "miner": 0.0, "mixer": 0.0, "other": 0.601, "ransom": 0.0, "wallet": 0.003, "payment": 0.0, "gambling": 0.0, "sanctions": 0.0, "dark_market": 0.0, "marketplace": 0.003, "dark_service": 0.0, "stolen_coins": 0.0, "seized_assets": 0.0, "illegal_service": 0.0, "liquidity_pools": 0.019, "exchange_licensed": 0.045, "child_exploitation": 0.0, "enforcement_action": 0.0, "exchange_fraudulent": 0.0, "exchange_unlicensed": 0.004, "terrorism_financing": 0.0, "p2p_exchange_licensed": 0.0, "p2p_exchange_unlicensed": 0.324},    
    ]

    for item in signals_sampling_from_successful_transactions:
        for key, value in item.items():
            if key not in low_risk_thresholds:
                if value:
                    low_risk_thresholds[key] = value
            else:
                low_risk_thresholds[key] = max(low_risk_thresholds[key], value)
    
    pprint(low_risk_thresholds)

def print_object():
    null = None
    false = False
    true = True
    object_to_print = {"data": {"id": "9bfddc3", "tx": null, "fiat": null, "time": null, "amount": null, "reason": null, "status": "ready", "address": "bc1qr5nfyumpke6efr0tw25py9q6jcvt5ajxfa9rv9", "flagged": "flag", "signals": {"atm": 0.0, "scam": 0.0, "miner": 0.0, "mixer": 0.0, "other": 0.0, "ransom": 0.0, "wallet": 0.0, "payment": 0.0, "gambling": 0.0, "sanctions": 0.0, "dark_market": 0.0, "marketplace": 0.0, "dark_service": 0.0, "stolen_coins": 0.0, "seized_assets": 0.0, "illegal_service": 0.0, "liquidity_pools": 0.0, "exchange_licensed": 0.0, "child_exploitation": 0.0, "enforcement_action": 0.0, "exchange_fraudulent": 0.0, "exchange_unlicensed": 1.0, "terrorism_financing": 0.0, "p2p_exchange_licensed": 0.0, "p2p_exchange_unlicensed": 0.0}, "archived": false, "currency": "btc", "customer": {"name": "QmKmqRitSGjZ", "token": "e2SnKVCGRQ72e4AV"}, "token_id": 0, "direction": "withdrawal", "riskscore": 0.6, "alert_list": [[[">=", "#rscore", 0.5], "#flag-high"]], "alert_type": ["counterparty"], "changed_at": 1710799955, "created_at": 1710799955, "updated_at": 1710799955, "alert_grade": "high", "flag_reason": ["MAX", ["IF", ["OR", ["IF", ["JUST", "#blist_in", false], ["YIELD", "#blist_in", true, true], false], ["IF", ["JUST", "#blist_out", false], ["YIELD", "#blist_out", true, true], false], ["IF", ["JUST", "#blist_out_interaction", false], ["YIELD", "#blist_out_interaction", true, true], false], false], "#flag-high", false], ["IF", ["OR", [">=", "#amount", 1000, false], ["ISNULL", "#amount", true], true], ["MAX", ["IF", [">", "#risky-amount", 0, false], ["YIELD", [">", "#risky-amount", 0, false], "#flag-high", 100], false], false], false], ["IF", ["AND", [">=", "#rscore", 0.5, true], ["=", "#direction", "deposit", false], false], ["YIELD", [">=", "#rscore", 0.5, true], "#flag-high", 100], false], ["IF", ["AND", [">=", "#rscore", 0.5, true], ["=", "#direction", "withdrawal", true], true], ["YIELD", [">=", "#rscore", 0.5, true], "#flag-high", 100], 100], 100], "settings_id": 13306, "counterparty": {"address": "bc1qr5nfyumpke6efr0tw25py9q6jcvt5ajxfa9rv9"}, "fiat_current": "usd", "risky_volume": null, "snapshoted_at": 1710799955, "customer_watched": false, "riskscore_profile": {"id": 0, "name": "Default", "signals": {"atm": 0.5, "scam": 1.0, "miner": 0.0, "mixer": 1.0, "other": 0.25, "ransom": 1.0, "wallet": 0.25, "payment": 0.0, "gambling": 0.75, "sanctions": 1.0, "dark_market": 1.0, "marketplace": 0.0, "dark_service": 1.0, "stolen_coins": 1.0, "seized_assets": 0.0, "illegal_service": 1.0, "liquidity_pools": 0.5, "exchange_licensed": 0.1, "child_exploitation": 1.0, "enforcement_action": 0.75, "exchange_fraudulent": 1.0, "exchange_unlicensed": 0.6, "terrorism_financing": 1.0, "p2p_exchange_licensed": 0.1, "p2p_exchange_unlicensed": 0.6}, "history_id": 3986}, "risky_volume_fiat": null, "fiat_code_effective": "usd"}, "meta": {"fiat_code": "usd", "calls_left": 4674, "calls_used": 326, "error_code": 0, "server_time": 1710799957, "error_message": "", "riskscore_profile": {"id": 0, "name": "Default - equal influence"}}}
    pprint(object_to_print.get('data').get('token_id'))


print_object()