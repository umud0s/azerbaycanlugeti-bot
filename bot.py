import json
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

BASE = Path(__file__).resolve().parent
load_dotenv(BASE / ".env")

with open(BASE / "data.json", encoding="utf-8") as f:
    DATA = json.load(f)

WORDS = {k.casefold(): v for k, v in DATA["words"].items()}
SOURCE = DATA.get("source", "https://orfoqrafiya.azleks.az/")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Bir söz yazın. Düzgün yazılışı və izahı göndərəcəyəm."
    )


async def lookup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (update.message.text or "").strip()
    if not text:
        return

    item = WORDS.get(text.casefold())
    if not item:
        await update.message.reply_text("Bu söz bazada tapılmadı.")
        return

    await update.message.reply_text(
        f"Düzgün yazılış: {item['correct']}\n\n"
        f"{item['definition']}\n\n"
        f"Mənbə: {SOURCE}"
    )


def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("BOT_TOKEN tapılmadı")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lookup))
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
