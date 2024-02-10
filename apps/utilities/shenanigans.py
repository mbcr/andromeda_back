from pprint import pprint

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

aggregator = 0
for key, value in weights.items():
    print(key, value, signals[key])
    aggregator += signals[key] * value

print(f'Total: {aggregator}')
