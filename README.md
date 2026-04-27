# 🎬 YouTube Downloader Bot

A Telegram bot that downloads videos and audio from YouTube — with quality selection and MP3 export.

## ✨ Features

- 🎵 Download audio as MP3
- 📱 Video in 360p / 720p / 1080p
- 🎛 Inline buttons for format selection
- ⚡ Fast and lightweight — no database needed

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/youtube-downloader-bot.git
cd youtube-downloader-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

FFmpeg is required for video/audio processing.

| OS | Command |
|----|---------|
| Windows | Download from [ffmpeg.org](https://ffmpeg.org/download.html) |
| macOS | `brew install ffmpeg` |
| Linux | `sudo apt install ffmpeg` |

### 4. Create your `.env` file

```bash
cp .env.example .env
```

Open `.env` and paste your bot token:

```
BOT_TOKEN=your_token_here
```

> Get a token from [@BotFather](https://t.me/BotFather) on Telegram.

### 5. Run the bot

```bash
python main.py
```

## 🤖 How to Use

1. Send a YouTube link to the bot
2. Choose a format:
   - **🎵 MP3** — audio only
   - **📱 360p** — small file size
   - **💻 720p** — HD quality
   - **🖥 1080p** — full HD
3. The bot downloads and sends the file

## ⌨️ Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |

## 📁 Project Structure

```
youtube-downloader-bot/
├── main.py            # Entry point
├── requirements.txt   # Dependencies
├── .env               # Your bot token (not committed)
├── .env.example       # Token template
├── .gitignore
└── bot/
    ├── __init__.py
    ├── init.py        # Bot setup
    └── handlers.py    # Message & callback handlers
```

## 🛠 Tech Stack

| Library | Purpose |
|---------|---------|
| [aiogram 3](https://docs.aiogram.dev/) | Telegram Bot API |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | YouTube downloading |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | Environment variables |

## 📝 License

MIT — free to use and modify.
