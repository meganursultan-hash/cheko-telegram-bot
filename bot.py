import os
import asyncio

from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.session.aiohttp import AiohttpSession

API_TOKEN = os.getenv("BOT_TOKEN")

router = Router()

async def ocr_receipt(image_bytes: bytes) -> list[tuple[str, float]]:
    """
    Заглушка: сюда потом подключишь реальный OCR.
    Сейчас просто возвращает фиксированные позиции.
    """
    return [
        ("Пицца Маргарита", 3800.0),
        ("Капучино", 1500.0),
    ]

def format_items(items: list[tuple[str, float]]) -> str:
    lines = []
    total = 0
    for name, amount in items:
        total += amount
        lines.append(f"- {name}: {int(amount)} ₸")
    lines.append(f"\nИтого по позициям: {int(total)} ₸")
    return "\n".join(lines)

@router.message(CommandStart())
async def cmd_start(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📸 Сканировать чек")]],
        resize_keyboard=True
    )
    await message.answer(
        "Я Cheko. Пришли мне фото чека, и я подготовлю позиции для деления.",
        reply_markup=kb
    )

@router.message(F.text == "📸 Сканировать чек")
async def ask_photo(message: Message):
    await message.answer("Пришли фото чека одним снимком — крупно, без бликов.")

@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot):
    await message.answer("Ок, читаю чек…")

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_bytes = await bot.download_file(file.file_path)
    image_bytes = file_bytes.read()

    items = await ocr_receipt(image_bytes)

    if not items:
        await message.answer("Не удалось распознать позиции. Попробуй сделать фото четче.")
        return

    text = "Вот что я вижу по чеку:\n\n"
    text += format_items(items)
    text += "\n\nДальше добавим распределение по людям в следующей версии."

    await message.answer(text, parse_mode=ParseMode.HTML)

async def main():
    if not API_TOKEN:
        raise RuntimeError("Укажи BOT_TOKEN в переменных окружения")

    session = AiohttpSession()
    bot = Bot(token=API_TOKEN, session=session)
    dp = Dispatcher()
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


