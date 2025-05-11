import logging
from aiogram import Bot, Dispatcher, executor, types
import requests
import asyncio
from keep_alive import keep_alive  # Keep-alive system

API_TOKEN = '7310009275:AAGsgHRrHfclSgGE4wLA8yWz9RWAFEmufP4'
RAPIDAPI_KEY = 'b4d6936178mshafaf4aec9942f2ap16237ejsn4249014c201e'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_name = message.from_user.full_name
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Download Video", "Developer")

    welcome_text = f"""স্বাগতম, {user_name}!

এই বটটির মাধ্যমে আপনি TikTok ভিডিও Watermark ছাড়াই সহজেই ডাউনলোড করতে পারবেন।

দয়া করে নিচের অপশন থেকে একটি বেছে নিন:"""

    await message.answer(welcome_text, reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "Download Video")
async def ask_for_link(message: types.Message):
    await message.reply("যে TikTok ভিডিওটা ডাউনলোড করতে চান, অনুগ্রহ করে তার লিংক দিন")

@dp.message_handler(lambda message: message.text == "Developer")
async def show_developer_info(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Admin Contact", url="https://t.me/Swygen_bot"))
    await message.reply(
        "এই বটটি তৈরি করেছেন Swygen Official।\nDeveloper এর সাথে যোগাযোগ করতে নিচের বাটনে ক্লিক করুন:",
        reply_markup=keyboard
    )

@dp.message_handler(lambda message: message.text.startswith("https://www.tiktok.com"))
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
            video_url = data["video"][0]
            sent_msg = await message.reply_video(video_url)

            feedback_keyboard = types.InlineKeyboardMarkup()
            feedback_keyboard.add(types.InlineKeyboardButton("Contact Admin", url="https://t.me/Swygen_bd"))
            await message.reply("সার্ভিসটা কেমন লেগেছে জানাতে ভুলবেন না:", reply_markup=feedback_keyboard)

            await asyncio.sleep(3600)
            await sent_msg.delete()
        else:
            await message.reply("ভিডিও ডাউনলোডে সমস্যা হচ্ছে, অনুগ্রহ করে পরে চেষ্টা করুন।")
    except Exception as e:
        await message.reply(f"ত্রুটি ঘটেছে: {e}")

if __name__ == '__main__':
    keep_alive()  # Keep alive system চালু
    executor.start_polling(dp, skip_updates=True)
