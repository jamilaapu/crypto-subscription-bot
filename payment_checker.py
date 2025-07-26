from web3 import Web3

BSC_RPC = "https://solitary-wider-brook.bsc.quiknode.pro/1e79b2e9d43a0b25dbf1c9dd06fe44ab05d121da/"
TARGET_WALLET = "0xC421E42508269556F0e19f2929378aA7499CD8Db"

web3 = Web3(Web3.HTTPProvider(BSC_RPC))

def verify_txhash(txhash, required_amount):
    try:
        tx = web3.eth.get_transaction(txhash)
        if tx and tx['to'] and tx['to'].lower() == TARGET_WALLET.lower():
            value_usdt = Web3.from_wei(tx['value'], 'ether')
            return float(value_usdt) >= required_amount
        return False
    except Exception as e:
        print(f"Error verifying txhash: {e}")
        return False
