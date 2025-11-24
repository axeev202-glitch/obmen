from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Основное меню
def get_main_menu():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton("📱 Лента объявлений"),
        KeyboardButton("➕ Создать объявление")
    ).add(
        KeyboardButton("👤 Мой профиль"),
        KeyboardButton("❓ Помощь")
    )

# Клавиатура профиля
def get_profile_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton("📋 Мои объявления"),
        KeyboardButton("🔄 Мои обмены")
    ).add(KeyboardButton("⬅️ Назад"))

# Кнопка назад
def get_back_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("⬅️ Назад"))

# Навигация по объявлениям
def get_ad_navigation(ad_id, current_index, total_ads):
    keyboard = InlineKeyboardMarkup()
    buttons = []
    
    if current_index > 0:
        buttons.append(InlineKeyboardButton("⬅️", callback_data=f"prev_{ad_id}"))
    
    buttons.extend([
        InlineKeyboardButton("❤️", callback_data=f"like_{ad_id}"),
        InlineKeyboardButton("💬", callback_data=f"chat_{ad_id}"),
        InlineKeyboardButton("🔍", callback_data=f"details_{ad_id}")
    ])
    
    if current_index < total_ads - 1:
        buttons.append(InlineKeyboardButton("➡️", callback_data=f"next_{ad_id}"))
    
    keyboard.row(*buttons)
    return keyboard

# Детали объявления
def get_ad_details_keyboard(ad_id):
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("💬 Написать автору", callback_data=f"start_chat_{ad_id}"),
        InlineKeyboardButton("⬅️ Назад", callback_data=f"back_feed_{ad_id}")
    )