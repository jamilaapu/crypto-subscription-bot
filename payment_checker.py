import requests
from config import OFFICIAL_WALLET, QUICKNODE_RPC

def verify_tx(txhash):
    try:
        headers = {"Content-Type": "application/json"}
        data = {
            "jsonrpc": "2.0",
            "method": "eth_getTransactionByHash",
            "params": [txhash],
            "id": 1
        }
        res = requests.post(QUICKNODE_RPC, json=data, headers=headers).json()
        if not res.get("result"):
            return False, None
        txn = res["result"]
        if txn["to"].lower() != OFFICIAL_WALLET.lower():
            return False, None
        value = int(txn["value"], 16) / 1e18
        if value >= 15:
            return True, "Yearly"
        elif value >= 2:
            return True, "Monthly"
        return False, None
    except Exception as e:
        print("Tx error:", e)
        return False, None
