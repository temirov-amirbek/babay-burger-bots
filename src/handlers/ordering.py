from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.keyboards.user import get_categories_keyboard, get_products_keyboard, get_cart_keyboard, get_main_menu
from src.states.user import Ordering
from src.utils.i18n import i18n
from src.models.base import Category, Product, Order, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.config import settings

ordering_router = Router()

@ordering_router.message(F.text.in_(["🍔 Buyurtma berish", "🍔 Заказать", "🍔 Order"]))
async def show_categories(message: Message, session: AsyncSession):
    user = await session.get(User, message.from_user.id)
    lang = user.language if user else "uz"
    
    categories = await session.scalars(select(Category))
    await message.answer(i18n.get(lang, "category-select"), 
                         reply_markup=get_categories_keyboard(categories.all(), lang))

@ordering_router.callback_query(F.data.startswith("cat_"))
async def show_products(callback: CallbackQuery, session: AsyncSession):
    cat_id = int(callback.data.split("_")[1])
    user = await session.get(User, callback.from_user.id)
    lang = user.language if user else "uz"
    
    products = await session.scalars(select(Product).where(Product.category_id == cat_id, Product.is_active == True))
    await callback.message.edit_text(i18n.get(lang, "product-select"), 
                                    reply_markup=get_products_keyboard(products.all(), lang))

@ordering_router.callback_query(F.data.startswith("prod_"))
async def add_to_cart(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    prod_id = int(callback.data.split("_")[1])
    user = await session.get(User, callback.from_user.id)
    lang = user.language if user else "uz"
    
    data = await state.get_data()
    cart = data.get("cart", {})
    cart[str(prod_id)] = cart.get(str(prod_id), 0) + 1
    await state.update_data(cart=cart)
    
    await callback.answer(i18n.get(lang, "add-to-cart"))

@ordering_router.message(F.text.in_(["🛒 Savat", "🛒 Корзина", "🛒 Cart"]))
async def show_cart(message: Message, state: FSMContext, session: AsyncSession):
    user = await session.get(User, message.from_user.id)
    lang = user.language if user else "uz"
    
    data = await state.get_data()
    cart = data.get("cart", {})
    
    if not cart:
        await message.answer(i18n.get(lang, "cart-empty"))
        return

    text = f"{i18n.get(lang, 'cart-title')}\n\n"
    total = 0
    for prod_id, count in cart.items():
        product = await session.get(Product, int(prod_id))
        name = getattr(product, f"name_{lang}")
        price = product.price * count
        total += price
        text += f"• {name} x {count} = {price} so'm\n"
    
    text += f"\n{i18n.get(lang, 'total-sum', sum=total)}"
    await message.answer(text, reply_markup=get_cart_keyboard(lang, i18n.get))

@ordering_router.callback_query(F.data == "checkout")
async def start_checkout(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    user = await session.get(User, callback.from_user.id)
    lang = user.language if user else "uz"
    
    await callback.message.answer(i18n.get(lang, "ask-address"))
    await state.set_state(Ordering.address)

@ordering_router.message(Ordering.address)
async def process_address(message: Message, state: FSMContext, session: AsyncSession):
    user = await session.get(User, message.from_user.id)
    lang = user.language if user else "uz"
    
    address = message.text if message.text else "Location sent"
    await state.update_data(address=address)
    
    data = await state.get_data()
    cart = data.get("cart")
    
    total = 0
    for prod_id, count in cart.items():
        product = await session.get(Product, int(prod_id))
        total += product.price * count
    
    # Buyurtmani saqlash
    new_order = Order(
        user_id=message.from_user.id,
        items=cart,
        total_amount=total,
        delivery_address=address,
        status="pending"
    )
    session.add(new_order)
    await session.flush() # ID olish uchun
    
    await message.answer(i18n.get(lang, "order-confirmed", id=new_order.id), 
                         reply_markup=get_main_menu(lang, i18n.get))
    
    # Adminlarga xabar berish
    for admin_id in settings.ADMIN_IDS:
        try:
            admin_text = i18n.get("uz", "admin-new-order") + "\n"
            admin_text += i18n.get("uz", "admin-order-details", 
                                  name=user.full_name, phone=user.phone_number, 
                                  address=address, total=total)
            await message.bot.send_message(admin_id, admin_text)
        except Exception:
            pass
            
    await session.commit()
    await state.clear()
