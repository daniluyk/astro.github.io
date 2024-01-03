# Импорт необходимых модулей
import asyncio
from aiogram import Bot, Dispatcher, types

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# Инициализация бота и диспетчера
bot = Bot(token="6966014456:AAGGxb9oFUZLltLd5KlED7OsziDT5-ieEE8")
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # Отправка приветственного сообщения с фото и новой клавиатурой
    photo = open('start.jpg', 'rb')
    markup = InlineKeyboardMarkup()
    item1 = InlineKeyboardButton("Правила записи", callback_data='booking_rules')
    item2 = InlineKeyboardButton("Виды консультаций", callback_data='consultation_types')
    item3 = InlineKeyboardButton("Мои контакты", callback_data='contact')
    item4 = InlineKeyboardButton("Наш магазин", url='https://t.me/+yzYS0bzE2-liZjFi')  
    markup.row(item1)
    markup.row(item2)
    markup.row(item3)
    markup.row(item4)

    # Получение имени и фамилии пользователя
    user_name = message.from_user.first_name
    user_last_name = message.from_user.last_name if message.from_user.last_name else ""

    # Форматирование сообщения с выделением имени и фамилии жирным шрифтом в HTML
    caption = f"Привет *{user_name} {user_last_name}* \n\nРада приветствовать тебя в своём боте"

    message = await bot.send_photo(message.chat.id, photo, caption, parse_mode='MarkdownV2', reply_markup=markup)
    return message.message_id  # Возвращаем ID сообщения

# Функция для редактирования сообщения с фото и клавиатурой
async def edit_photo_message(chat_id, message_id, new_photo, caption, markup, parse_mode=None):
    await bot.delete_message(chat_id=chat_id, message_id=message_id)  # Удаляем старое сообщение
    await bot.send_photo(chat_id, new_photo, caption=caption, reply_markup=markup, parse_mode=parse_mode)

# Функция для обработки кнопки "Мой контакт"
@dp.callback_query_handler(lambda query: query.data == 'contact')
async def handle_contact(callback_query: types.CallbackQuery):
    new_photo = open('start.jpg', 'rb')  # Укажите путь к фотографии

    markup = InlineKeyboardMarkup()
    astrolog_button = InlineKeyboardButton("Телеграм", url='https://t.me/anasteiiisha12')
    channel_button = InlineKeyboardButton("Телеграм канал", url='https://t.me/anasteiiisha12')
    insta_button = InlineKeyboardButton("Instagram", url='https://www.instagram.com/nastya_shvetsova12')
    back_button = InlineKeyboardButton("Назад", callback_data='back_to_main')
    markup.row(astrolog_button)
    markup.row(insta_button)
    markup.row(channel_button)
    markup.row(back_button)

    await edit_photo_message(
        callback_query.message.chat.id,
        callback_query.message.message_id,
        new_photo,
        caption="*Мои контакты*",
        markup=markup,
        parse_mode='MarkdownV2'
    )


# Функция для обработки кнопки "Правила записи"
@dp.callback_query_handler(lambda query: query.data == 'booking_rules')
async def handle_booking_rules(callback_query: types.CallbackQuery):
    # Редактирование сообщения с новым фото, подписью и клавиатурой
    new_photo = open('booking.jpg', 'rb')
    markup = InlineKeyboardMarkup()
    back_button = InlineKeyboardButton("Назад", callback_data='back_to_main')
    book_button = InlineKeyboardButton("Записаться", url='https://t.me/anasteiiisha12')
    markup.row(back_button, book_button)

    await edit_photo_message(
        callback_query.message.chat.id,
        callback_query.message.message_id,
        new_photo,
        caption="*Обязательно к прочтению*",
        markup=markup,
        parse_mode='MarkdownV2'
    )

# Функция для обработки кнопки "Виды консультаций"
@dp.callback_query_handler(lambda query: query.data == 'consultation_types')
async def handle_consultation_types(callback_query: types.CallbackQuery):
    # Редактирование сообщения с новым фото, подписью и клавиатурой для видов консультаций
    new_photo = open('consultation.jpg', 'rb')  # Измените имя файла и путь к изображению

    # Создание кнопок для разных уровней консультаций
    markup = InlineKeyboardMarkup()
    
    map_button = InlineKeyboardButton("Анализ личности", callback_data='level_map')
    markup.row(map_button)

    consultation_buttons = [
        InlineKeyboardButton("Совместимость", callback_data='level_year'),
        InlineKeyboardButton("Исполнение желаний", callback_data='level_dreem'),
        InlineKeyboardButton("Беременность", callback_data='level_baby'),
        InlineKeyboardButton("Любовная совместимость", callback_data='level_love'),
        InlineKeyboardButton("Финансы", callback_data='level_money'),
        InlineKeyboardButton("Карма", callback_data='level_karm')
    ]

    # Разделение кнопок на строки
    rows = [
        consultation_buttons[i:i + 2] for i in range(0, len(consultation_buttons), 2)
    ]

    # Добавление строк кнопок в разметку
    for row in rows:
        markup.row(*row)



    # Добавление кнопки "Назад" отдельно в ширину двух кнопок
    back_button = InlineKeyboardButton("Назад", callback_data='back_to_main')
    markup.row(back_button)


    await edit_photo_message(
        callback_query.message.chat.id,
        callback_query.message.message_id,
        new_photo,
        caption="Выберите консультацию",
        markup=markup
    )


