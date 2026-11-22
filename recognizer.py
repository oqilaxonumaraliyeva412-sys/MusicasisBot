import os
import asyncio
from shazamio import Shazam
from config import settings

# FFmpeg yo'lini olish
try:
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_PATH = "ffmpeg"

shazam = Shazam()

def extract_audio_from_video_ffmpeg(video_path: str, output_audio_path: str) -> bool:
    """
    FFmpeg yordamida videodan ovoz (MP3) ajratib olish
    """
    cmd = f'"{FFMPEG_PATH}" -y -i "{video_path}" -vn -acodec libmp3lame -ar 44100 -ac 2 -ab 192k "{output_audio_path}" -loglevel quiet'
    ret = os.system(cmd)
    return ret == 0

async def recognize_music_from_file(file_path: str) -> dict:
    """
    ShazamIO orqali audio/video fayldan musiqani tanish (identify).
    """
    try:
        # Agar fayl video bo'lsa, ffmpeg orqali avval mp3 ga aylantirib olishimiz mumkin
        # Yoki to'g'ridan-to'g'ri shazamio ga uzatish
        out = await shazam.recognize(file_path)
        track = out.get('track')
        if not track:
            return None
        
        title = track.get('title', '')
        subtitle = track.get('subtitle', '') # ijrochi
        
        return {
            'title': title,
            'artist': subtitle,
            'query': f"{subtitle} - {title}".strip(" -")
        }
    except Exception as e:
        print(f"Shazam xatosi: {e}")
        return None

