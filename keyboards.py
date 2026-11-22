from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import urllib.parse

def get_audio_keyboard(title: str, performer: str, download_url: str = None) -> InlineKeyboardMarkup:
    """
    Har bir yuborilgan musiqa ostida chiqadigan inline tugmalar:
    1. Yuklab olish
    2. Do'stlarga jo'natish (Telegram ichida inline ulashish)
    3. Boshqa ilovalarga jo'natish (Web share / havola)
    """
    query_text = f"{performer} - {title}".strip(" -")
    # Telegram inline qidiruv orqali ulashish
    share_query = query_text

    buttons = []
    
    # 1-qator: Do'stlarga jo'natish (Telegram chatlariga ulashish)
    row1 = [
        InlineKeyboardButton(
            text="📤 Do‘stlarga jo‘natish",
            switch_inline_query=share_query
        )
    ]
    buttons.append(row1)

    # 2-qator: Boshqa ilovalarga / tashqi ulashish
    # Telegram orqali tashqi ilovalarga link share qilish yoki Google orqali qidirish
    encoded_text = urllib.parse.quote(f"Tinglang: {query_text}")
    share_url = f"https://t.me/share/url?url={urllib.parse.quote('https://t.me/')}&text={encoded_text}"
    if download_url and download_url.startswith("http"):
        share_url = f"https://t.me/share/url?url={urllib.parse.quote(download_url)}&text={encoded_text}"

    row2 = [
        InlineKeyboardButton(
            text="🌐 Boshqa ilovalarga ulashish",
            url=share_url
        )
    ]
    buttons.append(row2)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_search_results_keyboard(results: list, prefix: str = "ytplay") -> InlineKeyboardMarkup:
    """
    Qidiruv yoki ijrochi qo'shiqlari ro'yxati uchun inline tugmalar
    results: [{'id': 'video_id', 'title': 'Qo'shiq nomi', 'duration': '3:20'}, ...]
    """
    buttons = []
    for idx, item in enumerate(results, 1):
        btn_text = f"{idx}. {item['title'][:40]}"
        callback_data = f"{prefix}:{item['id']}"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=callback_data)])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

