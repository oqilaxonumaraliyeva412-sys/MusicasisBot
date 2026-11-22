import os
import uuid
import asyncio
import yt_dlp
from config import settings

# FFmpeg yo'lini aniqlash
try:
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_PATH = "ffmpeg"

def extract_audio_from_url_sync(url: str, output_path: str) -> dict:
    """
    yt-dlp yordamida berilgan URL yoki qidiruvdan musiqani yuklab olish va MP3 ga aylantirish.
    YouTube bot blokirovkasini (Sign in to confirm you're not a bot) aylanib o'tish uchun
    Android/iOS mijozlaridan foydalanadi.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/%(id)s.%(ext)s',
        'ffmpeg_location': FFMPEG_PATH,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # Agar qidiruv bo'lsa entries ichida keladi
        if 'entries' in info and info['entries']:
            info = info['entries'][0]
        
        video_id = info.get('id')
        title = info.get('title', 'Nomaʼlum musiqa')
        artist = info.get('uploader') or info.get('artist') or info.get('creator') or 'Nomaʼlum ijrochi'
        duration = info.get('duration', 0)
        file_path = os.path.join(output_path, f"{video_id}.mp3")

        return {
            'file_path': file_path,
            'title': title,
            'artist': artist,
            'duration': duration,
            'webpage_url': info.get('webpage_url', url)
        }

async def download_audio_from_url(url: str) -> dict:
    """Asinxron tarzda audio yuklab olish"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, extract_audio_from_url_sync, url, settings.DOWNLOAD_DIR)

def search_youtube_sync(query: str, max_results: int = 5) -> list:
    """
    Qo'shiq nomi yoki ijrochi nomi bo'yicha YouTube'dan qidirish (yuklamasdan, ma'lumot olish)
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web']
            }
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        search_query = f"ytsearch{max_results}:{query}"
        info = ydl.extract_info(search_query, download=False)
        results = []
        if 'entries' in info and info['entries']:
            for entry in info['entries']:
                if entry:
                    results.append({
                        'id': entry.get('id'),
                        'title': entry.get('title', 'Nomaʼlum nom'),
                        'duration': entry.get('duration', 0),
                        'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                    })
        return results

async def search_youtube(query: str, max_results: int = 5) -> list:
    """Asinxron qidiruv"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, search_youtube_sync, query, max_results)

def search_artist_songs_sync(artist_name: str, max_results: int = 8) -> list:
    """
    Ijrochi ismi bo'yicha eng mashhur qo'shiqlarini topish
    """
    query = f"{artist_name} top songs audio"
    return search_youtube_sync(query, max_results=max_results)

async def search_artist_songs(artist_name: str, max_results: int = 8) -> list:
    """Ijrochi qidiruvining asinxron varianti"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, search_artist_songs_sync, artist_name, max_results)

