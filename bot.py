import asyncio
import websockets
import yt_dlp
import subprocess
from highrise import BaseBot, Highrise, User

# 🔑 Apne Highrise ka API Key aur Room ID dalna
API_KEY = "YOUR_HIGHRISE_API_KEY"
ROOM_ID = "YOUR_ROOM_ID"

# Queue system
music_queue = []

class RadioBot(BaseBot):
    async def on_chat(self, user: User, message: str) -> None:
        if message.startswith("!play "):
            url = message.split(" ", 1)[1]
            await self.send_whisper(user.id, f"🎶 Adding to queue: {url}")
            music_queue.append(url)
            if len(music_queue) == 1:
                await play_music(url)

        elif message == "!skip":
            if music_queue:
                await self.send_whisper(user.id, "⏭ Skipping current track...")
                await skip_track()
            else:
                await self.send_whisper(user.id, "❌ No music in queue.")

        elif message == "!queue":
            if music_queue:
                queue_list = "\n".join([f"{i+1}. {song}" for i, song in enumerate(music_queue)])
                await self.send_whisper(user.id, f"📜 Current Queue:\n{queue_list}")
            else:
                await self.send_whisper(user.id, "🎵 Queue is empty.")

# 🔊 Music playback using yt-dlp + ffmpeg
async def play_music(url):
    try:
        ydl_opts = {"format": "bestaudio", "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info["url"]

        process = subprocess.Popen(
            ["ffmpeg", "-i", audio_url, "-vn", "-f", "mp3", "pipe:1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )

        await asyncio.sleep(10)  # simulate playback
        process.kill()

        # Finish song → play next
        music_queue.pop(0)
        if music_queue:
            await play_music(music_queue[0])

    except Exception as e:
        print("Error in playback:", e)

async def skip_track():
    if music_queue:
        music_queue.pop(0)
        if music_queue:
            await play_music(music_queue[0])

# 🚀 Run bot
if __name__ == "__main__":
    bot = RadioBot()
    Highrise(bot).connect(API_KEY, ROOM_ID)
