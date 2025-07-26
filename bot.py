import telebot
from telebot import types
import json
import os
import datetime
import requests

# === CONFIGURATION ===
API_TOKEN = "8068835959:AAGM2cjx58bOMXBCNlp9N6jqCdI8F-bIRBo"
GROUP_ID = -1001414774829
RECEIVER_WALLET = "0xC421E42508269556F0e19f2929378aA7499CD8Db"
QUICKNODE_HTTP = "https://solitary-wider-brook.bsc.quiknode.pro/1e79b2e9d43a0b25dbf1c9dd06fe44ab05d121da/"  # Replace with QuickNode endpoint
DATA_FILE = "data.json"

bot = telebot.TeleBot(API_TOKEN)

# === DATA STORAGE ===
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"users": {}, "used_tx": []}, f)


def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# === HELPERS ===
def add_subscription(user_id, package, days):
    data = load_data()
    expiry_date = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    data["users"][str(user_id)] = {"package": package, "expiry": expiry_date}
    save_data(data)


def is_active(user_id):
    data = load_data()
    user = data["users"].get(str(user_id))
    if not user:
        return False
    expiry = datetime.datetime.strptime(user["expiry"], "%Y-%m-%d %H:%M:%S")
    return datetime.datetime.now() < expiry


def verify_txhash(txhash, amount_expected):
    """Verify transaction via QuickNode"""
    try:
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "eth_getTransactionByHash",
            "params": [txhash]
        }
        response = requests.post(QUICKNODE_HTTP, json=payload)
        result = response.json().get("result")
        if not result:
            return False, "Invalid TxHash"

        # Check receiver address
        to_address = result.get("to", "").lower()
        if to_address != RECEIVER_WALLET.lower():
            return False, "Receiver wallet mismatch."

        # Convert value from hex to decimal
        value = int(result.get("value", "0x0"), 16) / (10 ** 18)
        if value < amount_expected:
            return False, f"Amount too low. Expected {amount_expected} USDT."

        return True, "Transaction verified."
    except Exception as e:
        return False, f"Error verifying TxHash: {e}"


def mute_user(user_id):
    try:
        bot.restrict_chat_member(GROUP_ID, user_id, can_send_messages=False)
    except:
        pass


def unmute_user(user_id):
    try:
        bot.restrict_chat_member(
            GROUP_ID, user_id,
            can_send_messages=True, can_send_media_messages=True,
            can_send_polls=True, can_send_other_messages=True
        )
    except:
        pass


# === COMMAND HANDLERS ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💳 Buy Subscription", "📜 My Subscription", "🆘 HelpLine")
    bot.send_message(message.chat.id, "Welcome! Please choose an option:", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "💳 Buy Subscription")
def buy_subscription(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Monthly - 2 USDT", callback_data="buy_monthly"))
    markup.add(types.InlineKeyboardButton("Yearly - 15 USDT", callback_data="buy_yearly"))
    bot.send_message(message.chat.id, "Choose your package:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_buy(call):
    package = "monthly" if call.data == "buy_monthly" else "yearly"
    amount = 2 if package == "monthly" else 15
    msg = (f"Send **{amount} USDT** to our official BSC wallet:\n`{RECEIVER_WALLET}`\n\n"
           f"Then send your TxHash here.")
    bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")
    bot.register_next_step_handler(call.message, lambda m: process_txhash(m, package, amount))


def process_txhash(message, package, amount):
    txhash = message.text.strip()
    data = load_data()

    if txhash in data["used_tx"]:
        bot.reply_to(message, "❌ This TxHash has already been used!")
        return

    bot.reply_to(message, "⏳ Verifying your payment, please wait...")
    verified, msg = verify_txhash(txhash, amount)
    if not verified:
        bot.reply_to(message, f"❌ Verification failed: {msg}")
        return

    data["used_tx"].append(txhash)
    save_data(data)

    days = 30 if package == "monthly" else 365
    add_subscription(message.from_user.id, package, days)
    unmute_user(message.from_user.id)
    bot.reply_to(message, f"✅ Congratulations! Your {package} package is active for {days} days.")


@bot.message_handler(func=lambda m: m.text == "📜 My Subscription")
def my_subscription(message):
    data = load_data()
    user = data["users"].get(str(message.from_user.id))
    if not user:
        bot.reply_to(message, "❌ You don't have any active subscription.")
        return
    bot.reply_to(message, f"Your Package: {user['package']}\nExpiry: {user['expiry']}")


@bot.message_handler(func=lambda m: m.text == "🆘 HelpLine")
def help_line(message):
    bot.reply_to(message, "For any issues, contact @Jebon111")


# === GROUP MESSAGE CONTROL ===
@bot.message_handler(content_types=['text'])
def check_group_messages(message):
    if message.chat.id == GROUP_ID:
        if not is_active(message.from_user.id):
            mute_user(message.from_user.id)
            bot.send_message(GROUP_ID, f"⛔ {message.from_user.first_name}, buy a package to chat!",
                             reply_markup=types.InlineKeyboardMarkup().add(
                                 types.InlineKeyboardButton("Buy Subscription", url="https://t.me/YOUR_BOT_USERNAME")
                             ))


print("Bot is running...")
bot.infinity_polling()
