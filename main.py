import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton  # Импорт необходимых классов
from database import add_user, get_all_users, is_user_registered
import sqlite3

# Инициализация бота и диспетчера
bot = Bot(token="6966014456:AAGGxb9oFUZLltLd5KlED7OsziDT5-ieEE8")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Создание базы данных
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Создание таблицы, если ее нет
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users
    (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, last_name TEXT, birth_date TEXT, birth_place TEXT)
''')

# Закрытие соединения
conn.close()

# Определение состояний
class Registration(StatesGroup):
    birth_date = State()
    birth_place = State()

# Функция старт
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # Проверка, зарегистрирован ли пользователь
    if is_user_registered(message.from_user.id):
        # Отправка сообщения с кнопками
        # Отправка фотографии с текстом и клавиатурой
        markup = InlineKeyboardMarkup()
        item1 = InlineKeyboardButton("Правила записи", callback_data='booking_rules')
        item2 = InlineKeyboardButton("Виды консультаций", callback_data='consultation_types')
        item3 = InlineKeyboardButton("Мои контакты", callback_data='contact')
        item4 = InlineKeyboardButton("Наш магазин", url='https://t.me/+yzYS0bzE2-liZjFi')  
        markup.row(item1)
        markup.row(item2)
        markup.row(item3)
        markup.row(item4)

        with open('start.jpg', 'rb') as photo:
            await bot.send_photo(message.chat.id, photo, caption="Выбирай консультацию!", reply_markup=markup)
    else:
        # Отправка приветственного сообщения
        await bot.send_message(message.chat.id, "Привет, давай зарегистрируем тебя")

        # Запрос даты рождения
        await bot.send_message(message.chat.id, "Пожалуйста, введите свою дату рождения в формате ДД.ММ.ГГГГ")

        # Переход в состояние birth_date
        await Registration.birth_date.set()

# Обработка даты рождения
@dp.message_handler(state=Registration.birth_date)
async def process_birth_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['birth_date'] = message.text

    # Запрос места рождения
    await bot.send_message(message.chat.id, "Пожалуйста, введите место рождения")

    # Переход в состояние birth_place
    await Registration.next()

@dp.message_handler(state=Registration.birth_place)
async def process_birth_place(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['birth_place'] = message.text

    # Добавление пользователя в базу данных
    add_user(message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, data['birth_date'], data['birth_place'])

    # Завершение машины состояний
    try:
        await state.finish()
    except KeyError:
        pass

    # Создание кнопок
    markup = InlineKeyboardMarkup()
    item1 = InlineKeyboardButton("Правила записи", callback_data='booking_rules')
    item2 = InlineKeyboardButton("Виды консультаций", callback_data='consultation_types')
    item3 = InlineKeyboardButton("Мои контакты", callback_data='contact')
    item4 = InlineKeyboardButton("Наш магазин", url='https://t.me/+yzYS0bzE2-liZjFi')  
    markup.row(item1)
    markup.row(item2)
    markup.row(item3)
    markup.row(item4)

    # Отправка сообщения с кнопками
    # Отправка фотографии с текстом и клавиатурой
    with open('start.jpg', 'rb') as photo:
        await bot.send_photo(message.chat.id, photo, caption="Отлично! Поздравляю, с успешной регестрацией тебя!\n\nВыбирай консультацию!", reply_markup=markup)

@dp.message_handler(commands=['info'])
async def process_info(message: types.Message):
    # Проверка, является ли пользователь админом
    if message.from_user.id == 2085376749:
        # Получение списка всех пользователей
        users = get_all_users()

        # Формирование сообщения
        message_text = "Список всех пользователей:\n"
        
        counter = 1
        for user in users:
            message_text += f"{counter}. ID: *{user.id}*,\n Username: *@{user.username}*,\n Имя: {user.first_name},\n Фамилия: *{user.last_name}*,\n Дата рождения: *{user.birth_date}*,\n Место Рождения: *{user.birth_place}*\n\n"
            counter += 1

        # Отправка сообщения
        await bot.send_message(message.chat.id, message_text, parse_mode="Markdown")
    else:
        await bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")

@dp.message_handler(content_types=['text'])
async def send_text(message: types.Message):
    # Check if the user is an admin
    if message.from_user.id == 2085376749:
        # Get the list of all users
        users = get_all_users()

        # Get the text that the admin sent
        text = message.text

        # Send the text to all users
        sent_messages = []
        for user in users:
            sent_message = await bot.send_message(chat_id=user.id, text=text)
            sent_messages.append(sent_message)

        # Delete the messages after a few seconds
        await asyncio.sleep(600)
        for sent_message in sent_messages:
            await bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)
    else:
        await bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")

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
    insta_button = InlineKeyboardButton("Instagram", url='https://www.instagram.com/nastya_shvetsova12')
    back_button = InlineKeyboardButton("Назад", callback_data='back_to_main')
    markup.row(astrolog_button)
    markup.row(insta_button)
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

class UserState(StatesGroup):
    consultation_name = State()

state = UserState.consultation_name

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
    book_button = InlineKeyboardButton("Записаться", callback_data='book')
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

    await dp.current_state(chat=callback_query.message.chat.id, user=callback_query.from_user.id).update_data(consultation_name=consultation_name)

@dp.callback_query_handler(lambda query: query.data == 'book')
async def process_callback_book(callback_query: types.CallbackQuery, state: FSMContext):
    # Get the user's information
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.full_name
    user_username = callback_query.from_user.username

    # Get the consultation the user chose
    data = await state.get_data()
    consultation = data.get('consultation_name', 'Неизвестная консультация')

    # Answer the callback query
    # Send the message
    message = await bot.send_message(callback_query.from_user.id, text="*Отлично! Я получила твою запись\nСкоро с тобой свяжусь!*", parse_mode='Markdown')

    # Schedule the message to be deleted after 10 seconds
    await asyncio.sleep(10)
    await bot.delete_message(callback_query.from_user.id, message.message_id)

    # Send the user's information and the consultation to the admin
    admin_id = 2085376749  # Replace with your admin's ID
    admin_message = f"Пользователь *{user_name}*\n*@{user_username}*\n\n выбрал консультацию: *{consultation}*"
    await bot.send_message(chat_id=admin_id, text=admin_message, parse_mode='Markdown')

    # Answer the callback query
    await bot.answer_callback_query(callback_query.id)
    

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


