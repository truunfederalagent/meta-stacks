import requests, os, asyncio, aiofiles, time, json, base64
from aiohttp import ClientConnectionError, ClientSession
import imageio, cv2
from collections import defaultdict

path = 'meta_assets.json'
holders = defaultdict(int)
counts = defaultdict(int)
creators = ['2QDW33WUCFKDNEZEZPBF7MCJUOFWOTOPAL64NHHVXUXE5B6L5VKQMPYZXA', 'DTD2NBMU6VB2DVMRDEBTNTWVKATYOM5BN5Q26JRMKF5HTORLJ3U3ISYQDI']
elements = {}

if os.path.exists(path):
    with open(path) as f:
        assets = set(json.loads(f.read()))
else:
    assets = set()
    for creator in creators:
        url = f'https://algoindexer.algoexplorerapi.io/v2/assets?creator={creator}'
        data = requests.get(url).json()
        count = 0
        while 'next-token' in data:
            for asset in data['assets']:
                assets.add(asset['index'])
                count += 1
            data = requests.get(url+f'&next={data["next-token"]}').json()
    with open(path, 'w') as outfile:
        outfile.write(json.dumps(list(assets)))

async def get_meta_data(asset_id, session):
    confg_url = f'https://algoindexer.algoexplorerapi.io/v2/assets/{asset_id}/transactions?tx-type=acfg'
    config_data = await session.request(method='GET', url=confg_url)
    data = await config_data.json()
    for trans in data['transactions']:
        arc_69 = json.loads(base64.b64decode(trans['note']))
        if 'Name' in arc_69['properties']:
            elements[asset_id] = arc_69['properties']['Name']

async def fetch_meta(meta_id, session):
    try:
        asset_url = f'https://algoindexer.algoexplorerapi.io/v2/assets/{meta_id}/balances'
        asset_data = await session.request(method='GET', url = asset_url)
        data = await asset_data.json()
        for wallet in data['balances']:
            if wallet['address'] not in creators and wallet['amount'] == 1:
                holders[wallet['address']] += 1
        return await get_meta_data(meta_id, session)
    except ClientConnectionError:
        return None


async def fetch_all_metas(metas): 
    async with ClientSession() as session:
        tasks = []

        for meta in metas:
            tasks.append(
                fetch_meta(meta, session)
            )
        await asyncio.gather(*tasks)

    with open('asset-meta.json', 'w') as out:
        out.write(json.dumps(elements, indent=2))

asyncio.run(fetch_all_metas(assets))
