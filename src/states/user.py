from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    language = State()
    phone = State()
    name = State()

class Ordering(StatesGroup):
    category = State()
    product = State()
    cart = State()
    address = State()
    confirm = State()

class AdminStates(StatesGroup):
    menu = State()
    add_product_name = State()
    add_product_price = State()
    add_product_image = State()
    broadcast = State()
