import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, PreCheckoutQuery

from .core import build_launch_text, PaymentRequest, validate_precheckout


def build_play_keyboard(webapp_url: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🎮 Play", web_app=WebAppInfo(url=webapp_url))]],
        resize_keyboard=True,
    )


def build_dispatcher(webapp_url: str) -> Dispatcher:
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start_handler(message: Message):
        name = message.from_user.first_name if message.from_user else "Hunter"
        await message.answer(build_launch_text(name), reply_markup=build_play_keyboard(webapp_url))

    @dp.pre_checkout_query()
    async def pre_checkout(pcq: PreCheckoutQuery, bot: Bot):
        req = PaymentRequest(
            user_id=pcq.from_user.id,
            sku=pcq.invoice_payload,
            stars=pcq.total_amount,
            nonce=pcq.id,
        )
        await bot.answer_pre_checkout_query(pcq.id, ok=validate_precheckout(req))

    @dp.message(F.successful_payment)
    async def successful_payment(message: Message):
        await message.answer("✅ Оплата получена. Награды уже начисляются!")

    return dp


async def run() -> None:
    token = os.environ["BOT_TOKEN"]
    webapp_url = os.environ.get("WEBAPP_URL", "https://example.com")
    bot = Bot(token=token)
    dp = build_dispatcher(webapp_url)
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
