import requests, json
from config import QUICKNODE_URL, WALLET_ADDRESS, EXPECTED_AMOUNT, TXHASH_FILE

def is_valid_tx(txhash, package_name):
    with open(TXHASH_FILE, 'r') as f:
        used = json.load(f)
    if txhash in used:
        return False, "Already used"

    headers = {"Content-Type": "application/json"}
    payload = {
        "method": "eth_getTransactionByHash",
        "params": [txhash],
        "id": 1, "jsonrpc": "2.0"
    }

    try:
        res = requests.post(QUICKNODE_URL, headers=headers, json=payload)
        tx = res.json()['result']
        if tx is None:
            return False, "Invalid TX"

        to_address = tx['to'].lower()
        if to_address != WALLET_ADDRESS.lower():
            return False, "Wrong receiver"

        amount = int(tx['value'], 16) / 1e18
        if amount < EXPECTED_AMOUNT[package_name]:
            return False, "Amount too low"

        used[txhash] = True
        with open(TXHASH_FILE, 'w') as f:
            json.dump(used, f, indent=2)

        return True, ""
    except:
        return False, "Error"
