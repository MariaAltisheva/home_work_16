import json

def dictionary_users():
    with open('data/users.json', encoding='utf-8') as file:
         raw_json = file.read()
    return json.loads(raw_json)

def dictionary_offers():
    with open('data/offers.json', encoding='utf-8') as file:
        raw_json = file.read()
    return json.loads(raw_json)

def dictionary_orders():
    with open('data/orders.json', encoding='utf-8') as file:
        raw_json = file.read()
    return json.loads(raw_json)
