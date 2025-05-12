import logging
from aiogram import Bot, Dispatcher, executor, types
import requests
import asyncio
from keep_alive import keep_alive  # বট চালু রাখার জন্য

# Bot Token & RapidAPI Token
API_TOKEN = '7310009275:AAGsgHRrHfclSgGE4wLA8yWz9RWAFEmufP4'
RAPIDAPI_KEY = 'b4d6936178mshafaf4aec9942f2ap16237ejsn4249014c201e'

# লগিং শুরু
logging.basicConfig(level=logging.INFO)

# Bot সেটআপ
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# ইউজার লিংক রাখার জন্য
user_links = {}

# স্বাগতম মেসেজ
WELCOME_MSG = """
<b>স্বাগতম, {name}!</b>  
✨ এই বটটির মাধ্যমে আপনি সহজেই TikTok ভিডিও <b>Watermark ছাড়াই</b> ডাউনলোড করতে পারবেন!

<b>বৈশিষ্ট্যসমূহ:</b>
🎥 ভিডিও ডাউনলোড (HD, No Watermark)  
🎵 অডিও এক্সট্রাকশন  
⚡ দ্রুত ও নির্ভরযোগ্য সার্ভার  

<b>নিচে থেকে একটি অপশন বেছে নিন:</b>
"""

# Start কমান্ড
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("🎬 Download Video", "👨‍💻 Developer")
    await message.answer(WELCOME_MSG.format(name=message.from_user.first_name), reply_markup=keyboard)

# Download Video অপশন
@dp.message_handler(lambda message: message.text == "🎬 Download Video")
async def ask_for_link(message: types.Message):
    await message.reply("🔗 অনুগ্রহ করে সেই TikTok ভিডিওটির লিংক দিন যেটি আপনি ডাউনলোড করতে চান:")

# Developer অপশন
@dp.message_handler(lambda message: message.text == "👨‍💻 Developer")
async def show_developer_info(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("📞 Admin Contact", url="https://t.me/Swygen_bot"))
    await message.reply("🛠️ <b>এই বটটি তৈরি করেছেন:</b> <i>Swygen Official</i>\n\nযোগাযোগ করতে নিচের বাটনে ক্লিক করুন:", reply_markup=keyboard)

# TikTok লিংক হ্যান্ডলার
@dp.message_handler(lambda message: "tiktok.com" in message.text)
async def ask_format(message: types.Message):
    user_links[message.from_user.id] = message.text
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("🎥 Download Video", callback_data="download_video"),
        types.InlineKeyboardButton("🎵 Download Audio", callback_data="download_audio")
    )
    await message.reply("আপনি কোন ফরম্যাটে ডাউনলোড করতে চান?", reply_markup=keyboard)

# ডাউনলোড অপশন প্রসেস
@dp.callback_query_handler(lambda c: c.data in ["download_video", "download_audio"])
async def process_download_option(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    tiktok_url = user_links.get(user_id)

    if not tiktok_url:
        await callback_query.message.answer("❗ লিংক পাওয়া যায়নি, অনুগ্রহ করে আবার চেষ্টা করুন।")
        return

    await callback_query.message.answer("⏳ ডাউনলোড প্রক্রিয়া শুরু হয়েছে... অনুগ্রহ করে অপেক্ষা করুন...")

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
                video_url = data["video"][0]
                sent_msg = await callback_query.message.answer_video(video_url, caption="✅ আপনার ভিডিও প্রস্তুত!")
            else:
                music_url = data["music"]
                sent_msg = await callback_query.message.answer_audio(music_url, caption="✅ অডিও প্রস্তুত!")

            await callback_query.answer()

            feedback_keyboard = types.InlineKeyboardMarkup()
            feedback_keyboard.add(types.InlineKeyboardButton("💬 Contact Admin", url="https://t.me/Swygen_bd"))
            await callback_query.message.answer("⭐ <b>সার্ভিসটি কেমন লাগলো?</b> আপনার মতামত জানাতে ভুলবেন না:", reply_markup=feedback_keyboard)

            await asyncio.sleep(3600)
            await sent_msg.delete()
        else:
            await callback_query.message.answer("⚠️ ভিডিও ডাউনলোডে সমস্যা হচ্ছে, পরে আবার চেষ্টা করুন।")
    except Exception as e:
        await callback_query.message.answer(f"❌ <b>ত্রুটি ঘটেছে:</b> {e}")

# Keep alive এবং বট চালু
if __name__ == '__main__':
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
