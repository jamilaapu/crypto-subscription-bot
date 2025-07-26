import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import init_db, add_subscription, check_subscription, is_txhash_used, remove_expired_subscriptions
from payment_checker import verify_txhash
from datetime import datetime
import threading
import time

# ===== BOT CONFIG =====
BOT_TOKEN = "8068835959:AAGM2cjx58bOMXBCNlp9N6jqCdI8F-bIRBo"
ADMIN_ID = 583113839
GROUP_ID = -1001414774829  # তোমার গ্রুপের আসল ID দিয়ে দাও

bot = telebot.TeleBot(BOT_TOKEN)
init_db()


# ===== Remove expired subscriptions periodically =====
def subscription_cleaner():
    while True:
        remove_expired_subscriptions()
        time.sleep(3600)  # প্রতি ঘন্টায় চেক করবে


threading.Thread(target=subscription_cleaner, daemon=True).start()


# ===== Main Menu =====
def main_menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("Buy Subscription", callback_data="buy_subscription"),
        InlineKeyboardButton("My Subscription", callback_data="my_subscription"),
        InlineKeyboardButton("HelpLine", callback_data="helpline")
    )
    return markup


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Welcome! Choose an option below:", reply_markup=main_menu())


# ===== CALLBACK HANDLER =====
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "buy_subscription":
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("Monthly - 2 USDT", callback_data="buy_monthly"),
            InlineKeyboardButton("Yearly - 15 USDT", callback_data="buy_yearly"),
            InlineKeyboardButton("🔙 Back", callback_data="main_menu")
        )
        bot.edit_message_text("Choose your package:", call.message.chat.id, call.message.message_id,
                              reply_markup=markup)

    elif call.data == "buy_monthly":
        bot.send_message(call.message.chat.id,
                         "Send **2 USDT (BSC)** to our official wallet:\n\n`0xC421E42508269556F0e19f2929378aA7499CD8Db`\n\nThen submit your TxHash with /verify <TxHash>")

    elif call.data == "buy_yearly":
        bot.send_message(call.message.chat.id,
                         "Send **15 USDT (BSC)** to our official wallet:\n\n`0xC421E42508269556F0e19f2929378aA7499CD8Db`\n\nThen submit your TxHash with /verify <TxHash>")

    elif call.data == "my_subscription":
        package, expiry = check_subscription(call.from_user.id)
        if package:
            bot.send_message(call.message.chat.id, f"Your active package: {package}\nExpires on: {expiry}")
        else:
            bot.send_message(call.message.chat.id, "You have no active subscription.")

    elif call.data == "helpline":
        bot.send_message(call.message.chat.id, "For help, contact @Jebon111")

    elif call.data == "main_menu":
        bot.edit_message_text("Welcome! Choose an option below:", call.message.chat.id, call.message.message_id,
                              reply_markup=main_menu())


# ===== VERIFY TXHASH =====
@bot.message_handler(commands=['verify'])
def verify_txhash_handler(message):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "Usage: /verify <TxHash>")
            return

        txhash = parts[1].strip()
        if is_txhash_used(txhash):
            bot.reply_to(message, "This TxHash has already been used!")
            return

        user_id = message.from_user.id

        # প্রথমে Monthly ট্রাই করব
        if verify_txhash(txhash, 2):
            add_subscription(user_id, "monthly", txhash)
            bot.reply_to(message, "✅ Monthly package activated!")
            grant_group_permission(user_id)
        elif verify_txhash(txhash, 15):
            add_subscription(user_id, "yearly", txhash)
            bot.reply_to(message, "✅ Yearly package activated!")
            grant_group_permission(user_id)
        else:
            bot.reply_to(message, "❌ Invalid TxHash or wrong amount.")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")


# ===== Group Permission =====
def grant_group_permission(user_id):
    try:
        bot.restrict_chat_member(GROUP_ID, user_id, can_send_messages=True)
    except Exception as e:
        print(f"Error granting permission: {e}")


def revoke_group_permission(user_id):
    try:
        bot.restrict_chat_member(GROUP_ID, user_id, can_send_messages=False)
    except Exception as e:
        print(f"Error revoking permission: {e}")


# ===== Start Bot =====
print("Bot is running...")
bot.infinity_polling()
