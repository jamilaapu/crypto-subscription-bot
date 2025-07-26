import json, os
import telebot
from telebot import types
from config import *
from keep_alive import keep_alive
from payment_checker import verify_tx
from datetime import datetime, timedelta

bot = telebot.TeleBot(BOT_TOKEN)
keep_alive()

# ensure data files
if not os.path.exists(SUBSCRIPTIONS_FILE):
    with open(SUBSCRIPTIONS_FILE, "w") as f: json.dump({}, f)
if not os.path.exists(USED_TX_FILE):
    with open(USED_TX_FILE, "w") as f: json.dump([], f)

def load_subs():
    with open(SUBSCRIPTIONS_FILE) as f: return json.load(f)

def save_subs(d):
    with open(SUBSCRIPTIONS_FILE, "w") as f: json.dump(d, f, indent=2)

def load_used():
    with open(USED_TX_FILE) as f: return json.load(f)

def save_used(u):
    with open(USED_TX_FILE, "w") as f: json.dump(u, f, indent=2)

def is_active(uid):
    subs = load_subs()
    if str(uid) in subs:
        expiry = datetime.strptime(subs[str(uid)], "%Y-%m-%d %H:%M:%S")
        return datetime.now() < expiry
    return False

def restrict(uid):
    try:
        bot.restrict_chat_member(GROUP_ID, uid, can_send_messages=False)
    except: pass

def unrestrict(uid):
    try:
        bot.restrict_chat_member(GROUP_ID, uid,
            can_send_messages=True, can_send_media_messages=True,
            can_send_polls=True, can_send_other_messages=True)
    except: pass

@bot.message_handler(commands=['start','help'])
def cmd_start(msg):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💳 Buy Subscription", "📜 My Subscription")
    markup.row("🆘 HelpLine")
    bot.reply_to(msg, "Welcome! Choose option:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text=="💳 Buy Subscription")
def cmd_buy(msg):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("Monthly – 2 USDT", callback_data="buy_monthly"))
    kb.add(types.InlineKeyboardButton("Yearly – 15 USDT", callback_data="buy_yearly"))
    bot.send_message(msg.chat.id, f"Send USDT to:\n`{OFFICIAL_WALLET}`\nThen send TX Hash",
                     reply_markup=kb, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def cb_buy(c):
    amt = 2 if c.data=="buy_monthly" else 15
    pkg = "Monthly" if amt==2 else "Yearly"
    bot.answer_callback_query(c.id, f"{pkg} selected")
    bot.send_message(c.message.chat.id, "Now send your TxHash:")

@bot.message_handler(regexp="^0x[a-fA-F0-9]{64}$")
def recv_tx(msg):
    tx = msg.text.strip()
    used = load_used()
    if tx in used:
        return bot.reply_to(msg, "❌ This TxHash already used")
    bot.reply_to(msg, "⏳ Verifying TxHash...")
    ok, pkg = verify_tx(tx)
    if not ok:
        return bot.reply_to(msg, "❌ Invalid TxHash or amount too low")
    used.append(tx); save_used(used)
    subs = load_subs()
    exp = datetime.now() + timedelta(days=365 if pkg=="Yearly" else 30)
    subs[str(msg.from_user.id)] = exp.strftime("%Y-%m-%d %H:%M:%S")
    save_subs(subs)
    unrestrict(msg.from_user.id)
    bot.reply_to(msg, f"✅ Activated until {exp.strftime('%Y-%m-%d')}")

@bot.message_handler(func=lambda m: m.text=="📜 My Subscription")
def cmd_my(msg):
    subs = load_subs()
    info = subs.get(str(msg.from_user.id))
    if info:
        bot.reply_to(msg, f"Your package active till {info}")
    else:
        bot.reply_to(msg, "❌ No active subscription found")

@bot.message_handler(func=lambda m: m.text=="🆘 HelpLine")
def cmd_help(msg):
    bot.reply_to(msg, f"For help contact @Jebon111")

@bot.message_handler(func=lambda m: True, content_types=['text'])
def on_group(msg):
    if msg.chat.id == GROUP_ID and not is_active(msg.from_user.id):
        restrict(msg.from_user.id)
        bot.send_message(GROUP_ID,
                         f"⛔ @{msg.from_user.username}, please subscribe to chat!",
                         reply_markup=types.InlineKeyboardMarkup().add(
                             types.InlineKeyboardButton("Buy Subscription", url=f"https://t.me/{bot.get_me().username}")
                         ))

bot.infinity_polling()
