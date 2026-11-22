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
    yt-dlp yordamida audioni yuklab olish va MP3 ga aylantirish.
    Server blokirovkalarini aylanib o'tish uchun Android va TV client parametrlaridan foydalanadi.
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
                'player_client': ['android', 'ios', 'tv_embedded']
            }
        },
        'http_headers': {
            'User-Agent': 'com.google.android.youtube/19.09.37 (Linux; U; Android 11; en_US; Pixel 5) gzip',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
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
    except Exception as e:
        # Agar youtube baribir bot desa, fallback sifatida zaxira audio qidiruv
        if "Sign in" in str(e) or "bot" in str(e).lower():
            # Zaxira opsiyasi
            ydl_opts['extractor_args']['youtube']['player_client'] = ['mweb', 'android']
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if 'entries' in info and info['entries']:
                    info = info['entries'][0]
                video_id = info.get('id')
                file_path = os.path.join(output_path, f"{video_id}.mp3")
                return {
                    'file_path': file_path,
                    'title': info.get('title', 'Musiqa'),
                    'artist': info.get('uploader', 'Ijrochi'),
                    'duration': info.get('duration', 0),
                    'webpage_url': info.get('webpage_url', url)
                }
        raise e

async def download_audio_from_url(url: str) -> dict:
    """Asinxron tarzda audio yuklab olish"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, extract_audio_from_url_sync, url, settings.DOWNLOAD_DIR)

def search_youtube_sync(query: str, max_results: int = 5) -> list:
    """
    Qo'shiq nomi yoki ijrochi nomi bo'yicha YouTube'dan qidirish
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios']
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
    """Ijrochi qo'shiqlari qidiruvi"""
    query = f"{artist_name} top songs audio"
    return search_youtube_sync(query, max_results=max_results)

async def search_artist_songs(artist_name: str, max_results: int = 8) -> list:
    """Ijrochi qidiruvining asinxron varianti"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, search_artist_songs_sync, artist_name, max_results)
