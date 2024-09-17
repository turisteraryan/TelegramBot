import telebot
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

"""
🔹 Title: Ultimate Movie Download Bot
🔹 Purpose: A bot for searching and downloading movies.
🔹 Description: 
    - Users can search for movies by typing the movie name, and admins can upload movies using specific commands.
🔹 Version: 1.0.0
🔹 Release Date: September 7, 2024
🔹 Last Update: -
🔹 Developed by: @CodaZenith
🔹 Made by: @ClientName
"""


bot = telebot.TeleBot(os.getenv("7511000335:AAHCZz4yP6BhZxoKGOksndgSYg6Oy1WtAVQ"))

# Define Admin IDs
admin_ids = [1824621252]  # Add more admin IDs as needed

# To keep track of what we're asking from the admin
upload_states = {}

# Storage for uploaded movies
movies_db = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_message = (
        "🎬 <b>Welcome to the Ultimate Movie Download Bot!</b> 🎉\n\n"
        "Looking for the latest blockbusters or timeless classics? You've come to the right place! 🍿\n\n"
        "🌟 <b>Here's what you can do with this bot:</b>\n"
        "🔍 Search and download your favorite movies instantly!\n"
        "🎥 Get detailed information on trending movies.\n"
        "💬 Need suggestions? Just ask, and I'll recommend the best flicks!\n\n"
        "Please send me any movie name, and I'll try to find it for you! 🎞️\n\n"
        "<b>Made by</b> @ClientName\n"
        "<b>Developed by</b> @CodaZenith"
    )
    bot.reply_to(message, welcome_message, parse_mode='HTML')

@bot.message_handler(commands=['uploadfile'])
def initiate_upload_file(message):
    if message.from_user.id in admin_ids:
        bot.reply_to(message, "🎬 You are authorized to upload a movie! Please send me the <b>movie name</b> first.", parse_mode='HTML')
        upload_states[message.from_user.id] = {'step': 'name', 'type': 'file'}
    else:
        bot.reply_to(message, "🚫 You are not authorized to upload movies.")

@bot.message_handler(commands=['upload'])
def initiate_upload(message):
    if message.from_user.id in admin_ids:
        bot.reply_to(message, "🎬 You are authorized to upload a movie with more details! Please send me the <b>movie thumbnail</b> first.", parse_mode='HTML')
        upload_states[message.from_user.id] = {'step': 'thumbnail', 'type': 'detailed'}
    else:
        bot.reply_to(message, "🚫 You are not authorized to upload movies.")

@bot.message_handler(content_types=['photo'])
def handle_thumbnail(message):
    user_id = message.from_user.id
    if user_id in admin_ids and upload_states.get(user_id, {}).get('step') == 'thumbnail':
        upload_states[user_id]['thumbnail'] = message.photo[-1].file_id
        bot.reply_to(message, "👍 Thumbnail received! Now, please send me the <b>movie name</b>.", parse_mode='HTML')
        upload_states[user_id]['step'] = 'name'

@bot.message_handler(func=lambda message: message.from_user.id in admin_ids and upload_states.get(message.from_user.id, {}).get('step') == 'name')
def handle_name(message):
    user_id = message.from_user.id
    upload_states[user_id]['name'] = message.text.strip()
    if upload_states[user_id]['type'] == 'file':
        bot.reply_to(message, "🎞️ Got it! Please send me the <b>movie video file</b> (or any file).", parse_mode='HTML')
        upload_states[user_id]['step'] = 'file'
    elif upload_states[user_id]['type'] == 'detailed':
        bot.reply_to(message, "Now, please send me the <b>button titles</b> and <b>download links</b> in this format:\n\n<b>Format:</b>\nButtonTitle1 - URL1_!ButtonTitle2 - URL2, ButtonTitle3 - URL3_!ButtonTitle4 - URL4\n\nWhen you're done, type /finish to complete the upload.", parse_mode='HTML')
        upload_states[user_id]['step'] = 'buttons'

@bot.message_handler(content_types=['video', 'document'])
def handle_movie_file(message):
    user_id = message.from_user.id
    if user_id in admin_ids and upload_states.get(user_id, {}).get('step') == 'file':
        movie_name = upload_states[user_id]['name']
        movie_file = message.video.file_id if message.content_type == 'video' else message.document.file_id

        # Save the movie to the database
        movies_db[movie_name.lower()] = {'file': movie_file, 'name': movie_name}

        bot.reply_to(message, f"✅ Movie '<b>{movie_name}</b>' has been uploaded successfully!", parse_mode='HTML')

        # Clear the user's upload state
        del upload_states[user_id]

@bot.message_handler(func=lambda message: message.from_user.id in admin_ids and upload_states.get(message.from_user.id, {}).get('step') == 'buttons')
def handle_buttons(message):
    user_id = message.from_user.id
    buttons_text = message.text.strip()
    movie_name = upload_states[user_id]['name']
    thumbnail = upload_states[user_id]['thumbnail']

    buttons = []
    if buttons_text:
        button_groups = buttons_text.split(', ')
        for group in button_groups:
            titles_urls = group.split('_!')
            group_buttons = []
            for item in titles_urls:
                title, url = item.split(' - ')
                group_buttons.append(InlineKeyboardButton(text=title.strip(), url=url.strip()))
            buttons.extend(group_buttons)

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(*buttons)

    # Save the movie to the database
    movies_db[movie_name.lower()] = {'thumbnail': thumbnail, 'name': movie_name, 'buttons': markup}

    bot.reply_to(message, f"✅ Movie '<b>{movie_name}</b>' has been uploaded successfully with download links!", parse_mode='HTML')

    # Clear the user's upload state
    del upload_states[user_id]

@bot.message_handler(commands=['remove'])
def remove_movie(message):
    if message.from_user.id in admin_ids:
        if message.reply_to_message:
            # Handle removal by replying to a movie name or video file
            movie_name = message.reply_to_message.text.strip().lower() if message.reply_to_message.text else None
        else:
            # Handle removal by specifying the movie name directly in the command
            movie_name = message.text.split('/remove ', 1)[-1].strip().lower()

        if movie_name in movies_db:
            del movies_db[movie_name]
            bot.reply_to(message, f"✅ Movie '<b>{movie_name}</b>' has been successfully removed from the database.", parse_mode='HTML')
        else:
            bot.reply_to(message, f"❌ Movie '<b>{movie_name}</b>' not found in the database.", parse_mode='HTML')
    else:
        bot.reply_to(message, "🚫 You are not authorized to remove movies.")

@bot.message_handler(func=lambda message: not message.text.startswith('/'))
def search_movie(message):
    movie_name = message.text.strip().lower()

    checking_message = bot.reply_to(message, f"🔍 Checking for '<b>{message.text.strip()}</b>'...", parse_mode='HTML')

    if movie_name in movies_db:
        movie = movies_db[movie_name]

        bot.delete_message(message.chat.id, checking_message.message_id)

        if 'file' in movie:
            bot.send_video(message.chat.id, movie['file'], caption=f"🎬 <b>{movie['name']}</b> is available for download!", parse_mode='HTML')
        elif 'thumbnail' in movie and 'buttons' in movie:
            bot.send_photo(message.chat.id, movie['thumbnail'], caption=f"🎬 <b>{movie['name']}</b>' is available for download!", reply_markup=movie['buttons'], parse_mode='HTML')
    else:
        bot.delete_message(message.chat.id, checking_message.message_id)
        bot.reply_to(message, f"❌ Sorry, we couldn't find the movie '<b>{message.text.strip()}</b>' in our database.", parse_mode='HTML')

bot.infinity_polling()
        
