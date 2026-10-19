import json
import os
from difflib import get_close_matches
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


def normalize(text: str) -> str:
    # Azərbaycan dilində I → ı, İ → i
    return text.replace("I", "ı").replace("İ", "i").casefold()


WORDS = {normalize(k): v for k, v in DATA["words"].items()}
SOURCE = DATA.get("source", "https://orfoqrafiya.azleks.az/")
WORD_KEYS = list(WORDS.keys())


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Bir söz yazın. Düzgün yazılışı və izahı göndərəcəyəm."
    )


async def lookup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (update.message.text or "").strip()
    if not text:
        return

    key = normalize(text)
    item = WORDS.get(key)
    if item:
        await update.message.reply_text(
            f"Düzgün yazılış: {item['correct']}\n\n"
            f"{item['definition']}\n\n"
            f"İzah: bot redaksiyası.\n"
            f"Yazılışı yoxlamaq üçün: {SOURCE}"
        )
        return

    # Oxşar sözlər təklif et
    matches = get_close_matches(key, WORD_KEYS, n=3, cutoff=0.6)
    if matches:
        suggestions = []
        for m in matches:
            correct = WORDS[m]["correct"]
            suggestions.append(correct)
        text_sugg = ", ".join(suggestions)
        await update.message.reply_text(
            f"Bu söz bazada tapılmadı.\n\n"
            f"Oxşar yazılışlar: {text_sugg}\n\n"
            f"Yazılışı yoxlamaq üçün: {SOURCE}"
        )
    else:
        await update.message.reply_text(
            f"Bu söz bazada tapılmadı.\n\nYazılışı yoxlamaq üçün: {SOURCE}"
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
