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
