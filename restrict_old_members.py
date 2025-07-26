import telebot
from telebot.types import ChatPermissions
import json

# Bot Token & Group ID
BOT_TOKEN = "8068835959:AAGM2cjx58bOMXBCNlp9N6jqCdI8F-bIRBo"
GROUP_ID = -1001414774829
DATA_FILE = "subscriptions.json"

bot = telebot.TeleBot(BOT_TOKEN)

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def restrict_non_subscribers():
    subs = load_data()
    try:
        # Get all admins
        members = bot.get_chat_administrators(GROUP_ID)
        admins = [admin.user.id for admin in members]
        print(f"Admin IDs: {admins}")

        # TODO: Replace with actual group member IDs
        group_members = [12345678, 987654321, 583113839]

        for user_id in group_members:
            if str(user_id) not in subs and user_id not in admins:
                try:
                    bot.restrict_chat_member(
                        GROUP_ID,
                        user_id,
                        ChatPermissions(can_send_messages=False)
                    )
                    print(f"User {user_id} restricted.")
                except Exception as e:
                    print(f"Error restricting {user_id}: {e}")

    except Exception as e:
        print(f"Error fetching members: {e}")

if __name__ == "__main__":
    restrict_non_subscribers()
