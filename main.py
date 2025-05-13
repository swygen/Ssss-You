import logging
from aiogram import Bot, Dispatcher, executor, types
import requests
import asyncio
from keep_alive import keep_alive  # আপনার হোস্টিং সার্ভিসে keep_alive ব্যবহার করলে

# Bot Token & API Key
API_TOKEN = '7310009275:AAGsgHRrHfclSgGE4wLA8yWz9RWAFEmufP4'
RAPIDAPI_KEY = 'b4d6936178mshafaf4aec9942f2ap16237ejsn4249014c201e'

# লগিং চালু
logging.basicConfig(level=logging.INFO)

# বট সেটআপ
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ইউজার লিংক ট্র্যাকিং
user_links = {}
audio_links = {}

WELCOME_MSG = """👋 স্বাগতম, {name}!

এই বট ব্যবহার করে আপনি সহজেই TikTok ভিডিও **Watermark ছাড়া** ডাউনলোড করতে পারবেন।

✨ ফিচার:
- ✅ ভিডিও ডাউনলোড
- ✅ অডিও ডাউনলোড (যদি উপলব্ধ থাকে)

নিচে থেকে একটি অপশন বেছে নিন:"""

# চ্যানেল সদস্যতা যাচাই ফাংশন
async def is_member(user_id):
    try:
        chat_member = await bot.get_chat_member(chat_id='@swygenbd', user_id=user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except:
        return False

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if not await is_member(message.from_user.id):
        join_button = types.InlineKeyboardMarkup()
        join_button.add(types.InlineKeyboardButton("✅ এখন জয়েন করুন", url="https://t.me/swygenbd"))
        await message.answer("❗️এই বটটি ব্যবহারের জন্য আপনাকে আমাদের চ্যানেলে জয়েন করতে হবে।", reply_markup=join_button)
        return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("▶️ Download Video", "👨‍💻 Developer")
    await message.answer(WELCOME_MSG.format(name=message.from_user.first_name), reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "▶️ Download Video")
async def ask_for_link(message: types.Message):
    await message.reply("🔗 অনুগ্রহ করে TikTok ভিডিওর লিংক পাঠান।")

@dp.message_handler(lambda message: message.text == "👨‍💻 Developer")
async def show_developer_info(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("📩 Admin Contact", url="https://t.me/Swygen_bot"))
    await message.reply("এই বটটি তৈরি করেছেন Swygen Official।", reply_markup=keyboard)

@dp.message_handler(lambda message: "tiktok.com" in message.text)
async def ask_format(message: types.Message):
    user_links[message.from_user.id] = message.text
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("🎬 Download Video", callback_data="download_video"),
        types.InlineKeyboardButton("🎵 Download Audio", callback_data="download_audio")
    )
    await message.reply("আপনি কোন ফরম্যাটে ডাউনলোড করতে চান?", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data in ["download_video", "download_audio"])
async def process_download_option(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
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
            sent_msg = None

            if callback_query.data == "download_video":
                video_url = data.get("video", [None])[0]
                if video_url:
                    sent_msg = await callback_query.message.answer_video(video_url, caption="✅ ভিডিও সফলভাবে ডাউনলোড হয়েছে!")
                else:
                    await callback_query.message.answer("❌ ভিডিও লিংক খুঁজে পাওয়া যায়নি।")
                    return

            elif callback_query.data == "download_audio":
                music_url = data.get("music")
                if music_url:
                    if isinstance(music_url, list):
                        music_url = music_url[0]

                    # অডিও লিংক সেভ করা
                    audio_links[user_id] = music_url

                    download_button = types.InlineKeyboardMarkup()
                    download_button.add(types.InlineKeyboardButton("⬇️ অডিও ডাউনলোড করুন", callback_data="send_audio_file"))
                    await callback_query.message.answer("✅ অডিও প্রস্তুত! নিচে ক্লিক করে ডাউনলোড করুন:", reply_markup=download_button)
                else:
                    await callback_query.message.answer("❌ এই ভিডিওর জন্য আলাদা অডিও খুঁজে পাওয়া যায়নি।")
                    return

            await callback_query.answer()

            feedback_keyboard = types.InlineKeyboardMarkup()
            feedback_keyboard.add(types.InlineKeyboardButton("⭐ মতামত দিন", url="https://t.me/Swygen_bd"))
            await callback_query.message.answer("আপনার অভিজ্ঞতা কেমন ছিল? নিচে ক্লিক করে জানান:", reply_markup=feedback_keyboard)

            if sent_msg:
                await asyncio.sleep(3600)
                try:
                    await sent_msg.delete()
                except:
                    pass
        else:
            await callback_query.message.answer("❌ ডাউনলোডে সমস্যা হয়েছে, কিছুক্ষণ পরে চেষ্টা করুন।")
    except Exception as e:
        await callback_query.message.answer(f"⚠️ ত্রুটি ঘটেছে: {str(e)}")

# অডিও ফাইল পাঠানো
@dp.callback_query_handler(lambda c: c.data == "send_audio_file")
async def send_audio_file(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    music_url = audio_links.get(user_id)

    if music_url:
        try:
            await bot.send_audio(chat_id=user_id, audio=music_url, caption="✅ অডিও সফলভাবে পাঠানো হয়েছে!")
            await callback_query.answer()
        except Exception as e:
            await callback_query.message.answer(f"❌ অডিও পাঠানো যায়নি: {str(e)}")
    else:
        await callback_query.message.answer("❌ অডিও লিংক পাওয়া যায়নি।")

# বট চালু রাখার জন্য
if __name__ == '__main__':
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
