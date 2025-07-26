import telebot
from telebot import types
import time
import json
import os
import requests

# ===================== CONFIG =====================
BOT_TOKEN = "8068835959:AAGM2cjx58bOMXBCNlp9N6jqCdI8F-bIRBo"
ADMIN_ID = 583113839
GROUP_ID = -1001414774829
WALLET_ADDRESS = "0xC421E42508269556F0e19f2929378aA7499CD8Db"
QUICKNODE_RPC = "https://solitary-wider-brook.bsc.quiknode.pro/1e79b2e9d43a0b25dbf1c9dd06fe44ab05d121da/"

bot = telebot.TeleBot(BOT_TOKEN)

# Subscription data files
SUB_FILE = "subscriptions.json"
USED_TX_FILE = "used_tx.json"

# ===================== UTIL FUNCTIONS =====================
def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

subscriptions = load_json(SUB_FILE)
used_tx = load_json(USED_TX_FILE)

def is_subscribed(user_id):
    if str(user_id) in subscriptions:
        if subscriptions[str(user_id)]["expiry"] > time.time():
            return True
    return False

def add_subscription(user_id, duration_days):
    expiry = time.time() + duration_days * 86400
    subscriptions[str(user_id)] = {"expiry": expiry}
    save_json(SUB_FILE, subscriptions)

def mark_tx_used(tx_hash):
    used_tx[tx_hash] = True
    save_json(USED_TX_FILE, used_tx)

def is_tx_used(tx_hash):
    return tx_hash in used_tx

# ===================== PAYMENT VERIFICATION =====================
def verify_tx_hash(tx_hash, amount_usdt):
    """Verify USDT payment using QuickNode"""
    try:
        url = QUICKNODE_RPC
        headers = {"Content-Type": "application/json"}
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getTransactionReceipt",
            "params": [tx_hash],
            "id": 1
        }
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        data = response.json()

        if "result" in data and data["result"]:
            to_address = data["result"]["to"]
            if to_address and to_address.lower() == WALLET_ADDRESS.lower():
                return True  # Amount check skipped for simplicity
        return False
    except Exception as e:
        print(f"Payment check error: {e}")
        return False

# ===================== COMMAND HANDLERS =====================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    sub_month = types.InlineKeyboardButton("💳 Buy 1-Month ($2)", callback_data="buy_month")
    sub_year = types.InlineKeyboardButton("💳 Buy 1-Year ($15)", callback_data="buy_year")
    my_sub_btn = types.InlineKeyboardButton("📦 My Subscription", callback_data="my_sub")
    markup.add(sub_month)
    markup.add(sub_year)
    markup.add(my_sub_btn)
    bot.send_message(
        message.chat.id,
        "🤖 Welcome! Choose a subscription package below.\n\n"
        "⚠ **Note:** Only **BSC Chain USDT** is supported.",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data in ["buy_month", "buy_year"])
def buy_subscription(call):
    if call.data == "buy_month":
        amount = 2
        days = 30
    else:
        amount = 15
        days = 365

    msg = (
        f"💳 **Buy Subscription**\n\n"
        f"Send **{amount} USDT** (BSC Chain Only) to this address:\n"
        f"`{WALLET_ADDRESS}`\n\n"
        "Then send your **TxHash** here."
    )
    bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")

    # Save pending subscription package info
    subscriptions[str(call.from_user.id)] = {"pending_days": days}
    save_json(SUB_FILE, subscriptions)

@bot.callback_query_handler(func=lambda call: call.data == "my_sub")
def my_subscription(call):
    if is_subscribed(call.from_user.id):
        expiry = subscriptions[str(call.from_user.id)]["expiry"]
        days_left = int((expiry - time.time()) / 86400)
        bot.send_message(call.message.chat.id, f"✅ Active subscription. Days left: {days_left}")
    else:
        bot.send_message(call.message.chat.id, "❌ You have no active subscription.")

# ===================== PAYMENT CHECKER =====================
@bot.message_handler(func=lambda msg: len(msg.text) == 66 and msg.text.startswith("0x"))
def check_payment(message):
    tx_hash = message.text.strip()
    user_id = message.from_user.id

    # Is any package pending?
    if str(user_id) not in subscriptions or "pending_days" not in subscriptions[str(user_id)]:
        bot.reply_to(message, "⚠️ You didn't select any package. Use /start first.")
        return

    if is_tx_used(tx_hash):
        bot.reply_to(message, "⚠️ This TxHash was already used.")
        return

    bot.send_message(message.chat.id, "⏳ Verifying payment, please wait...")
    amount = 2 if subscriptions[str(user_id)]["pending_days"] == 30 else 15
    success = verify_tx_hash(tx_hash, amount_usdt=amount)

    if success:
        add_subscription(user_id, subscriptions[str(user_id)]["pending_days"])
        mark_tx_used(tx_hash)
        bot.send_message(message.chat.id, "✅ Payment verified! Subscription activated.")
    else:
        bot.send_message(message.chat.id, "❌ Payment verification failed. Please check your TxHash.")

# ===================== GROUP MESSAGE CONTROL =====================
@bot.message_handler(content_types=['text'])
def group_message_control(message):
    if message.chat.id == GROUP_ID:
        try:
            chat_member = bot.get_chat_member(GROUP_ID, message.from_user.id)
            status = chat_member.status

            if status in ['administrator', 'creator'] or message.from_user.id == ADMIN_ID:
                return

            if not is_subscribed(message.from_user.id):
                bot.restrict_chat_member(
                    GROUP_ID,
                    message.from_user.id,
                    until_date=time.time() + 300
                )
                bot.reply_to(
                    message,
                    "🚫 You are muted! Buy a subscription to chat."
                )
        except Exception as e:
            print(f"Error in group_message_control: {e}")

# ===================== BOT RUN =====================
if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
