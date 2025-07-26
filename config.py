<<<<<<< HEAD
BOT_TOKEN = "8068835959:AAGM2cjx58bOMXBCNlp9N6jqCdI8F-bIRBo"
GROUP_ID = -1001414774829
DATA_FILE = "subscriptions.json"
TXHASH_FILE = "used_txhash.json"
WALLET_ADDRESS = "0xC421E42508269556F0e19f2929378aA7499CD8Db"  # Receiver Wallet

# QuickNode setup
QUICKNODE_URL = "https://solitary-wider-brook.bsc.quiknode.pro/1e79b2e9d43a0b25dbf1c9dd06fe44ab05d121da/"
EXPECTED_AMOUNT = {
    "basic": 2,
    "standard": 5,
    "premium": 15
}
=======
# config.py

# Telegram Bot Token
BOT_TOKEN = "8068835959:AAGM2cjx58bOMXBCNlp9N6jqCdI8F-bIRBo"

# BSC RPC (Binance Smart Chain Node)
BSC_RPC = "https://bsc-dataseed.binance.org/"

# Official Wallet Address (যেখানে পেমেন্ট আসবে)
from web3 import Web3
WALLET_ADDRESS = Web3.to_checksum_address("0xC421E42508269556F0e19f2929378aA7499CD8Db")


# Subscription Prices (in smallest unit, e.g., USDT decimals = 18)
MONTHLY_PRICE = 2 * (10 ** 18)  # 2 USDT
YEARLY_PRICE = 15 * (10 ** 18)  # 15 USDT

# JSON file to save users
USERS_DB_FILE = "users_db.json"
USED_TX_FILE = "used_tx.json"  # Already used TxHashes list
>>>>>>> a4d36114e0e0e58573a99dcdee0dbce47092fa68
