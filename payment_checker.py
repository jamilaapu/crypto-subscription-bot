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
