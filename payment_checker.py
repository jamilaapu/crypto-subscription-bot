import requests
from decimal import Decimal

# QuickNode Endpoint
QUICKNODE_URL = "https://solitary-wider-brook.bsc.quiknode.pro/1e79b2e9d43a0b25dbf1c9dd06fe44ab05d121da/"
USDT_CONTRACT = "0x55d398326f99059fF775485246999027b3197955"

def verify_txhash(txhash, to_address, required_amount):
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_getTransactionReceipt",
            "params": [txhash]
        }
        r = requests.post(QUICKNODE_URL, json=payload)
        data = r.json()

        if "result" not in data or data["result"] is None:
            return False

        receipt = data["result"]
        logs = receipt.get("logs", [])

        for log in logs:
            if log["address"].lower() == USDT_CONTRACT.lower():
                topics = log["topics"]
                if len(topics) >= 3:
                    to = "0x" + topics[2][-40:]
                    if to.lower() == to_address.lower():
                        # এখানে Amount চেক করব
                        value_hex = log["data"]
                        value = int(value_hex, 16) / (10 ** 18)
                        if Decimal(value) >= Decimal(required_amount):
                            return True
        return False
    except Exception as e:
        print("Error verifying payment:", e)
        return False
