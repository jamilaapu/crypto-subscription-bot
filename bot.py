import telebot
from telebot.types import ChatPermissions
import json
import time
from datetime import datetime, timedelta
from keep_alive import keep_alive

BOT_TOKEN = "8068835959:AAGM2cjx58bOMXBCNlp9N6jqCdI8F-bIRBo"  # তোমার বট টোকেন
GROUP_ID = -1001414774829     # তোমার গ্রুপ আইডি

bot = telebot.TeleBot(BOT_TOKEN)

USER_DB_FILE = "users_db.json"


# ---- ইউজার ডেটাবেজ ----
def load_users():
    try:
        with open(USER_DB_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f, indent=4)

def is_subscribed(user_id):
    users = load_users()
    if str(user_id) in users:
        expiry = datetime.strptime(users[str(user_id)], "%Y-%m-%d %H:%M:%S")
        if expiry > datetime.now():
            return True
    return False

def add_subscription(user_id, days=30):
    users = load_users()
    expiry_date = datetime.now() + timedelta(days=days)
    users[str(user_id)] = expiry_date.strftime("%Y-%m-%d %H:%M:%S")
    save_users(users)


# ---- পারমিশন ----
def block_user(user_id):
    bot.restrict_chat_member(GROUP_ID, user_id, ChatPermissions(can_send_messages=False))

def allow_user(user_id):
    bot.restrict_chat_member(GROUP_ID, user_id, ChatPermissions(can_send_messages=True))

def check_subscriptions():
    users = load_users()
    for user_id, expiry in list(users.items()):
        expiry_date = datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S")
        if expiry_date <= datetime.now():
            block_user(int(user_id))
            del users[user_id]
    save_users(users)


# ---- কমান্ড হ্যান্ডলার ----
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "👋 হ্যালো! গ্রুপে মেসেজ করতে প্যাকেজ কিনতে /buy ব্যবহার করুন।")

@bot.message_handler(commands=['buy'])
def buy_subscription(message):
    user_id = message.from_user.id
    add_subscription(user_id, 30)  # ৩০ দিনের সাবস্ক্রিপশন
    allow_user(user_id)
    bot.reply_to(message, "✅ আপনার সাবস্ক্রিপশন অ্যাক্টিভ হয়েছে। এখন আপনি মেসেজ করতে পারবেন।")


# ---- গ্রুপে নতুন ইউজার ----
@bot.chat_member_handler()
def handle_new_member(update):
    if update.new_chat_member:
        user_id = update.new_chat_member.user.id
        if not is_subscribed(user_id):
            block_user(user_id)
            bot.send_message(GROUP_ID, f"👋 {update.new_chat_member.user.first_name}, সাবস্ক্রিপশন না কিনা পর্যন্ত আপনি মেসেজ করতে পারবেন না।")


# ---- মেসেজ ডিলিট ----
@bot.message_handler(func=lambda m: True)
def handle_messages(message):
    user_id = message.from_user.id
    if message.chat.id == GROUP_ID and not is_subscribed(user_id):
        bot.delete_message(GROUP_ID, message.message_id)
        bot.send_message(user_id, "❌ আপনার সাবস্ক্রিপশন নেই। /buy কমান্ড ব্যবহার করে কিনুন।")


# ---- বট রান ----
def run_bot():
    while True:
        check_subscriptions()
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_bot()
