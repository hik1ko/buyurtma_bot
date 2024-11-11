import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from sqlalchemy import insert

from middleware import CustomMiddleware
from misc import GeneralStates
from utils import get_admins
from handlers.handlers import *

TOKEN = getenv("BOT_TOKEN")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()


@main_router.message(Command('start'))
async def command_start_handler(message: Message, state: FSMContext, session: Session):
    is_exists = session.query(User).filter(User.tg_id == message.from_user.id).scalar()
    if not is_exists:
        user = {
            "tg_id": message.from_user.id,
            "username": message.from_user.username,
            "full_name": message.from_user.full_name,
        }
        await message.answer(
            text=f"Assalomu alaykum {html.bold(message.from_user.full_name)}, iltimos kuting admin bo'lganingizdan keyin botdan foydalanishingiz mumkin.")
        session.execute(insert(User).values(**user))
        session.commit()
        await state.set_state(GeneralStates.start)
    else:
        if message.from_user.id in await get_admins(session):
            await state.set_state(AdminStates.main_menu)
            await message.answer(text="Admin panelga xush kelibsiz.", reply_markup=await admin_button())


async def main() -> None:
    dp.include_router(*[main_router])
    dp.update.middleware(CustomMiddleware())
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
