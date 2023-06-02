import json
from pprint import pprint


with open('response_1685720803753.json', 'r', encoding='utf-8') as f:
    json_data = f.read()

data = json.loads(json_data)["data"]

pprint(len(data))

formatted_data = []
unique_combinations = set()

for item in data:
    combination = (item["currency"])
    if combination not in unique_combinations:
        unique_combinations.add(combination)
        formatted_item = {
            "currency_name": item["currency"],
            "currency_label": item["symbol"].upper()
        }
        formatted_data.append(formatted_item)

pprint(len(formatted_data))
with open('coin_list.json', 'w') as f:
    json.dump(formatted_data, f)