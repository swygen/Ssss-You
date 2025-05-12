import logging
from aiogram import Bot, Dispatcher, executor, types
import requests
import asyncio
from keep_alive import keep_alive
from datetime import datetime, timedelta

API_TOKEN = '7310009275:AAGsgHRrHfclSgGE4wLA8yWz9RWAFEmufP4'
RAPIDAPI_KEY = 'b4d6936178mshafaf4aec9942f2ap16237ejsn4249014c201e'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_links = {}
user_limits = {}  # ইউজার আইডি অনুযায়ী ডাউনলোড লিমিট ট্র্যাক করবে

WELCOME_MSG = """👋 স্বাগতম, {name}!

এই বট ব্যবহার করে আপনি সহজেই TikTok ভিডিও **Watermark ছাড়া** ডাউনলোড করতে পারবেন।

✨ ফিচার:
- ✅ ভিডিও ডাউনলোড
- ✅ অডিও ডাউনলোড
- ✅ ডেইলি ১৫টি ফ্রি ডাউনলোড (Free Membership)

নিচে থেকে একটি অপশন বেছে নিন:"""

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("▶️ Download Video", "👨‍💻 Developer", "⭐ Membership")
    await message.answer(WELCOME_MSG.format(name=message.from_user.first_name), reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "▶️ Download Video")
async def ask_for_link(message: types.Message):
    await message.reply("🔗 অনুগ্রহ করে TikTok ভিডিওর লিংক পাঠান।")

@dp.message_handler(lambda message: message.text == "👨‍💻 Developer")
async def show_developer_info(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("📩 Admin Contact", url="https://t.me/Swygen_bot"))
    await message.reply("এই বটটি তৈরি করেছেন Swygen Official।\nযোগাযোগ করতে নিচের বাটনে ক্লিক করুন:", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "⭐ Membership")
async def show_membership(message: types.Message):
    await message.reply("আপনি বর্তমানে ⭐ Free Membership-এ আছেন।\nপ্রতিদিন ১৫টি ভিডিও/অডিও ডাউনলোড করতে পারবেন।\n\nডাউনলোড করতে ▶️ Download Video বাটনে ক্লিক করুন।")

@dp.message_handler(lambda message: "tiktok.com" in message.text)
async def ask_format(message: types.Message):
    user_links[message.from_user.id] = message.text
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("🎬 Download Video", callback_data="download_video"),
        types.InlineKeyboardButton("🎵 Download Audio", callback_data="download_audio")
    )
    await message.reply("আপনি কোন ফরম্যাটে ডাউনলোড করতে চান?", reply_markup=keyboard)

def check_limit(user_id):
    today = datetime.now().date()
    if user_id not in user_limits:
        user_limits[user_id] = {"date": today, "count": 0}
    elif user_limits[user_id]["date"] != today:
        user_limits[user_id] = {"date": today, "count": 0}
    return user_limits[user_id]["count"] < 15

def increment_limit(user_id):
    user_limits[user_id]["count"] += 1

@dp.callback_query_handler(lambda c: c.data in ["download_video", "download_audio"])
async def process_download_option(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if not check_limit(user_id):
        await callback_query.message.answer("⚠️ আপনি আজকের ১৫টি ফ্রি ডাউনলোড সীমা পূর্ণ করেছেন।\nআগামীকাল আবার চেষ্টা করুন।")
        return

    tiktok_url = user_links.get(user_id)
    if not tiktok_url:
        await callback_query.message.answer("❌ লিংক পাওয়া যায়নি, অনুগ্রহ করে আবার চেষ্টা করুন।")
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
                else:
                    await callback_query.message.answer("❌ ভিডিও লিংক খুঁজে পাওয়া যায়নি।")
                    return
            else:
                music_url = data.get("music")
                if music_url:
                    sent_msg = await callback_query.message.answer_audio(music_url, caption="✅ অডিও সফলভাবে ডাউনলোড হয়েছে!")
                else:
                    await callback_query.message.answer("❌ এই ভিডিওর জন্য আলাদা অডিও খুঁজে পাওয়া যায়নি।")
                    return

            increment_limit(user_id)
            await callback_query.answer()

            feedback_keyboard = types.InlineKeyboardMarkup()
            feedback_keyboard.add(types.InlineKeyboardButton("⭐ মতামত দিন", url="https://t.me/Swygen_bd"))
            await callback_query.message.answer("আপনার অভিজ্ঞতা কেমন ছিল? নিচে ক্লিক করে জানান:", reply_markup=feedback_keyboard)

            await asyncio.sleep(3600)
            await sent_msg.delete()
        else:
            await callback_query.message.answer("❌ ডাউনলোডে সমস্যা হয়েছে, কিছুক্ষণ পরে চেষ্টা করুন।")
    except Exception as e:
        await callback_query.message.answer(f"⚠️ ত্রুটি ঘটেছে: {str(e)}")

if __name__ == '__main__':
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
