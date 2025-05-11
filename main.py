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
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# স্বাগতম মেসেজ
WELCOME_MSG = """স্বাগতম, {name}!
আপনি এই বট ব্যবহার করে TikTok ভিডিও Watermark ছাড়াই ডাউনলোড করতে পারবেন।
নিচের অপশন থেকে একটি বেছে নিন:"""

# Start কমান্ড
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Download Video", "Developer")
    await message.answer(WELCOME_MSG.format(name=message.from_user.first_name), reply_markup=keyboard)

# Download Video অপশন
@dp.message_handler(lambda message: message.text == "Download Video")
async def ask_for_link(message: types.Message):
    await message.reply("যে TikTok ভিডিওটা ডাউনলোড করতে চান, অনুগ্রহ করে তার লিংক দিন।")

# Developer অপশন
@dp.message_handler(lambda message: message.text == "Developer")
async def show_developer_info(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Admin Contact", url="https://t.me/Swygen_bot"))
    await message.reply("এই বটটি তৈরি করেছেন Swygen Official।\nDeveloper এর সাথে যোগাযোগ করতে নিচের বাটনে ক্লিক করুন:", reply_markup=keyboard)

# TikTok ভিডিও ডাউনলোড
@dp.message_handler(lambda message: "tiktok.com" in message.text)
async def download_tiktok_video(message: types.Message):
    tiktok_url = message.text
    await message.reply("ডাউনলোড হচ্ছে, অনুগ্রহ করে অপেক্ষা করুন...")

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
            video_url = data["video"][0]  # no watermark video
            sent_msg = await message.reply_video(video_url)

            # Feedback বাটন
            feedback_keyboard = types.InlineKeyboardMarkup()
            feedback_keyboard.add(types.InlineKeyboardButton("Contact Admin", url="https://t.me/Swygen_bd"))
            await message.reply("সার্ভিসটা কেমন লেগেছে জানাতে ভুলবেন না:", reply_markup=feedback_keyboard)

            # ১ ঘন্টা পর ভিডিও ডিলিট
            await asyncio.sleep(3600)
            await sent_msg.delete()
        else:
            await message.reply("ভিডিও ডাউনলোডে সমস্যা হচ্ছে, অনুগ্রহ করে পরে চেষ্টা করুন।")
    except Exception as e:
        await message.reply(f"ত্রুটি ঘটেছে: {e}")

# Keep alive এবং বট চালু
if __name__ == '__main__':
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
