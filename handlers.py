import asyncio
import os
import uuid
import yt_dlp
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup, Message

router = Router()

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB (Лимит стандартного Bot API)


class DownloadState(StatesGroup):
    url = State()


def _sync_download(url: str, mode: str, quality: str, out_prefix: str) -> str:
    """Синхронная функция скачивания для запуска в отдельном потоке."""
    output_template = f"downloads/{out_prefix}_%(title).100s.%(ext)s"

    if mode == "audio":
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "quiet": True,
            "no_warnings": True,
        }
    else:
        ydl_opts = {
            "format": f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality}][ext=mp4]/best",
            "outtmpl": output_template,
            "merge_output_format": "mp4",
            "quiet": True,
            "no_warnings": True,
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

        if mode == "audio":
            filename = os.path.splitext(filename)[0] + ".mp3"

    return filename


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Отправь ссылку на YouTube видео, чтобы скачать его в MP3 или MP4."
    )


@router.message(F.text.regexp(r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"))
async def handle_url(message: Message, state: FSMContext):
    url = message.text.strip()
    await state.update_data(url=url)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎵 MP3 (Аудио)", callback_data="dl:audio:0")],
            [
                InlineKeyboardButton(text="📱 360p", callback_data="dl:video:360"),
                InlineKeyboardButton(text="💻 720p", callback_data="dl:video:720"),
                InlineKeyboardButton(text="🖥 1080p", callback_data="dl:video:1080"),
            ],
        ]
    )

    await message.answer("Выберите формат:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("dl:"))
async def handle_download(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    url = data.get("url")

    if not url:
        await callback.answer("❌ Ссылка устарела. Отправьте ее заново.", show_alert=True)
        return

    _, mode, quality = callback.data.split(":")
    await callback.message.edit_text("⏳ Скачиваю и обрабатываю файл...")

    os.makedirs("downloads", exist_ok=True)
    task_id = uuid.uuid4().hex[:8]
    file_path = None

    try:
        # Запуск тяжелого процесса в фоновом пуле потоков
        file_path = await asyncio.to_thread(_sync_download, url, mode, quality, task_id)

        if not os.path.exists(file_path):
            raise FileNotFoundError("Файл не был создан.")

        if os.path.getsize(file_path) > MAX_FILE_SIZE:
            await callback.message.edit_text(
                "❌ Размер файла превышает 50 МБ (ограничение Telegram Bot API)."
            )
            return

        input_file = FSInputFile(file_path)

        if mode == "audio":
            await callback.message.answer_audio(audio=input_file, caption="🎵 Аудио готово")
        else:
            await callback.message.answer_video(
                video=input_file, caption=f"🎬 Видео готово ({quality}p)"
            )

        await callback.message.delete()

    except Exception as err:
        await callback.message.edit_text(f"❌ Не удалось обработать: {err}")

    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        await callback.answer()