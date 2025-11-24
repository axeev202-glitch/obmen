from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Ваши данные
BOT_TOKEN = "8405555671:AAExA31C9BW6zd4QlTCqU_1OEor7khUSfV8"
ADMIN_IDS = [1188933834]

# Инициализация
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Настройки
GUARANTOR_CONTACT = "📞 Контакт гаранта: @Axeev\n📍 Адрес: укажите ваш адрес"
DATABASE_URL = "sqlite:///exchange_bot.db"