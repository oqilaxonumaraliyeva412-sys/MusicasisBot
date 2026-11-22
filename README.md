# 🎵 Ko‘p funksiyali Telegram Musiqa Boti (Aiogram 3.x)

Ushbu bot Python va `aiogram 3.x` kutubxonasida yaratilgan bo‘lib, quyidagi barcha imkoniyatlarni o‘z ichiga oladi:
1. **Qo‘shiq nomi bo‘yicha qidiruv** (topib, MP3 qilib yuboradi).
2. **Havola (ssilka) orqali musiqa yuklash** (YouTube, Instagram, TikTok, SoundCloud va h.k. platformalardan audioni MP3 qilib ajratadi; noto‘g‘ri havolalarda ogohlantirish beradi).
3. **Video orqali musiqani aniqlash (Shazam)** (Video yoki dumaloq video xabar yuborilsa, Shazam orqali tanib, MP3 formatini topib yuboradi).
4. **Qo‘shiqchi ismi bo‘yicha musiqalar** (Ijrochining sara qo‘shiqlari ro‘yxatini chiqaradi va tanlanganini yuklaydi).
5. **Inline tugmalar**: "📤 Do‘stlarga jo‘natish" (`switch_inline_query`), "🌐 Boshqa ilovalarga ulashish" va boshqalar.

---

## 🛠 O‘rnatish va Ishga tushirish bo‘yicha qo‘llanma

### 1-qadam: FFmpeg o‘rnatish (Juda muhim!)
Audioni MP3 ga aylantirish va videodan ovoz ajratish uchun kompyuteringizda yoki serveringizda **FFmpeg** dasturi o‘rnatilgan bo‘lishi shart:
- **Windows uchun:** [ffmpeg.org/download.html](https://ffmpeg.org/download.html) saytidan yuklab oling yoki `winget install Gyan.FFmpeg` buyrug‘ini bajaring. Keyin uni tizim `PATH`iga qo‘shing.
- **Ubuntu/Debian Linux uchun:**
  ```bash
  sudo apt update && sudo apt install -y ffmpeg
  ```

### 2-qadam: Kerakli kutubxonalarni o‘rnatish
Terminal yoki konsolda loyiha papkasiga kiring va quyidagi buyruqni bering:
```bash
pip install -r requirements.txt
```

### 3-qadam: `BOT_TOKEN` ni kiritish
1. Telegramda [@BotFather](https://t.me/BotFather) botiga kiring va `/newbot` buyrug‘i orqali yangi bot ochib token oling.
2. Bot inline rejimida ham ishlashi (do‘stlarga jo‘natish tugmasi uchun) uchun `@BotFather`da quyidagilarni sozlang:
   - `/setinline` -> botingizni tanlang -> biror matn yozing (masalan, `Musiqa qidirish...`).
3. Loyiha papkasidagi `.env.example` faylidan nusxa olib, yangi `.env` fayl yarating (yoki mavjud `.env` faylini oching).
4. `.env` fayliga tokeningizni kiriting:
   ```env
   BOT_TOKEN=1234567890:ABCdefGhIJKlmNoPQRstuVWXyz
   ```

### 4-qadam: Botni ishga tushirish
Quyidagi buyruq orqali botni ishga tushiring:
```bash
python main.py
```

---

## 📂 Loyiha tuzilishi
- [main.py](file:///c:/Users/MADI/Desktop/TWO%20creating%20bot/main.py) — Barcha buyruqlar, matn, video va inline query handlerlari.
- [downloader.py](file:///c:/Users/MADI/Desktop/TWO%20creating%20bot/downloader.py) — `yt-dlp` orqali audiolarni qidirish va yuklab olish moduli.
- [recognizer.py](file:///c:/Users/MADI/Desktop/TWO%20creating%20bot/recognizer.py) — `shazamio` orqali videolardan musiqani aniqlash.
- [keyboards.py](file:///c:/Users/MADI/Desktop/TWO%20creating%20bot/keyboards.py) — Musiqa ostidagi va qidiruv ro‘yxatidagi inline tugmalar.
- [config.py](file:///c:/Users/MADI/Desktop/TWO%20creating%20bot/config.py) — Sozlamalar va `.env` o‘quvchi modul.
- [requirements.txt](file:///c:/Users/MADI/Desktop/TWO%20creating%20bot/requirements.txt) — Kerakli kutubxonalar ro‘yxati.
- [.env.example](file:///c:/Users/MADI/Desktop/TWO%20creating%20bot/.env.example) — Muhit o‘zgaruvchilari namunasi.

# MusicasisBot
