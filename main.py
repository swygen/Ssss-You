import logging
from aiogram import Bot, Dispatcher, executor, types
import requests
import asyncio
from keep_alive import keep_alive  # হোস্টিং বা সার্ভার চালু রাখতে

# Bot Token & API Key
API_TOKEN = '7310009275:AAGsgHRrHfclSgGE4wLA8yWz9RWAFEmufP4'
RAPIDAPI_KEY = 'b4d6936178mshafaf4aec9942f2ap16237ejsn4249014c201e'

# লগিং চালু
logging.basicConfig(level=logging.INFO)

# বট সেটআপ
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ইউজার লিংক রাখার ডিকশনারি
user_links = {}

# ইউজার সদস্যপদ
user_membership = {}

# স্বাগতম বার্তা
WELCOME_MSG = """👋 স্বাগতম, {name}!

এই বট ব্যবহার করে আপনি সহজেই TikTok ভিডিও **Watermark ছাড়া** ডাউনলোড করতে পারবেন।

✨ ফিচার:
- ✅ ভিডিও ডাউনলোড
- ✅ অডিও ডাউনলোড (যদি উপলব্ধ থাকে)

নিচে থেকে একটি অপশন বেছে নিন:"""

# Start Command
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("▶️ Download Video", "👨‍💻 Developer", "💎 Membership")
    await message.answer(WELCOME_MSG.format(name=message.from_user.first_name), reply_markup=keyboard)

# Download অপশন
@dp.message_handler(lambda message: message.text == "▶️ Download Video")
async def ask_for_link(message: types.Message):
    await message.reply("🔗 অনুগ্রহ করে TikTok ভিডিওর লিংক পাঠান।")

# Developer Info
@dp.message_handler(lambda message: message.text == "👨‍💻 Developer")
async def show_developer_info(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("📩 Admin Contact", url="https://t.me/Swygen_bot"))
    await message.reply("এই বটটি তৈরি করেছেন Swygen Official।\nযোগাযোগ করতে নিচের বাটনে ক্লিক করুন:", reply_markup=keyboard)

# Membership
@dp.message_handler(lambda message: message.text == "💎 Membership")
async def show_membership_info(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_membership:
        user_membership[user_id] = {"status": "free", "downloads_left": 15}  # free membership with 15 downloads

    membership_info = f"আপনার বর্তমান সদস্যপদ: {user_membership[user_id]['status'].capitalize()} \n"
    membership_info += f"বাকি ডাউনলোড: {user_membership[user_id]['downloads_left']} \n"
    membership_info += "আপনি ভিডিও ও অডিও ডাউনলোড করতে পারবেন।"
    
    await message.reply(membership_info)

# TikTok লিংক হ্যান্ডলার
@dp.message_handler(lambda message: "tiktok.com" in message.text)
async def ask_format(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_membership and user_membership[user_id]["downloads_left"] <= 0:
        await message.reply("⚠️ আপনার ডাউনলোড সীমা শেষ হয়ে গেছে, দয়া করে আবার চেষ্টা করুন কাল!")
        return

    user_links[user_id] = message.text
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("🎬 Download Video", callback_data="download_video"),
        types.InlineKeyboardButton("🎵 Download Audio", callback_data="download_audio")
    )
    await message.reply("আপনি কোন ফরম্যাটে ডাউনলোড করতে চান?", reply_markup=keyboard)

# ডাউনলোড প্রসেসিং
@dp.callback_query_handler(lambda c: c.data in ["download_video", "download_audio"])
async def process_download_option(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    tiktok_url = user_links.get(user_id)

    if not tiktok_url:
        await callback_query.message.answer("❌ লিংক পাওয়া যায়নি, অনুগ্রহ করে আবার চেষ্টা করুন।")
        return

    if user_id in user_membership and user_membership[user_id]["downloads_left"] <= 0:
        await callback_query.message.answer("⚠️ আপনার ডাউনলোড সীমা শেষ হয়ে গেছে, দয়া করে আবার চেষ্টা করুন কাল!")
        return

    await callback_query.message.answer("⏳ ডাউনলোড হচ্ছে... অনুগ্রহ করে অপেক্ষা করুন...")

    api_url = "https://tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com/index"
    headers = {
        "x-rapidapi-host": "tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com",
        "x-rapidapi-key": RAPIDAPI_KEY
    }
    params = {"url": tiktok_url}

    try:
        response = requests.get(api_url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if callback_query.data == "download_video":
                video_url = data.get("video", [None])[0]
                if video_url:
                    sent_msg = await callback_query.message.answer_video(video_url, caption="✅ ভিডিও সফলভাবে ডাউনলোড হয়েছে!")
                    # Deduct one download from the user's limit
                    user_membership[user_id]["downloads_left"] -= 1
                else:
                    await callback_query.message.answer("❌ ভিডিও লিংক খুঁজে পাওয়া যায়নি।")
                    return
            else:
                music_list = data.get("music")
                if music_list and isinstance(music_list, list) and music_list[0]:
                    music_url = music_list[0]
                    audio_button = types.InlineKeyboardMarkup()
                    audio_button.add(types.InlineKeyboardButton("🎵 অডিও ডাউনলোড করুন", url=music_url))
                    await callback_query.message.answer("✅ অডিও তৈরি হয়েছে। নিচের বাটনে ক্লিক করে ডাউনলোড করুন:", reply_markup=audio_button)

                    # Deduct one download from the user's limit
                    user_membership[user_id]["downloads_left"] -= 1
                else:
                    await callback_query.message.answer("❌ এই ভিডিওর জন্য আলাদা অডিও খুঁজে পাওয়া যায়নি।")
                    return

            await callback_query.answer()

            # Feedback বাটন
            feedback_keyboard = types.InlineKeyboardMarkup()
            feedback_keyboard.add(types.InlineKeyboardButton("⭐ মতামত দিন", url="https://t.me/Swygen_bd"))
            await callback_query.message.answer("আপনার অভিজ্ঞতা কেমন ছিল? নিচে ক্লিক করে জানান:", reply_markup=feedback_keyboard)

            # মিডিয়া ১ ঘণ্টা পর মুছে ফেলা
            await asyncio.sleep(3600)
            await sent_msg.delete()
        else:
            await callback_query.message.answer("❌ ডাউনলোডে সমস্যা হয়েছে, কিছুক্ষণ পরে চেষ্টা করুন।")
    except Exception as e:
        await callback_query.message.answer(f"⚠️ ত্রুটি ঘটেছে: {str(e)}")

# বট চালু রাখার জন্য
if __name__ == '__main__':
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
