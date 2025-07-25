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
            return json.load(f)
    except:
        return {}

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


# ---------------------------
# Run Bot
# ---------------------------
bot.infinity_polling()
