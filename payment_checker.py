<<<<<<< HEAD
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
=======
from web3 import Web3
from config import BSC_RPC, WALLET_ADDRESS, MONTHLY_PRICE, YEARLY_PRICE

# BEP-20 USDT Contract (Binance Smart Chain)
USDT_CONTRACT = Web3.to_checksum_address("0x55d398326f99059fF775485246999027B3197955")  # BSC USDT
USDT_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"}
        ],
        "name": "Transfer",
        "type": "event"
    }
]

# BSC Connection
w3 = Web3(Web3.HTTPProvider(BSC_RPC))
if not w3.is_connected():
    raise Exception("[ERROR] Could not connect to Binance Smart Chain RPC.")

usdt_contract = w3.eth.contract(address=USDT_CONTRACT, abi=USDT_ABI)


def verify_transaction(txhash: str, required_amount: int) -> bool:
    """Check if the transaction hash is valid and payment matches."""
    try:
        txhash = txhash.strip()
        print(f"[DEBUG] Checking transaction: {txhash}")

        # Get transaction receipt
        receipt = w3.eth.get_transaction_receipt(txhash)
        logs = usdt_contract.events.Transfer().process_receipt(receipt)

        found_valid_transfer = False
        for log in logs:
            sender = log['args']['from']
            receiver = log['args']['to']
            value = log['args']['value']

            print(f"[DEBUG] Transfer Event => FROM: {sender} TO: {receiver} VALUE: {value}")

            # Check if payment sent to our wallet
            if receiver.lower() == WALLET_ADDRESS.lower():
                found_valid_transfer = True

                # Check amount
                if int(value) >= required_amount:
                    print("[SUCCESS] Transaction verified successfully!")
                    return True
                else:
                    print(f"[ERROR] Payment amount too low. Required: {required_amount}, Got: {value}")
                    return False

        if not found_valid_transfer:
            print("[ERROR] No valid token transfer to our wallet found.")
            return False

    except Exception as e:
        print("[ERROR] Error verifying transaction:", e)
        return False


# Testing (Only for Debugging)
if __name__ == "__main__":
    test_txhash = "0xYOUR_TEST_TXHASH"
    result = verify_transaction(test_txhash, MONTHLY_PRICE)
    print("Verify result:", result)
>>>>>>> a4d36114e0e0e58573a99dcdee0dbce47092fa68
