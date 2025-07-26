import telebot, json, time, threading
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from config import BOT_TOKEN, GROUP_ID, DATA_FILE
from payment_checker import is_valid_tx

bot = telebot.TeleBot(BOT_TOKEN)

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

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
bot.infinity_polling()
