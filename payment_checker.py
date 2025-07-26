import requests

# তোমার অফিসিয়াল ওয়ালেট
OFFICIAL_WALLET = "0xC421E42508269556F0e19f2929378aA7499CD8Db".lower()

# সাপোর্টেড টোকেন কন্ট্রাক্ট (USDT এবং Binance-Peg BSC-USD)
SUPPORTED_TOKENS = [
    "0x55d398326f99059fF775485246999027b3197955".lower(),  # USDT (BEP20)
    "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d".lower(),  # Binance-Peg BSC-USD
]

# মিনিমাম পেমেন্ট (USD)
MIN_AMOUNT = 2.0

# তোমার QuickNode RPC
QN_RPC = "https://solitary-wider-brook.bsc.quiknode.pro/1e79b2e9d43a0b25dbf1c9dd06fe44ab05d121da/"

def verify_txhash(tx_hash):
    """
    QuickNode দিয়ে TxHash চেক করা হবে।
    সঠিক হলে True রিটার্ন করবে, না হলে False।
    """

    try:
        # QuickNode RPC Call
        data = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "eth_getTransactionReceipt",
            "params": [tx_hash]
        }
        response = requests.post(QN_RPC, json=data, timeout=10)
        receipt = response.json()

        # Debug print (Render logs এ দেখতে পারবে)
        print("QuickNode Receipt:", receipt)

        if "result" not in receipt or receipt["result"] is None:
            return False  # TxHash invalid

        logs = receipt["result"].get("logs", [])
        for log in logs:
            # Contract Address চেক করো
            contract_addr = log.get("address", "").lower()
            if contract_addr in SUPPORTED_TOKENS:
                topics = log.get("topics", [])
                if len(topics) >= 3:
                    # Receiver ওয়ালেট চেক করো
                    to_wallet = "0x" + topics[2][-40:]
                    if to_wallet.lower() == OFFICIAL_WALLET:
                        # Amount (Hex থেকে Decimal এ কনভার্ট)
                        amount = int(log.get("data", "0x0"), 16) / (10 ** 18)
                        print(f"Detected Amount: {amount} USD")

                        if amount >= MIN_AMOUNT:
                            return True
                        else:
                            return False
        return False

    except Exception as e:
        print(f"Error verifying TxHash: {e}")
        return False