# Функция для обработки кнопок уровней консультаций
@dp.callback_query_handler(lambda query: query.data.startswith('level_'))
async def handle_consultation_levels(callback_query: types.CallbackQuery):
    # Получение уровня консультации из callback_data
    level = callback_query.data.split('_')[1]

    # Словарь с путями к изображениям и описаниями для каждого уровня консультаций
    consultation_data = {
        'year': {'image_path': 'year.jpg', 'description': '*Стоимость 1990 Руб*'},
        '3month': {'image_path': '3month.jpg', 'description': '*Стоимость 1990 Руб*'},
        'dreem': {'image_path': 'dreem.jpg', 'description': '*Стоимость 790 Руб*'},
        'map': {'image_path': 'map.jpg', 'description': '*Стоимость 3490 Руб*'},
        'baby': {'image_path': 'baby.jpg', 'description': '*Стоимость 1990 Руб*'},
        'love': {'image_path': 'love.jpg', 'description': '*Стоимость 2490 Руб*'},
        'money': {'image_path': 'money.jpg', 'description': '*Стоимость 2690 Руб*'},
        'karm': {'image_path': 'karm.jpg', 'description': '*Стоимость 2490 Руб*'}
    }

    # Словарь, соотносящий значения callback_data с текстами кнопок
    consultation_names = {
        'year': 'Совместимость',
        '3month': 'Прогноз на 3 месяца',
        'dreem': 'Исполнение желаний',
        'map': 'Анализ личности',
        'baby': 'Беременность',
        'love': 'Любовная совместимость',
        'money': 'Финансы',
        'karm': 'Карма',
    }


    # Получение данных для конкретного уровня
    consultation_info = consultation_data.get(level, {'image_path': 'default_consultation.jpg', 'description': 'Описание для консультации по умолчанию'})

    # Редактирование сообщения с фото, подписью и клавиатурой для уровней консультаций
    new_photo = open(consultation_info['image_path'], 'rb')  # Измените имя файла и путь к изображению для каждого уровня

    # Создание кнопок для уровней консультаций
    markup = InlineKeyboardMarkup()
    back_button = InlineKeyboardButton("Назад", callback_data='back_to_consultation_types')
    book_button = InlineKeyboardButton("Записаться", url='https://t.me/anasteiiisha12')
    markup.row(back_button, book_button)

    # Получение названия консультации из словаря
    consultation_name = consultation_names.get(level, 'Неизвестная консультация')

    await edit_photo_message(
        callback_query.message.chat.id,
        callback_query.message.message_id,
        new_photo,
        caption=f"Выбрана консультация *{consultation_name}*\n\n{consultation_info['description']}",
        markup=markup,
        parse_mode='MarkdownV2'
    )

# Функция для кнопки "Назад" из уровней консультаций
@dp.callback_query_handler(lambda query: query.data == 'back_to_consultation_types')
async def handle_back_to_consultation_types(callback_query: types.CallbackQuery):
    # Редактирование сообщения с новым фото, подписью и клавиатурой для видов консультаций
    new_photo = open('consultation.jpg', 'rb')  # Измените имя файла и путь к изображению



    # Создание кнопок для разных уровней консультаций
    markup = InlineKeyboardMarkup()

    map_button = InlineKeyboardButton("Анализ личности", callback_data='level_map')
    markup.row(map_button)

    consultation_buttons = [
        InlineKeyboardButton("Совместимость", callback_data='level_year'),
        InlineKeyboardButton("Исполнение желаний", callback_data='level_dreem'),
        InlineKeyboardButton("Беременность", callback_data='level_baby'),
        InlineKeyboardButton("Любовная совместимость", callback_data='level_love'),
        InlineKeyboardButton("Финансы", callback_data='level_money'),
        InlineKeyboardButton("Карма", callback_data='level_karm')
    ]

    # Разделение кнопок на строки
    rows = [
        consultation_buttons[i:i + 2] for i in range(0, len(consultation_buttons), 2)
    ]

    # Добавление строк кнопок в разметку
    for row in rows:
        markup.row(*row)



    # Добавление кнопки "Назад" отдельно в ширину двух кнопок
    back_button = InlineKeyboardButton("Назад", callback_data='back_to_main')
    markup.row(back_button)


    await edit_photo_message(
        callback_query.message.chat.id,
        callback_query.message.message_id,
        new_photo,
        caption="Выберите консультацию",
        markup=markup
    )


# Функция для обработки кнопки "Назад"
@dp.callback_query_handler(lambda query: query.data == 'back_to_main')
async def handle_back_to_main(callback_query: types.CallbackQuery):
    # Редактирование сообщения обратно на функцию start
    photo = open('start.jpg', 'rb')
    markup = InlineKeyboardMarkup()
    item1 = InlineKeyboardButton("Правила записи", callback_data='booking_rules')
    item2 = InlineKeyboardButton("Виды консультаций", callback_data='consultation_types')
    item3 = InlineKeyboardButton("Мои контакты", callback_data='contact')
    item4 = InlineKeyboardButton("Наш магазин", url='https://t.me/+yzYS0bzE2-liZjFi')  
    markup.row(item1)
    markup.row(item2)
    markup.row(item3)
    markup.row(item4)

    await edit_photo_message(
        callback_query.message.chat.id,
        callback_query.message.message_id,
        photo,
        caption="",
        markup=markup
    )
   
# Запуск бота
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling())
    loop.run_forever()

