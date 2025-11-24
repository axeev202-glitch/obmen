import logging
import json
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import dp, bot
from database import init_db, get_db, User, Advertisement, Exchange
from keyboards import get_main_menu, get_profile_keyboard, get_back_keyboard, get_ad_navigation, get_ad_details_keyboard

# Состояния
class RegistrationStates(StatesGroup):
    name = State()
    phone = State()
    city = State()

class AdStates(StatesGroup):
    title = State()
    condition = State()
    exchange = State()

# Хранилище для лент пользователей
user_feeds = {}

# ========== КОМАНДА START ==========
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message, state: FSMContext):
    db = get_db()
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if user:
        await message.answer(
            f"👋 Добро пожаловать, {user.first_name}!\nВыберите действие:",
            reply_markup=get_main_menu()
        )
    else:
        await message.answer(
            "👋 Добро пожаловать в бот для обмена телефонами!\n"
            "Введите ваше имя и фамилию:"
        )
        await RegistrationStates.name.set()

# ========== РЕГИСТРАЦИЯ ==========
@dp.message_handler(state=RegistrationStates.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📞 Введите ваш номер телефона:")
    await RegistrationStates.phone.set()

@dp.message_handler(state=RegistrationStates.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("🏙️ Введите ваш город:")
    await RegistrationStates.city.set()

@dp.message_handler(state=RegistrationStates.city)
async def process_city(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    db = get_db()
    
    new_user = User(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=user_data['name'],
        phone=user_data['phone'],
        city=message.text
    )
    
    db.add(new_user)
    db.commit()
    db.close()
    
    await state.finish()
    await message.answer(
        f"✅ Регистрация завершена!\n"
        f"👤 {user_data['name']} | 📞 {user_data['phone']} | 🏙️ {message.text}",
        reply_markup=get_main_menu()
    )

# ========== ГЛАВНОЕ МЕНЮ ==========
@dp.message_handler(lambda m: m.text == "👤 Мой профиль")
async def show_profile(message: types.Message):
    db = get_db()
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user:
        await message.answer("Сначала зарегистрируйтесь: /start")
        return
    
    ads_count = db.query(Advertisement).filter(Advertisement.user_id == user.id).count()
    
    profile_text = (
        f"👤 Ваш профиль:\n\n"
        f"📝 Имя: {user.first_name}\n"
        f"📞 Телефон: {user.phone}\n"
        f"🏙️ Город: {user.city}\n"
        f"⭐ Рейтинг: {user.rating}/5.0\n"
        f"📱 Объявлений: {ads_count}"
    )
    
    await message.answer(profile_text, reply_markup=get_profile_keyboard())
    db.close()

@dp.message_handler(lambda m: m.text == "📱 Лента объявлений")
async def show_ads_feed(message: types.Message):
    db = get_db()
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user:
        await message.answer("Сначала зарегистрируйтесь: /start")
        return
    
    ads = db.query(Advertisement).filter(
        Advertisement.user_id != user.id,
        Advertisement.is_active == True
    ).all()
    
    if not ads:
        await message.answer("📭 Пока нет объявлений для обмена")
        return
    
    user_feeds[message.from_user.id] = {'ads': ads, 'index': 0}
    await show_ad(message.from_user.id, ads[0], 0, len(ads))
    db.close()

# ========== ПОКАЗ ОБЪЯВЛЕНИЯ ==========
async def show_ad(user_id, ad, index, total):
    db = get_db()
    ad_user = db.query(User).filter(User.id == ad.user_id).first()
    
    ad.views += 1
    db.commit()
    
    caption = (
        f"📱 {ad.title}\n"
        f"📝 {ad.description}\n"
        f"🔄 Хочу: {ad.desired_exchange}\n"
        f"🏙️ {ad_user.city} | 👁️ {ad.views} | ❤️ {ad.likes}"
    )
    
    try:
        await bot.send_message(
            user_id,
            caption,
            reply_markup=get_ad_navigation(ad.id, index, total)
        )
    except:
        await bot.send_message(user_id, caption)
    
    db.close()

# ========== СОЗДАНИЕ ОБЪЯВЛЕНИЯ ==========
@dp.message_handler(lambda m: m.text == "➕ Создать объявление")
async def start_create_ad(message: types.Message, state: FSMContext):
    await message.answer(
        "Создаем объявление!\nВведите название модели телефона:",
        reply_markup=get_back_keyboard()
    )
    await AdStates.title.set()

@dp.message_handler(state=AdStates.title)
async def process_ad_title(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await state.finish()
        await message.answer("Главное меню:", reply_markup=get_main_menu())
        return
    
    await state.update_data(title=message.text)
    await message.answer("📝 Опишите состояние телефона:")
    await AdStates.condition.set()

@dp.message_handler(state=AdStates.condition)
async def process_ad_condition(message: types.Message, state: FSMContext):
    await state.update_data(condition=message.text)
    await message.answer("🔄 Что хотите получить взамен?")
    await AdStates.exchange.set()

@dp.message_handler(state=AdStates.exchange)
async def process_ad_exchange(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    db = get_db()
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    new_ad = Advertisement(
        user_id=user.id,
        title=user_data['title'],
        condition=user_data['condition'],
        desired_exchange=message.text
    )
    
    db.add(new_ad)
    db.commit()
    db.close()
    
    await state.finish()
    await message.answer(
        f"✅ Объявление создано!\n\n"
        f"📱 {user_data['title']}\n"
        f"📝 {user_data['condition']}\n"
        f"🔄 {message.text}",
        reply_markup=get_main_menu()
    )

# ========== КНОПКА НАЗАД ==========
@dp.message_handler(lambda m: m.text == "⬅️ Назад")
async def back_to_main(message: types.Message):
    await message.answer("Главное меню:", reply_markup=get_main_menu())

# ========== HELP ==========
@dp.message_handler(lambda m: m.text == "❓ Помощь")
async def show_help(message: types.Message):
    help_text = (
        "🤖 Бот для обмена телефонами\n\n"
        "📱 Создавайте объявления\n"
        "🔄 Находите подходящие варианты\n"
        "💬 Общайтесь с другими пользователями\n"
        "✅ Безопасный обмен через гаранта\n\n"
        "Для начала работы используйте кнопки ниже 👇"
    )
    await message.answer(help_text)

# ========== ЗАПУСК БОТА ==========
if __name__ == '__main__':
    print("🚀 Запуск бота...")
    init_db()
    
    # Регистрируем обработчики
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)