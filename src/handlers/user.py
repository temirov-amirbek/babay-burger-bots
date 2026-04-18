from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from src.keyboards.user import get_language_keyboard, get_phone_keyboard, get_main_menu
from src.states.user import Registration, Ordering
from src.utils.i18n import i18n
from src.models.base import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

user_router = Router()

@user_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(i18n.get("uz", "welcome"), reply_markup=get_language_keyboard())
    await state.set_state(Registration.language)

@user_router.callback_query(Registration.language, F.data.startswith("lang_"))
async def select_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(lang=lang)
    await callback.message.delete()
    await callback.message.answer(i18n.get(lang, "phone-request"), 
                                 reply_markup=get_phone_keyboard(lang, i18n.get))
    await state.set_state(Registration.phone)

@user_router.message(Registration.phone, F.contact)
async def get_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    data = await state.get_data()
    lang = data.get("lang")
    await message.answer(i18n.get(lang, "ask-name"), reply_markup=ReplyKeyboardRemove())
    await state.set_state(Registration.name)

@user_router.message(Registration.name)
async def get_name(message: Message, state: FSMContext, session: AsyncSession):
    name = message.text
    data = await state.get_data()
    lang = data.get("lang")
    phone = data.get("phone")
    
    # Userni DBga saqlash
    new_user = User(id=message.from_user.id, full_name=name, phone_number=phone, language=lang)
    session.add(new_user)
    await session.commit()
    
    await message.answer(i18n.get(lang, "main-menu"), reply_markup=get_main_menu(lang, i18n.get))
    await state.clear()

@user_router.message(F.text == "🍔 Buyurtma berish")
@user_router.message(F.text == "🍔 Заказать")
@user_router.message(F.text == "🍔 Order")
async def start_order(message: Message, state: FSMContext, session: AsyncSession):
    # Bu yerda kategoriyalarni DBdan olish kerak
    # Hozircha misol uchun
    lang = "uz" # Bu yerda user tilini DBdan olish kerak
    await message.answer(i18n.get(lang, "category-select"))
    await state.set_state(Ordering.category)
