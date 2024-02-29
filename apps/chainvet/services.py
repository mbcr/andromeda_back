# from pprint import pprint

def grade_risk_level(signals:dict)-> str:
    ## Risk thresholds are derived from sampling of assessments. See utilities.shenanigans.py for latest sample
    # For the lower bound (delineating Low and Middle grades), sample transactions that have gone through, and get the maximum of each category.
    # For the upper bound (delineating Middle and High grades), sample transactions that have been halted due to AML, and get the lower of each triggering category. <-- This has not been done yet (arbitrary)
    risk_thresholds = {
        "atm": (0.02, 1),
        "child_exploitation": (0.002, 0.01),
        "dark_market": (0.006, 0.015),
        "dark_service": (0.006, 0.015),
        "enforcement_action": (0.012, 0.024),
        "exchange_fraudulent": (0.006, 0.02),
        "exchange_unlicensed": (0.35, 1.0),
        "gambling": (0.02, 0.04),
        "illegal_service": (0.006, 0.015),
        "liquidity_pools": (0.02, 0.04),
        "mixer": (0.003, 0.012),
        "p2p_exchange_unlicensed": (0.2, 1),
        "ransom": (0.001, 0.005),
        "sanctions": (0.001, 0.005),
        "scam": (0.001, 0.005),
        "stolen_coins": (0.001, 0.005),
        "terrorism_financing": (0.001, 0.005),
    }
    medium_risk_categories = [
        "atm",
        "exchange_unlicensed",
        "liquidity_pools",
        "p2p_exchange_unlicensed"
    ]
    high_risk_categories = [
        "child_exploitation",
        "dark_market",
        "dark_service",
        "enforcement_action",
        "exchange_fraudulent",
        "gambling",
        "illegal_service",
        "mixer",
        "ransom",
        "sanctions",
        "scam",
        "stolen_coins",
        "terrorism_financing"
    ]

    def check_key_value_pair(risk_category,risk_value):
        if risk_category not in risk_thresholds.keys():
            return 0
        low, middle = risk_thresholds[risk_category]
        if risk_value <= low:
            return 0
        if risk_value >= low and risk_value <= middle:
            return 1
        return 2

    risk_grade_names = {
        0: 'Low',
        1: 'Medium',
        2: 'High'
    }

    individual_risks = []
    aggregated_risk = {
        0: 0,
        1: 0,
        2: 0
    }
    total_high_risk = 0
    total_medium_risk = 0
    for key,value in signals.items():
        individual_risk_grade = check_key_value_pair(risk_category=key,risk_value=value)
        individual_risks.append(individual_risk_grade)
        aggregated_risk[individual_risk_grade] += value
        if key in high_risk_categories:
            total_high_risk += value
        elif key in medium_risk_categories:
            total_medium_risk += value
    
    max_individual_risk = max(individual_risks)
    
    # Take into consideration aggregate risk to determine the composite risk grade
    aggregate_risk = 0
    if max_individual_risk == 0:
        if total_medium_risk > 0.4:
            aggregate_risk = 1
        if total_high_risk > 0.06:
            aggregate_risk = 2
        elif total_high_risk > 0.02:
            aggregate_risk = 1
    if max_individual_risk == 1:
        if total_high_risk > 0.04:
            aggregate_risk = 2
        else:
            aggregate_risk = 0
    composite_risk_grade = max(max_individual_risk,aggregate_risk)
    
    # Return the risk grade name
    risk_grade = risk_grade_names[composite_risk_grade]
    return risk_grade


# Example of signals:
# sign = {"atm": 0.0, "scam": 0.0, "miner": 0.0, "mixer": 0.0, "other": 0.601, "ransom": 0.0, "wallet": 0.003, "payment": 0.0, "gambling": 0.0, "sanctions": 0.0, "dark_market": 0.0, "marketplace": 0.003, "dark_service": 0.0, "stolen_coins": 0.0, "seized_assets": 0.0, "illegal_service": 0.0, "liquidity_pools": 0.019, "exchange_licensed": 0.045, "child_exploitation": 0.0, "enforcement_action": 0.0, "exchange_fraudulent": 0.0, "exchange_unlicensed": 0.004, "terrorism_financing": 0.0, "p2p_exchange_licensed": 0.0, "p2p_exchange_unlicensed": 0.324}
# sign = {"atm": 0.0, "scam": 0.0, "miner": 0.0, "mixer": 0.0, "other": 0.404, "ransom": 0.0, "wallet": 0.0, "payment": 0.014, "gambling": 0.0, "sanctions": 0.002, "dark_market": 0.0, "marketplace": 0.0, "dark_service": 0.0, "stolen_coins": 0.0, "seized_assets": 0.0, "illegal_service": 0.0, "liquidity_pools": 0.0, "exchange_licensed": 0.562, "child_exploitation": 0.0, "enforcement_action": 0.0, "exchange_fraudulent": 0.0, "exchange_unlicensed": 0.017, "terrorism_financing": 0.0, "p2p_exchange_licensed": 0.0, "p2p_exchange_unlicensed": 0.0}
# sign = {"atm": 0.0, "scam": 0.0, "miner": 0.0, "mixer": 0.005, "other": 0.006, "ransom": 0.0, "wallet": 0.0, "payment": 0.004, "gambling": 0.0, "sanctions": 0.0, "dark_market": 0.0, "marketplace": 0.0, "dark_service": 0.0, "stolen_coins": 0.002, "seized_assets": 0.0, "illegal_service": 0.0, "liquidity_pools": 0.0, "exchange_licensed": 0.097, "child_exploitation": 0.0, "enforcement_action": 0.001, "exchange_fraudulent": 0.0, "exchange_unlicensed": 0.884, "terrorism_financing": 0.0, "p2p_exchange_licensed": 0.0, "p2p_exchange_unlicensed": 0.0}
# sign = {"atm": 0.0, "scam": 0.0, "miner": 0.0, "mixer": 0.0, "other": 0.444, "ransom": 0.0, "wallet": 0.054, "payment": 0.0, "gambling": 0.0, "sanctions": 0.0, "dark_market": 0.0, "marketplace": 0.041, "dark_service": 0.0, "stolen_coins": 0.004, "seized_assets": 0.0, "illegal_service": 0.0, "liquidity_pools": 0.041, "exchange_licensed": 0.028, "child_exploitation": 0.0, "enforcement_action": 0.0, "exchange_fraudulent": 0.0, "exchange_unlicensed": 0.006, "terrorism_financing": 0.0, "p2p_exchange_licensed": 0.0, "p2p_exchange_unlicensed": 0.379}
# sign = {"atm": 0.001, "scam": 0.0, "miner": 0.007, "mixer": 0.003, "other": 0.011, "ransom": 0.0, "wallet": 0.011, "payment": 0.027, "gambling": 0.02, "sanctions": 0.0, "dark_market": 0.006, "marketplace": 0.0, "dark_service": 0.0, "stolen_coins": 0.001, "seized_assets": 0.0, "illegal_service": 0.0, "liquidity_pools": 0.0, "exchange_licensed": 0.769, "child_exploitation": 0.0, "enforcement_action": 0.012, "exchange_fraudulent": 0.0, "exchange_unlicensed": 0.122, "terrorism_financing": 0.0, "p2p_exchange_licensed": 0.003, "p2p_exchange_unlicensed": 0.003}
# print(f"The risk grade (individual) is: {grade_risk_level(sign)}")



