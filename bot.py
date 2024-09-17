import telebot

# Replace with your bot token
API_TOKEN = '7511000335:AAHCZz4yP6BhZxoKGOksndgSYg6Oy1WtAVQ'

# Initialize the bot
bot = telebot.TeleBot(API_TOKEN)

# Start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! How can I assist you today?")

# Echo handler (repeats whatever the user sends)
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)

# Polling for new messages
bot.polling()
