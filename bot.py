import os
import subprocess
import asyncio
import websockets
import yt_dlp

QUEUE = []
CURRENT = None
ICECAST_URL = "icecast://source:hackme@localhost:8000/stream"

async def play_song(song_url):
    global CURRENT
    CURRENT = song_url

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'extract_flat': False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(song_url, download=False)
        audio_url = info['url']

    cmd = [
        "ffmpeg", "-re", "-i", audio_url,
        "-vn", "-c:a", "mp3", "-content_type", "audio/mpeg",
        "-f", "mp3", ICECAST_URL
    ]

    process = subprocess.Popen(cmd)
    process.wait()

async def handle_message(msg):
    global QUEUE, CURRENT

    if msg.startswith("!p "):
        query = msg[3:]
        print(f"Searching: {query}")

        ydl_opts = {'quiet': True, 'default_search': 'ytsearch1'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            url = info['entries'][0]['url']

        QUEUE.append(url)
        print(f"Added to queue: {url}")

        if CURRENT is None:
            await play_queue()

    elif msg == "!skip":
        print("Skipping song...")
        await skip_song()

    elif msg == "!stop":
        print("Stopping playback...")
        QUEUE.clear()
        CURRENT = None
        os.system("pkill ffmpeg")

async def play_queue():
    global QUEUE
    while QUEUE:
        url = QUEUE.pop(0)
        await play_song(url)

async def skip_song():
    os.system("pkill ffmpeg")

async def main():
    while True:
        msg = input("Command: ")
        await handle_message(msg)

if __name__ == "__main__":
    asyncio.run(main())