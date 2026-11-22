import os
import re
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import CommandStart, Command
from aiogram.types import FSInputFile, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from config import settings
from keyboards import get_audio_keyboard, get_search_results_keyboard
from downloader import download_audio_from_url, search_youtube, search_artist_songs
from recognizer import recognize_music_from_file

# Windows muhitida SSL sertifikat xatolarini chetlab o'tish uchun maxsus sessiya
session = AiohttpSession()
session._connector_type = aiohttp.TCPConnector
session._connector_init = dict(ssl=False)

# Bot va Dispetcherni ishga tushirish
bot = Bot(token=settings.BOT_TOKEN, session=session)
dp = Dispatcher()

# URL tekshirish uchun Regex
URL_REGEX = r'(https?://(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?://[^\s]+)'

# Qo'llab-quvvatlanadigan asosiy domenlar
SUPPORTED_DOMAINS = [
    'youtube.com', 'youtu.be', 'instagram.com', 'tiktok.com',
    'soundcloud.com', 'spotify.com', 'facebook.com', 'fb.watch', 'pin.it', 'pinterest.com'
]


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """
    /start buyrug'i uchun handler. Foydalanuvchiga bot imkoniyatlarini tushuntiradi.
    """
    text = (
        f"Assalomu alaykum, <b>{message.from_user.first_name}</b>! 🎶\n\n"
        "Men <b>Musiqa Botiman</b>. Quyidagi imkoniyatlarim mavjud:\n\n"
        "1️⃣ <b>Qo‘shiq nomi</b>ni yozing — musiqani topib beraman.\n"
        "2️⃣ <b>Qo‘shiqchi ismi</b>ni yozing — uning barcha sara qo‘shiqlarini chiqarib beraman.\n"
        "3️⃣ <b>Havola (link)</b> yuboring (YouTube, Instagram, TikTok, SoundCloud va h.k.) — audiosini yuklab beraman.\n"
        "4️⃣ <b>Video yoki video-xabar (dumaloq video)</b> tashlang — musiqasini <i>Shazam</i> qilib topib beraman!\n\n"
        "Menga qo‘shiq nomi, ijrochi yoki havola yuboring!"
    )
    await message.answer(text, parse_mode="HTML")


@dp.message(F.video | F.video_note)
async def handle_video_shazam(message: types.Message):
    """
    3. Video yoki dumaloq video (video note) orqali musiqani aniqlash (Shazam funksiyasi)
    """
    status_msg = await message.reply("🔍 Videodagi musiqa aniqlanmoqda (Shazam)... Iltimos, kuting.")
    video_item = message.video or message.video_note
    
    # Fayl hajmi tekshiruvi (Telegram bot API 20MB gacha fayllarni bot yuklab olishiga ruxsat beradi)
    if video_item.file_size and video_item.file_size > 20 * 1024 * 1024:
        await status_msg.edit_text("⚠️ Video hajmi juda katta (20MB dan oshmasligi kerak).")
        return

    file_id = video_item.file_id
    temp_video_path = os.path.join(settings.DOWNLOAD_DIR, f"video_{file_id}.mp4")

    try:
        # Faylni yuklab olamiz
        file_info = await bot.get_file(file_id)
        await bot.download_file(file_info.file_path, temp_video_path)

        # Musiqani aniqlaymiz
        match_info = await recognize_music_from_file(temp_video_path)
        if not match_info:
            await status_msg.edit_text("😔 Afsuski, ushbu videodagi musiqa topilmadi.")
            return

        query = match_info['query']
        await status_msg.edit_text(f"✅ Musiqa topildi: <b>{query}</b>\nYuklab olinmoqda...", parse_mode="HTML")

        # Topilgan nom bo'yicha YouTube'dan MP3 yuklab olamiz
        audio_data = await download_audio_from_url(f"ytsearch1:{query}")
        audio_file = FSInputFile(audio_data['file_path'])
        
        reply_kb = get_audio_keyboard(
            title=audio_data.get('title', match_info['title']),
            performer=audio_data.get('artist', match_info['artist']),
            download_url=audio_data.get('webpage_url')
        )

        caption = f"🎵 <b>{match_info['artist']} - {match_info['title']}</b>\n\n🤖 @{(await bot.me()).username}"
        await message.reply_audio(
            audio=audio_file,
            title=match_info['title'],
            performer=match_info['artist'],
            caption=caption,
            parse_mode="HTML",
            reply_markup=reply_kb
        )
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ Xatolik yuz berdi: {str(e)}")
    finally:
        # Vaqtinchalik videoni o'chirish
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)


