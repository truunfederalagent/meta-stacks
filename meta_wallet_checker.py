import json,requests
from collections import Counter

with open('asset-meta.json') as meta, open('meta_assets.json') as assets:
    metadata = json.loads(meta.read())
    meta_assets = set(json.loads(assets.read()))


def get_metas_by_wallet(wallet):
    wallet_url = f'https://algoindexer.algoexplorerapi.io/v2/accounts/{wallet}'
    data = requests.get(wallet_url).json()['account']['assets']
    holding = {}
    for asset in data:
        if asset['asset-id'] in meta_assets and asset['amount'] == 1:
            holding[asset['asset-id']] = metadata[str(asset['asset-id'])]

    return holding


def get_stacks(holdings):
    elements = list(holdings.values())
    counter = Counter(elements)
    return {el:count for el, count in counter.items() if count > 1}

def get_tickets(wallet):
    metas = get_metas_by_wallet(wallet)
    stacks = get_stacks(metas)
    return 1 if len(stacks) == 0 else sum(stacks.values())

wallet = '...'
print(get_tickets(wallet))
