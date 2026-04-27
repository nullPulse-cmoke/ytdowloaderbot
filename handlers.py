import os
import yt_dlp
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

router = Router()
user_urls = {}  



@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Я скачиваю видео и музыку с YouTube.\n\n"
        "Просто отправь мне ссылку на видео 🎬"
    )



@router.message(F.text.startswith("http"))
async def handle_url(message: Message):
    url = message.text.strip()
    user_urls[message.from_user.id] = url

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎵 MP3 (аудио)", callback_data="audio"),
        ],
        [
            InlineKeyboardButton(text="📱 360p", callback_data="360"),
            InlineKeyboardButton(text="💻 720p", callback_data="720"),
            InlineKeyboardButton(text="🖥 1080p", callback_data="1080"),
        ]
    ])

    await message.answer("Что скачать?", reply_markup=keyboard)



@router.callback_query(F.data.in_({"audio", "360", "720", "1080"}))
async def handle_choice(callback: CallbackQuery):
    user_id = callback.from_user.id
    url = user_urls.get(user_id)

    if not url:
        await callback.message.answer("❌ Сначала отправь ссылку на видео!")
        await callback.answer()
        return

    choice = callback.data
    await callback.message.edit_text("⏳ Скачиваю, подожди...")

    try:
        if choice == "audio":
            file_path = await download(url, mode="audio")
            await callback.message.answer_audio(
                audio=open(file_path, "rb"),
                caption="🎵 Готово!"
            )
        else:
            file_path = await download(url, mode="video", quality=choice)
            await callback.message.answer_video(
                video=open(file_path, "rb"),
                caption=f"🎬 Готово! ({choice}p)"
            )

        os.remove(file_path)

    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {e}")

    await callback.answer()


async def download(url: str, mode: str, quality: str = "720") -> str:
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)

    if mode == "audio":
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{output_dir}/%(title)s.%(ext)s",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "quiet": True,
        }
    else:
        height = quality
        ydl_opts = {
            "format": f"bestvideo[height<={height}]+bestaudio/best[height<={height}]",
            "outtmpl": f"{output_dir}/%(title)s.%(ext)s",
            "merge_output_format": "mp4",
            "quiet": True,
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

        if mode == "audio":
            filename = os.path.splitext(filename)[0] + ".mp3"

    return filename
