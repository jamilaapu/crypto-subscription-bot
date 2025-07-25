import time
import threading
from telebot import TeleBot
from payment_checker import check_subscriptions
from keep_alive import keep_alive

TOKEN = "YOUR_BOT_TOKEN"
bot = TeleBot(TOKEN)

# ---------- মেসেজ হ্যান্ডলার ----------
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    bot.delete_message(GROUP_ID, message.message_id)
    bot.send_message(message.chat.id, "আপনার সাবস্ক্রিপশন নেই। /buy কমান্ড ব্যবহার করে কিনুন!")

# ---------- বট চালানোর ফাংশন ----------
def run_bot():
    bot.remove_webhook()  # গুরুত্বপূর্ণ: webhook মুছে দিচ্ছে
    while True:
        try:
            bot.polling(none_stop=True, timeout=30)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

# ---------- সাবস্ক্রিপশন চেকার ----------
def schedule_checker():
    while True:
        check_subscriptions()
        time.sleep(60)  # প্রতি ১ মিনিটে সাবস্ক্রিপশন চেক করবে

# ---------- মেইন ----------
if __name__ == "__main__":
    # সাবস্ক্রিপশন চেক থ্রেড
    threading.Thread(target=schedule_checker, daemon=True).start()

    # Flask সার্ভার থ্রেড
    threading.Thread(target=keep_alive, daemon=True).start()

    # বট চালু
    run_bot()
