import telebot
from telebot import types
import json
import time
import requests
from datetime import datetime, timedelta

# ============ CONFIG ============
API_TOKEN = "8068835959:AAGM2cjx58bOMXBCNlp9N6jqCdI8F-bIRBo"
GROUP_ID = -1001414774829  # তোমার গ্রুপ আইডি
WALLET_ADDRESS = "0xC421E42508269556F0e19f2929378aA7499CD8Db"
QUICKNODE_URL = "https://solitary-wider-brook.bsc.quiknode.pro/1e79b2e9d43a0b25dbf1c9dd06fe44ab05d121da/"  # তোমার QuickNode URL
PRICE_MONTHLY = 2    # USDT
PRICE_YEARLY = 15    # USDT
DATA_FILE = "subscriptions.json"
bot = telebot.TeleBot(API_TOKEN)
# ================================


# ============ UTILITIES ============
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def restrict_user(user_id):
    """গ্রুপে ইউজারের permission OFF করে দেবে"""
    try:
        perms = telebot.types.ChatPermissions(can_send_messages=False)
        bot.restrict_chat_member(GROUP_ID, user_id, permissions=perms)
    except Exception as e:
        print(f"[ERROR] Restrict failed: {e}")


def unrestrict_user(user_id):
    """গ্রুপে ইউজারের permission ON করে দেবে"""
    try:
        perms = telebot.types.ChatPermissions(can_send_messages=True,
                                              can_send_media_messages=True,
                                              can_send_other_messages=True)
        bot.restrict_chat_member(GROUP_ID, user_id, permissions=perms)
    except Exception as e:
        print(f"[ERROR] Unrestrict failed: {e}")


def verify_txhash(txhash, required_amount):
    """
    QuickNode ব্যবহার করে ট্রানজেকশন ভেরিফাই করবে।
    """
    try:
        headers = {"Content-Type": "application/json"}
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "eth_getTransactionByHash",
            "params": [txhash]
        }
        response = requests.post(QUICKNODE_URL, json=payload, headers=headers)
        data = response.json()

        if "result" in data and data["result"] is not None:
            to_addr = data["result"]["to"]
            if to_addr.lower() == WALLET_ADDRESS.lower():
                return True  # এখানে চাইলে value চেক করতে পারো
        return False
    except Exception as e:
        print(f"[ERROR] TX Verify: {e}")
        return False


def check_expired():
    """প্রতি ঘণ্টায় subscription মেয়াদ চেক করে expire করলে permission অফ করবে।"""
    data = load_data()
    updated = False
    now = int(time.time())

    for uid, sub in data.items():
        if sub["expiry"] < now:
            restrict_user(int(uid))
            data[uid]["active"] = False
            updated = True

    if updated:
        save_data(data)


def show_banner_if_needed(user_id):
    """যাদের প্যাকেজ নাই তাদের Banner পাঠাবে।"""
    data = load_data()
    if str(user_id) not in data or not data[str(user_id)]["active"]:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("🔑 Activate Now", url="https://t.me/CryptoBDBank_bot")
        markup.add(btn)
        bot.send_message(GROUP_ID, "🔒 **Access Locked!**\nপ্যাকেজ কিনে চ্যাট করার অনুমতি পান।", reply_markup=markup, parse_mode="Markdown")
# ==================================


# ============ COMMAND HANDLERS ============
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("💳 Buy Subscription")
    btn2 = types.KeyboardButton("📜 My Subscription")
    btn3 = types.KeyboardButton("🆘 HelpLine")
    markup.add(btn1, btn2, btn3)

    bot.send_message(message.chat.id,
                     "👋 Welcome! Choose an option below:",
                     reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "💳 Buy Subscription")
def buy_subscription(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👉 Monthly Fee 2$ USDT")
    btn2 = types.KeyboardButton("👉 Yearly Fee 15$ USDT")
    btn_back = types.KeyboardButton("🔙 Back")
    markup.add(btn1, btn2, btn_back)
    bot.send_message(message.chat.id, "Choose your package:", reply_markup=markup)


@bot.message_handler(func=lambda m: "Monthly Fee" in m.text or "Yearly Fee" in m.text)
def package_selected(message):
    if "Monthly" in message.text:
        price = PRICE_MONTHLY
        package_type = "monthly"
    else:
        price = PRICE_YEARLY
        package_type = "yearly"

    bot.send_message(
        message.chat.id,
        f"Send **{price}$ USDT** (BSC chain) to:\n\n`{WALLET_ADDRESS}`\n\n"
        "Then submit your TxHash ID:",
        parse_mode="Markdown"
    )

    bot.register_next_step_handler(message, process_txhash, package_type)


def process_txhash(message, package_type):
    txhash = message.text.strip()
    price = PRICE_MONTHLY if package_type == "monthly" else PRICE_YEARLY

    bot.send_message(message.chat.id, "🔍 Verifying your transaction...")
    if verify_txhash(txhash, price):
        data = load_data()
        user_id = str(message.from_user.id)
        duration = 30 * 24 * 3600 if package_type == "monthly" else 365 * 24 * 3600

        data[user_id] = {
            "package": package_type,
            "expiry": int(time.time()) + duration,
            "active": True,
            "txhash": txhash
        }
        save_data(data)

        unrestrict_user(message.from_user.id)
        bot.send_message(message.chat.id, "✅ Subscription Activated! You can now chat in the group.")
    else:
        bot.send_message(message.chat.id, "❌ Invalid TxHash or Payment not found.")


@bot.message_handler(func=lambda m: m.text == "📜 My Subscription")
def my_subscription(message):
    data = load_data()
    user_id = str(message.from_user.id)

    if user_id in data and data[user_id]["active"]:
        expiry_time = datetime.fromtimestamp(data[user_id]["expiry"]).strftime("%Y-%m-%d %H:%M")
        bot.send_message(message.chat.id, f"📦 Package: {data[user_id]['package'].capitalize()}\n⏳ Expiry: {expiry_time}")
    else:
        bot.send_message(message.chat.id, "❌ You have no active subscription.")


@bot.message_handler(func=lambda m: m.text == "🆘 HelpLine")
def helpline(message):
    bot.send_message(message.chat.id, "For any help, contact: @Jebon111")


@bot.message_handler(func=lambda m: m.text == "🔙 Back")
def back_to_main(message):
    send_welcome(message)
# =========================================


# ============ RESTRICT NON-SUBSCRIBERS ============
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'sticker'])
def block_non_subscribers(message):
    if message.chat.id == GROUP_ID and not message.from_user.is_bot:
        data = load_data()
        uid = str(message.from_user.id)

        if uid not in data or not data[uid]["active"]:
            try:
                restrict_user(message.from_user.id)
                show_banner_if_needed(message.from_user.id)
                bot.delete_message(GROUP_ID, message.message_id)
            except:
                pass
# ================================================


# ============ BACKGROUND TASK ============
import threading

def background_task():
    while True:
        check_expired()
        time.sleep(3600)  # প্রতি ১ ঘণ্টা পর চেক করবে

threading.Thread(target=background_task, daemon=True).start()
# =========================================


print("🤖 Bot is running...")
bot.infinity_polling()
