import telebot
from telebot.types import ChatPermissions
from config import BOT_TOKEN, GROUP_ID

bot = telebot.TeleBot(BOT_TOKEN)

group_members = [1991832392,]  # <-- manually export list from @GroupHelpBot or @GroupHelpHelper

for uid in group_members:
    try:
        bot.restrict_chat_member(
            GROUP_ID, uid,
            permissions=ChatPermissions(can_send_messages=False)
        )
        print(f"Restricted {uid}")
    except Exception as e:
        print(f"Failed {uid}: {e}")
