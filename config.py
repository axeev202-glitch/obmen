from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Ваши данные
BOT_TOKEN = "8364853114:AAGfVhFQjq14TnoGSaMOtW3nErpYrtYzvF0"
ADMIN_IDS = [1188933834]

# Инициализация
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Настройки
GUARANTOR_CONTACT = "📞 Контакт гаранта: @Axeev\n📍 Адрес: укажите ваш адрес"
DATABASE_URL = "sqlite:///exchange_bot.db"