from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def get_language_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbekcha", callback_data="lang_uz")
    builder.button(text="🇷🇺 Русский", callback_data="lang_ru")
    builder.button(text="🇺🇸 English", callback_data="lang_en")
    builder.adjust(1)
    return builder.as_markup()

def get_phone_keyboard(lang: str, i18n_func):
    builder = ReplyKeyboardBuilder()
    builder.button(text=i18n_func(lang, "send-phone"), request_contact=True)
    return builder.as_markup(resize_keyboard=True)

def get_main_menu(lang: str, i18n_func):
    builder = ReplyKeyboardBuilder()
    builder.button(text=i18n_func(lang, "btn-order"))
    builder.button(text=i18n_func(lang, "btn-my-orders"))
    builder.button(text=i18n_func(lang, "btn-about"))
    builder.button(text=i18n_func(lang, "btn-contact"))
    builder.button(text=i18n_func(lang, "btn-settings"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_categories_keyboard(categories, lang: str):
    builder = InlineKeyboardBuilder()
    for cat in categories:
        name = getattr(cat, f"name_{lang}")
        builder.button(text=name, callback_data=f"cat_{cat.id}")
    builder.adjust(2)
    return builder.as_markup()

def get_products_keyboard(products, lang: str):
    builder = InlineKeyboardBuilder()
    for prod in products:
        name = getattr(prod, f"name_{lang}")
        builder.button(text=f"{name} - {prod.price} so'm", callback_data=f"prod_{prod.id}")
    builder.button(text="🔙 Ortga", callback_data="back_to_cats")
    builder.adjust(1)
    return builder.as_markup()

def get_cart_keyboard(lang: str, i18n_func):
    builder = InlineKeyboardBuilder()
    builder.button(text=i18n_func(lang, "btn-checkout"), callback_data="checkout")
    builder.button(text=i18n_func(lang, "btn-clear-cart"), callback_data="clear_cart")
    builder.adjust(1)
    return builder.as_markup()