@dp.message(F.text)
async def handle_text_message(message: types.Message):
    """
    Matnli xabarlarni qayta ishlash:
    - Havolalar (YouTube, Instagram, TikTok, va h.k.)
    - Qo'shiqchi yoki qo'shiq nomi bo'yicha qidiruv
    """
    text = message.text.strip()
    
    # Buyruqlarni e'tiborsiz qoldiramiz
    if text.startswith('/'):
        return

    # 1. Havolani tekshiramiz
    urls = re.findall(URL_REGEX, text)
    if urls:
        url = urls[0]
        # Tekshirish: taniqli musiqa/video platformasi yoki qo'llab-quvvatlanadimi?
        is_supported = any(domain in url.lower() for domain in SUPPORTED_DOMAINS)
        
        status_msg = await message.reply("⏳ Havola tekshirilmoqda va audio yuklanmoqda...")
        try:
            audio_data = await download_audio_from_url(url)
            audio_file = FSInputFile(audio_data['file_path'])

            reply_kb = get_audio_keyboard(
                title=audio_data.get('title'),
                performer=audio_data.get('artist'),
                download_url=audio_data.get('webpage_url')
            )

            caption = f"🎵 <b>{audio_data.get('title')}</b>\n\n🤖 @{(await bot.me()).username}"
            await message.reply_audio(
                audio=audio_file,
                title=audio_data.get('title'),
                performer=audio_data.get('artist'),
                duration=audio_data.get('duration'),
                caption=caption,
                parse_mode="HTML",
                reply_markup=reply_kb
            )
            await status_msg.delete()

            # Yuklangan faylni tozalash
            if os.path.exists(audio_data['file_path']):
                os.remove(audio_data['file_path'])
            return
        except Exception:
            # Agar yuklab bo'lmasa yoki musiqa bo'lmagan sayt bo'lsa
            await status_msg.edit_text("❌ Bu musiqaning ssilkasi emas yoki audioni ajratib olish imkoni bo‘lmadi.")
            return

    # 2. Qo'shiq yoki Ijrochi nomi bo'yicha qidiruv
    status_msg = await message.reply("🔎 Qidirilmoqda...")
    try:
        # Eng avval 6 ta mos natijani chiqaramiz (bu ham qo'shiq, ham ijrochining qo'shiqlari uchun qulay)
        results = await search_youtube(text, max_results=6)
        if not results:
            await status_msg.edit_text("😔 Hech qanday musiqa topilmadi. Qayta urinib ko‘ring.")
            return

        kb = get_search_results_keyboard(results, prefix="ytplay")
        bot_user = await bot.me()
        response_text = (
            f"🎶 <b>'{text}'</b> bo‘yicha topilgan natijalar:\n\n"
            "Kerakli musiqani yuklab olish uchun quyidagi tugmalardan birini bosing:"
        )
        await status_msg.edit_text(response_text, reply_markup=kb, parse_mode="HTML")
    except Exception as e:
        await status_msg.edit_text(f"❌ Qidirishda xatolik yuz berdi: {str(e)}")


@dp.callback_query(F.data.startswith("ytplay:"))
async def handle_play_callback(callback: CallbackQuery):
    """
    Foydalanuvchi qidiruv ro'yxatidan biror musiqani tanlaganda ishga tushadi
    """
    video_id = callback.data.split(":")[1]
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    await callback.answer("Yuklab olinmoqda...")
    status_msg = await callback.message.reply("⏳ Musiqa yuklanmoqda...")

    try:
        audio_data = await download_audio_from_url(video_url)
        audio_file = FSInputFile(audio_data['file_path'])

        reply_kb = get_audio_keyboard(
            title=audio_data.get('title'),
            performer=audio_data.get('artist'),
            download_url=audio_data.get('webpage_url')
        )

        caption = f"🎵 <b>{audio_data.get('title')}</b>\n👤 <i>{audio_data.get('artist')}</i>\n\n🤖 @{(await bot.me()).username}"
        await callback.message.reply_audio(
            audio=audio_file,
            title=audio_data.get('title'),
            performer=audio_data.get('artist'),
            duration=audio_data.get('duration'),
            caption=caption,
            parse_mode="HTML",
            reply_markup=reply_kb
        )
        await status_msg.delete()

        # Faylni xotiradan tozalash
        if os.path.exists(audio_data['file_path']):
            os.remove(audio_data['file_path'])

    except Exception as e:
        await status_msg.edit_text(f"❌ Musiqani yuklab olishda xatolik: {str(e)}")


@dp.inline_query()
async def inline_share_handler(inline_query: InlineQuery):
    """
    Do'stlarga jo'natish (switch_inline_query) orqali boshqa chatlarda qidirish va ulashish
    """
    query = inline_query.query.strip()
    if not query:
        return

    results = []
    try:
        search_data = await search_youtube(query, max_results=5)
        for item in search_data:
            article = InlineQueryResultArticle(
                id=item['id'],
                title=item['title'],
                input_message_content=InputTextMessageContent(
                    message_text=f"🎶 Tinglang: <b>{item['title']}</b>\nhttps://www.youtube.com/watch?v={item['id']}",
                    parse_mode="HTML"
                ),
                description=f"Davomiyligi: {item.get('duration', 0)} soniya"
            )
            results.append(article)
        
        await inline_query.answer(results, cache_time=300)
    except Exception:
        pass


async def main():
    print("Bot ishga tushmoqda...")
    # Eskirgan yangilanishlarni tashlab yuborish
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot to'xtatildi.")

