<<<<<<< HEAD
import telebot, json, time, threading
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from config import BOT_TOKEN, GROUP_ID, DATA_FILE
from payment_checker import is_valid_tx

bot = telebot.TeleBot(BOT_TOKEN)

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
=======
import telebot
from telebot import types
import json
from datetime import datetime, timedelta
from config import BOT_TOKEN, MONTHLY_PRICE, YEARLY_PRICE, USERS_DB_FILE, USED_TX_FILE
from payment_checker import verify_transaction

bot = telebot.TeleBot(BOT_TOKEN)

# ---------------------------
# Load and Save Functions
# ---------------------------
def load_users():
    try:
        with open(USERS_DB_FILE, "r") as f:
>>>>>>> a4d36114e0e0e58573a99dcdee0dbce47092fa68
            return json.load(f)
    except:
        return {}

<<<<<<< HEAD
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Welcome to the subscription bot!")

@bot.message_handler(func=lambda m: True)
def restrict_if_not_subscribed(message):
    user_id = str(message.from_user.id)
    subs = load_data()
    now = int(time.time())

    if str(message.chat.id) != str(GROUP_ID):
        return

    if user_id not in subs or subs[user_id]["expiry"] < now:
        try:
            bot.restrict_chat_member(
                GROUP_ID, message.from_user.id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔓 Unlock Access", url="https://t.me/CryptoBDBank_bot"))
            bot.reply_to(message, "🚫 You need to activate a package to chat.", reply_markup=markup)
        except Exception as e:
            print(f"Restrict failed: {e}")

@bot.callback_query_handler(func=lambda c: True)
def handle_callback(c):
    pass  # future use

@bot.message_handler(commands=['activate'])
def handle_activate(message):
    try:
        _, txhash, package = message.text.split()
    except:
        bot.reply_to(message, "❌ Format: /activate TXHASH package_name")
        return

    ok, reason = is_valid_tx(txhash, package)
    if not ok:
        bot.reply_to(message, f"❌ Invalid TX: {reason}")
        return

    user_id = str(message.from_user.id)
    subs = load_data()
    duration = 3 * 86400  # 3 days for example
    now = int(time.time())
    expiry = now + duration

    subs[user_id] = {"package": package, "expiry": expiry}
    save_data(subs)

    bot.restrict_chat_member(
        GROUP_ID, message.from_user.id,
        permissions=ChatPermissions(can_send_messages=True)
    )
    bot.reply_to(message, "✅ Activated successfully!")

def check_expired():
    subs = load_data()
    now = int(time.time())
    changed = False

    for user_id in list(subs):
        if subs[user_id]["expiry"] < now:
            try:
                bot.restrict_chat_member(
                    GROUP_ID, int(user_id),
                    permissions=ChatPermissions(can_send_messages=False)
                )
                print(f"⛔ Expired: {user_id}")
            except Exception as e:
                print(f"Restrict error: {e}")
            del subs[user_id]
            changed = True

    if changed:
        save_data(subs)

def background_task():
    while True:
        check_expired()
        time.sleep(3600)

threading.Thread(target=background_task, daemon=True).start()

print("✅ Bot is running...")
=======
def save_users(users):
    with open(USERS_DB_FILE, "w") as f:
        json.dump(users, f, indent=4)

def load_used_tx():
    try:
        with open(USED_TX_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_used_tx(tx_list):
    with open(USED_TX_FILE, "w") as f:
        json.dump(tx_list, f, indent=4)


# ---------------------------
# Main Menu
# ---------------------------
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💰 Buy Subscription", "📜 My Subscription")
    markup.add("☎ HelpLine")
    return markup


# ---------------------------
# Start Command
# ---------------------------
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Welcome to *Crypto BD Bank Subscription Bot*.\n\nPlease choose an option:",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )


# ---------------------------
# Buy Subscription
# ---------------------------
@bot.message_handler(func=lambda m: m.text == "💰 Buy Subscription")
def buy_subscription(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("👉 Monthly fee 2$ USDT", "👉 Yearly fee 15$ USDT")
    markup.add("🔙 Back")
    bot.send_message(message.chat.id, "Choice your package:", reply_markup=markup)


# ---------------------------
# Package Selected
# ---------------------------
@bot.message_handler(func=lambda m: m.text in ["👉 Monthly fee 2$ USDT", "👉 Yearly fee 15$ USDT"])
def select_package(message):
    user_id = str(message.from_user.id)
    users = load_users()
    users[user_id] = users.get(user_id, {})
    users[user_id]["selected_package"] = "monthly" if "Monthly" in message.text else "yearly"
    save_users(users)

    amount = "2$" if "Monthly" in message.text else "15$"
    bot.send_message(
        message.chat.id,
        f"Now send *{amount} USDT (BSC chain)* to our official wallet:\n\n"
        "`0xC421E42508269556F0e19f2929378aA7499CD8Db`\n\n"
        "Send Complete?\nNow Submit your *TxHash ID* 👇👇👇",
        parse_mode="Markdown"
    )


# ---------------------------
# My Subscription
# ---------------------------
@bot.message_handler(func=lambda m: m.text == "📜 My Subscription")
def my_subscription(message):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id not in users or "expiry" not in users[user_id]:
        bot.send_message(message.chat.id, "❌ You don't have any active subscription.")
        return

    pkg = users[user_id].get("package", "Unknown")
    expiry = users[user_id]["expiry"]
    bot.send_message(
        message.chat.id,
        f"📦 *Package:* {pkg.capitalize()}\n"
        f"⏳ *Expires on:* {expiry}",
        parse_mode="Markdown"
    )


# ---------------------------
# HelpLine
# ---------------------------
@bot.message_handler(func=lambda m: m.text == "☎ HelpLine")
def help_line(message):
    bot.send_message(message.chat.id, "For any issue contact: @Jebon111")


# ---------------------------
# Back Button
# ---------------------------
@bot.message_handler(func=lambda m: m.text == "🔙 Back")
def go_back(message):
    bot.send_message(message.chat.id, "Main menu:", reply_markup=main_menu())


# ---------------------------
# TxHash Input
# ---------------------------
@bot.message_handler(func=lambda m: m.text.startswith("0x") and len(m.text) > 10)
def handle_txhash(message):
    user_id = str(message.from_user.id)
    txhash = message.text.strip()

    used_tx = load_used_tx()
    if txhash in used_tx:
        bot.send_message(message.chat.id, "⚠ This TxHash was already used.")
        return

    users = load_users()
    if user_id not in users or "selected_package" not in users[user_id]:
        bot.send_message(message.chat.id, "❌ Please choose a package first from *Buy Subscription*.", parse_mode="Markdown")
        return

    pkg = users[user_id]["selected_package"]
    required_amount = MONTHLY_PRICE if pkg == "monthly" else YEARLY_PRICE

    bot.send_message(message.chat.id, "⏳ Checking your payment, please wait...")
    success = verify_transaction(txhash, required_amount)

    if success:
        expiry = datetime.now() + (timedelta(days=30) if pkg == "monthly" else timedelta(days=365))
        users[user_id]["package"] = pkg
        users[user_id]["expiry"] = expiry.strftime("%Y-%m-%d")
        save_users(users)

        used_tx.append(txhash)
        save_used_tx(used_tx)

        bot.send_message(
            message.chat.id,
            f"🎉 *Congratulations!* Your subscription is now active!\n\n"
            f"Package: *{pkg.capitalize()}*\n"
            f"Expires on: {expiry.strftime('%Y-%m-%d')}\n\n"
            "Go to 📜 *My Subscription* to see details.",
            parse_mode="Markdown"
        )
    else:
        bot.send_message(message.chat.id, "❌ Payment not verified. Try again.")

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

# ---------------------------
# Run Bot
# ---------------------------
>>>>>>> a4d36114e0e0e58573a99dcdee0dbce47092fa68
bot.infinity_polling()
