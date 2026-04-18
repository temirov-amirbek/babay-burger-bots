from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from src.states.user import AdminStates
from src.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.models.base import Order, Product, User

admin_router = Router()

@admin_router.message(Command("admin"), F.from_user.id.in_(settings.ADMIN_IDS))
async def admin_start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Buyurtmalar", callback_data="admin_orders")],
        [InlineKeyboardButton(text="➕ Mahsulot qo'shish", callback_data="admin_add_prod")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Xabar yuborish", callback_data="admin_broadcast")]
    ])
    await message.answer("Admin paneliga xush kelibsiz!", reply_markup=keyboard)

@admin_router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery, session: AsyncSession):
    # Kunlik buyurtmalar soni
    orders_count = await session.scalar(select(func.count(Order.id)))
    total_revenue = await session.scalar(select(func.sum(Order.total_amount)))
    users_count = await session.scalar(select(func.count(User.id)))
    
    stats_text = (
        f"📊 Statistika:\n\n"
        f"👥 Foydalanuvchilar: {users_count}\n"
        f"📦 Jami buyurtmalar: {orders_count}\n"
        f"💰 Jami daromad: {total_revenue or 0} so'm"
    )
    await callback.message.edit_text(stats_text, reply_markup=callback.message.reply_markup)

@admin_router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Barcha foydalanuvchilarga yuboriladigan xabarni kiriting:")
    await state.set_state(AdminStates.broadcast)

@admin_router.message(AdminStates.broadcast)
async def send_broadcast(message: Message, state: FSMContext, session: AsyncSession):
    users = await session.scalars(select(User.id))
    count = 0
    for user_id in users:
        try:
            await message.copy_to(chat_id=user_id)
            count += 1
        except Exception:
            pass
    await message.answer(f"Xabar {count} ta foydalanuvchiga yuborildi.")
    await state.clear()
