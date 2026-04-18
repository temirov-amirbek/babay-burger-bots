import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    ADMIN_IDS: List[int] = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]
    DB_URL: str = os.getenv("DB_URL")
    
    # Qo'shimcha sozlamalar
    DELIVERY_PRICE: int = 15000
    MIN_ORDER_AMOUNT: int = 30000
    SUPPORT_URL: str = "https://t.me/babay_support"

settings = Settings()
