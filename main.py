import os
import aiogram
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import ChatNotFound
from database import add_user, get_all_users, is_user_registered, get_user_info




#Токен
token = "6966014456:AAGGxb9oFUZLltLd5KlED7OsziDT5-ieEE8" 

# Инициализация бота и диспетчера
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

#Переменные нужные
admin_id = 2085376749 #Админ
admin_command = 'adminDan' #Команда для админки

channel_id = -1002060801138 #Канал основной
chanel_url = 'https://t.me/+yzYS0bzE2-liZjFi' #Ссылка на тг канал

channel_id_order = -1002079891249 #Канал для заказов

instagram_url = 'https://www.instagram.com/nastya_shvetsova12' #Ссылка на инсту
telegram_contact = 'https://t.me/anasteiiisha12' #Ссылка на тг


#Кнопки Колибровки самая верхняя, редактируеться колбэк после level_
up_button = InlineKeyboardButton("Анализ личности", callback_data='level_map')

#Кнопки консультаций, редактируеться колбэк после level_
global consultation_buttons
consultation_buttons = [
    InlineKeyboardButton("Совместимость", callback_data='level_year'),
    InlineKeyboardButton("Исполнение желаний", callback_data='level_dreem'),
    InlineKeyboardButton("Беременность", callback_data='level_baby'),
    InlineKeyboardButton("Любовная совместимость", callback_data='level_love'),
    InlineKeyboardButton("Финансы", callback_data='level_money'),
    InlineKeyboardButton("Карма", callback_data='level_karm')
]
#Названия кнопок
global consultation_names
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
#Данные консультаций
global consultation_data
consultation_data = {
    'year': {'image_path': 'consult/year.jpg', 'description': '*Стоимость 1990 Руб*'},
    '3month': {'image_path': 'consult/3month.jpg', 'description': '*Стоимость 1990 Руб*'},
    'dreem': {'image_path': 'consult/dreem.jpg', 'description': '*Стоимость 790 Руб*'},
    'map': {'image_path': 'consult/map.jpg', 'description': '*Стоимость 2990 Руб*'},
    'baby': {'image_path': 'consult/baby.jpg', 'description': '*Стоимость 1990 Руб*'},
    'love': {'image_path': 'consult/love.jpg', 'description': '*Стоимость 2490 Руб*'},
    'money': {'image_path': 'consult/money.jpg', 'description': '*Стоимость 2490 Руб*'},
    'karm': {'image_path': 'consult/karm.jpg', 'description': '*Стоимость 2390 Руб*'}
}

# Создание базы данных
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users
    (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, last_name TEXT, birth_date TEXT, birth_place TEXT)
''')
conn.close()


# Определение состояний
class Registration(StatesGroup):
    birth_date = State()
    birth_place = State()
    
# РЕДАКТИРУЕТЬСЯ ПОД ЗАКАЗЧИКА!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# РЕДАКТИРУЕТЬСЯ ПОД ЗАКАЗЧИКА!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # РЕДАКТИРУЕТЬСЯ ПОД ЗАКАЗЧИКА!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@dp.message_handler(commands=['start'])
async def start(message: types.Message):  # Замените на ваш chat_id канала
    user_id = message.from_user.id

    if await is_user_subscribed(user_id, channel_id):# Проверка, зарегистрирован ли пользователь
        if is_user_registered(message.from_user.id):
            # Отправка сообщения с кнопками
            # Отправка фотографии с текстом и клавиатурой 
            markup = InlineKeyboardMarkup()
            item1 = InlineKeyboardButton("Правила записи", callback_data='booking_rules')
            item2 = InlineKeyboardButton("Виды консультаций", callback_data='consultation_types')
            item3 = InlineKeyboardButton("Мои контакты", callback_data='contact')
            item4 = InlineKeyboardButton("Мой канал", url=chanel_url)  
            markup.row(item1)
            markup.row(item2)
            markup.row(item3)
            markup.row(item4)

            with open('bot/start.jpg', 'rb') as photo:
                await bot.send_photo(message.chat.id, photo, caption="Выбирай консультацию!", reply_markup=markup)
        else:
            # Отправка приветственного сообщения
            await bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAELF2BllwbgQNjS8m89jXLUhil9UTJrJAACAQEAAladvQoivp8OuMLmNDQE")

            # Запрос даты рождения
            await bot.send_message(message.chat.id, "Пожалуйста, введите свою дату рождения и точное время в формате\n\n*(ДД.ММ.ГГГГ ЧЧ:ММ)\n(12.12.2000 12:12)\n\nВАЖНО! Указывай точное время рождения, в противном случае, я не смогу нести ответсвенность за 100% качество консультаций*", parse_mode="Markdown")

            # Переход в состояние birth_date
            await Registration.birth_date.set()
    else:
        markup = InlineKeyboardMarkup()
        item1 = InlineKeyboardButton("Подписаться", url=chanel_url)
        item2 = InlineKeyboardButton("Подписалась", callback_data='start_sub')
        markup.row(item1)
        markup.row(item2)
        await bot.send_message(message.chat.id, "Подпишитесь на канал, чтобы продолжить регистрацию\nПосле подписки, нажмите\n*'Подписалась'*", reply_markup=markup, parse_mode="Markdown")
        await bot.delete_message(message.chat.id, message.message_id)

# РЕДАКТИРУЕТЬСЯ ПОД ЗАКАЗЧИКА!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # РЕДАКТИРУЕТЬСЯ ПОД ЗАКАЗЧИКА!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # РЕДАКТИРУЕТЬСЯ ПОД ЗАКАЗЧИКА!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
@dp.callback_query_handler(lambda query: query.data == 'start_sub')
async def handle_start_sub(callback_query: types.CallbackQuery): 
    user_id = callback_query.from_user.id

    if await is_user_subscribed(user_id, channel_id):
        if is_user_registered(user_id):
            markup = InlineKeyboardMarkup()
            item1 = InlineKeyboardButton("Правила записи", callback_data='booking_rules')
            item2 = InlineKeyboardButton("Виды консультаций", callback_data='consultation_types')
            item3 = InlineKeyboardButton("Мои контакты", callback_data='contact')
            item4 = InlineKeyboardButton("Мой канал", url=chanel_url)  
            markup.row(item1)
            markup.row(item2)
            markup.row(item3)
            markup.row(item4)

            with open('bot/start.jpg', 'rb') as photo:
                await bot.send_photo(user_id, photo, caption="Выбирай консультацию!", reply_markup=markup)
        else:
            # Отправка приветственного сообщения
            await bot.send_sticker(user_id, "CAACAgIAAxkBAAELF2BllwbgQNjS8m89jXLUhil9UTJrJAACAQEAAladvQoivp8OuMLmNDQE")

            # Запрос даты рождения
            await bot.send_message(user_id, "Пожалуйста, введите свою дату рождения и точное время в формате\n\n*(ДД.ММ.ГГГГ ЧЧ:ММ)\n(12.12.2000 12:12)\n\nВАЖНО! Указывай точное время рождения, в противном случае, я не смогу нести ответсвенность за 100% качество консультаций*", parse_mode="Markdown")

            # Переход в состояние birth_date
            await Registration.birth_date.set()
    else:
        markup = InlineKeyboardMarkup()
        item1 = InlineKeyboardButton("Подписаться", url=chanel_url)
        item2 = InlineKeyboardButton("Подписалась", callback_data='start_sub')
        markup.row(item1)
        markup.row(item2)
        await bot.send_message(user_id, "Подпишись на мой канал, чтобы получить скидку 10% на первую консультацию!\nПосле подписки, нажми\n*'Подписалась'*", reply_markup=markup, parse_mode="Markdown")
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)

#Проверка подписан ли пользователь
async def is_user_subscribed(user_id, channel_id):
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        if member.status in ['left', 'kicked']:
            return False
        else:
            return True
    except ChatNotFound:
        return False
    

# РЕДАКТИРУЕТЬСЯ ПОД ЗАКАЗЧИКА!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # РЕДАКТИРУЕТЬСЯ ПОД ЗАКАЗЧИКА!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # РЕДАКТИРУЕТЬСЯ ПОД ЗАКАЗЧИКА!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  
# Обработка даты рождения
@dp.message_handler(state=Registration.birth_date)
async def process_birth_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['birth_date'] = message.text

    # Запрос места рождения
    await bot.send_message(message.chat.id, "Пожалуйста, введите место рождения в формате\n\n*(Страна, Область, Город)*", parse_mode="Markdown")

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
    item4 = InlineKeyboardButton("Мой канал", url=chanel_url)  
    markup.row(item1)
    markup.row(item2)
    markup.row(item3)
    markup.row(item4)

    # Отправка сообщения с кнопками
    # Отправка фотографии с текстом и клавиатурой
    with open('bot/start.jpg', 'rb') as photo:
        await bot.send_photo(message.chat.id, photo, caption="Отлично! Поздравляю, с успешной регистрацией тебя!\n\nМеня зовут *Анастасия*\nЯ *сертифицированный* астролог.\n\n*Моя цель* - помочь тебе разобраться в себе, открыть новые грани личности и стать еще лучше", reply_markup=markup, parse_mode="Markdown")

# Обработчик нажатия на кнопку "Назад Админка"
@dp.callback_query_handler(lambda c: c.data == 'back_admin')
async def process_callback_back(callback_query: types.CallbackQuery):
    # Проверка, является ли пользователь админом
    if callback_query.from_user.id == admin_id:
        # Формирование сообщения для админ панели
        message_text = "Админка"
        button_user_list = InlineKeyboardButton("Список пользователей", callback_data="user_list")
        button_user_number = InlineKeyboardButton("Количество пользователей", callback_data="user_number")
        button_mailing = InlineKeyboardButton("Общая рассылка", callback_data="mailing")


        # Создание клавиатуры
        keyboard = InlineKeyboardMarkup()
        keyboard.add(button_user_list).add(button_user_number).add(button_mailing)

        # Отправка сообщения
        await bot.edit_message_text(message_text, callback_query.message.chat.id, callback_query.message.message_id, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await bot.send_message(callback_query.message.chat.id, "У вас нет прав для выполнения этой команды.")
        
# Функция для отправки админ панели
@dp.message_handler(commands=[admin_command])
async def send_admin_panel(message: types.Message):
    # Проверка, является ли пользователь админом
    if message.from_user.id == admin_id:
        # Создание кнопок
        button_user_list = InlineKeyboardButton("Список пользователей", callback_data="user_list")
        button_user_number = InlineKeyboardButton("Количество пользователей", callback_data="user_number")
        button_mailing = InlineKeyboardButton("Общая рассылка", callback_data="mailing")


        # Создание клавиатуры
        keyboard = InlineKeyboardMarkup()
        keyboard.add(button_user_list).add(button_user_number).add(button_mailing)

        # Отправка сообщения с кнопками
        await bot.send_message(message.chat.id, "Админка", reply_markup=keyboard)
    else:
        await bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")

@dp.callback_query_handler(lambda c: c.data == 'mailing')
async def process_mailing(callback_query: types.CallbackQuery):
    # Проверка, является ли пользователь админом
    if callback_query.from_user.id == admin_id:
        # Запрос текста рассылки у администратора
        await bot.edit_message_text(chat_id=callback_query.message.chat.id, 
                                    message_id=callback_query.message.message_id, 
                                    text="Введите текст рассылки:")

        # Ожидание ответа администратора
        @dp.message_handler(content_types=['text'])
        async def handle_mailing_text(message: types.Message):
            button_back = InlineKeyboardButton("Назад", callback_data="back_admin")

        # Создание клавиатуры
            keyboard = InlineKeyboardMarkup()
            keyboard.add(button_back)
            # Получение текста рассылки
            mailing_text = message.text

            # Получение списка всех пользователей
            users = get_all_users()

            # Отправка рассылки всем пользователям
            for user in users:
                message_id = await bot.send_message(user.id, mailing_text)

                # Запуск функции удаления сообщения через 10 минут
                asyncio.create_task(delete_message_after_delay(message_id.message_id, user.id))

            # Обновление сообщения о выполнении рассылки
            await bot.edit_message_text(chat_id=callback_query.message.chat.id, 
                                        message_id=callback_query.message.message_id, 
                                        text="Рассылка выполнена.", reply_markup=keyboard)

            # Удаление обработчика ответа администратора
            dp.message_handlers.unregister(handle_mailing_text)
    else:
        await bot.send_message(callback_query.message.chat.id, "У вас нет прав для выполнения этой команды.")

async def delete_message_after_delay(message_id, chat_id):
    # Ждем 10 минут
    await asyncio.sleep(600)

    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except aiogram.utils.exceptions.MessageToDeleteNotFound:
        pass
        
@dp.callback_query_handler(lambda c: c.data == 'user_number')
async def process_callback(callback_query: types.CallbackQuery):
    # Проверка, является ли пользователь админом
    if callback_query.from_user.id == admin_id:
        button_back = InlineKeyboardButton("Назад", callback_data="back_admin")

        # Создание клавиатуры
        keyboard = InlineKeyboardMarkup()
        keyboard.add(button_back)

        # Получение списка всех пользователей
        users = get_all_users()

        # Получение количества пользователей
        user_count = len(users)

        # Отправка сообщения с количеством пользователей
        await bot.edit_message_text(chat_id=callback_query.message.chat.id, 
                                    message_id=callback_query.message.message_id, 
                                    text=f"*Количество пользователей: \n\n{user_count}*", 
                                    parse_mode="Markdown", 
                                    reply_markup=keyboard)
    else:
        await bot.send_message(callback_query.message.chat.id, "У вас нет прав для выполнения этой команды.")


@dp.callback_query_handler(lambda c: c.data in ['analytics', 'user_list'])
async def process_callback(callback_query: types.CallbackQuery):
    # Проверка, является ли пользователь админом
    if callback_query.from_user.id == admin_id:
        if callback_query.data == 'user_list':
            button_back = InlineKeyboardButton("Назад", callback_data="back_admin")

            # Создание клавиатуры
            keyboard = InlineKeyboardMarkup()
            keyboard.add(button_back)

            # Получение списка всех пользователей
            users = get_all_users()

            # Формирование сообщения
            message_text = "Список всех пользователей:\n"
            message_text1 = "Все пользователи"
            counter = 1
            for user in users:
                message_text += f"{counter}. ID: {user.id},\n Username: @{user.username},\n Имя: {user.first_name},\n Фамилия: {user.last_name},\n Дата рождения: {user.birth_date},\n Место Рождения: {user.birth_place}\n\n"
                counter += 1

            # Создание текстового файла
            with open('users.txt', 'w', encoding='utf-8') as f:
                f.write(message_text)
            # Отправка сообщения
            sent_message = await bot.edit_message_text(message_text1, callback_query.message.chat.id, callback_query.message.message_id, reply_markup=keyboard, parse_mode="Markdown")

            # Отправка файла
            with open('users.txt', 'rb') as f:
               file = await bot.send_document(callback_query.message.chat.id, f)

            # Удаление файла на сервере сразу после отправки
            os.remove('users.txt')

            # Задержка на 60 секунд (1 минута)
            await asyncio.sleep(60)

            # Удаление сообщения
            await bot.delete_message(callback_query.message.chat.id, file.message_id)
        else:
            pass
    else:
        await bot.send_message(callback_query.message.chat.id, "У вас нет прав для выполнения этой команды.")




#ТУУУУУУУУУУУУУУТ ОСНОВНАЯ ЧАССССССССССССССССССССТЬ
        #ТУУУУУУУУУУУУУУТ ОСНОВНАЯ ЧАССССССССССССССССССССТЬ
        #ТУУУУУУУУУУУУУУТ ОСНОВНАЯ ЧАССССССССССССССССССССТЬ
        #ТУУУУУУУУУУУУУУТ ОСНОВНАЯ ЧАССССССССССССССССССССТЬ




# Функция для редактирования сообщения с фото и клавиатурой
async def edit_photo_message(chat_id, message_id, new_photo, caption, markup, parse_mode=None):
    await bot.delete_message(chat_id=chat_id, message_id=message_id)  # Удаляем старое сообщение
    await bot.send_photo(chat_id, new_photo, caption=caption, reply_markup=markup, parse_mode=parse_mode)

#РЕДАКТИРУЮ
# Функция для обработки кнопки "Мой контакт"
@dp.callback_query_handler(lambda query: query.data == 'contact')
async def handle_contact(callback_query: types.CallbackQuery):
    new_photo = open('bot/contact.jpg', 'rb')

    markup = InlineKeyboardMarkup()
    astrolog_button = InlineKeyboardButton("Телеграм", url=telegram_contact)
    insta_button = InlineKeyboardButton("Instagram", url=instagram_url)
    back_button = InlineKeyboardButton("Назад", callback_data='back_to_main')
    markup.row(astrolog_button)
    markup.row(insta_button)
    markup.row(back_button)

    await edit_photo_message(
        callback_query.message.chat.id,
        callback_query.message.message_id,
        new_photo,
        caption="*Отвечаю только по вопросам консультации.*",
        markup=markup,
        parse_mode='Markdown'
    )


# Функция для обработки кнопки "Правила записи"
@dp.callback_query_handler(lambda query: query.data == 'booking_rules')
async def handle_booking_rules(callback_query: types.CallbackQuery):
    # Редактирование сообщения с новым фото, подписью и клавиатурой
    new_photo = open('bot/booking.jpg', 'rb')
    markup = InlineKeyboardMarkup()
    back_button = InlineKeyboardButton("Назад", callback_data='back_to_main')
    book_button = InlineKeyboardButton("Записаться", url=telegram_contact)
    markup.row(back_button, book_button)

    await edit_photo_message(
        callback_query.message.chat.id,
        callback_query.message.message_id,
        new_photo,
        caption="*Обязательно к прочтению*",
        markup=markup,
        parse_mode='Markdown'
    )


# Функция для обработки кнопки "Виды консультаций"
@dp.callback_query_handler(lambda query: query.data == 'consultation_types')
async def handle_consultation_types(callback_query: types.CallbackQuery):
    # Редактирование сообщения с новым фото, подписью и клавиатурой для видов консультаций
    new_photo = open('bot/consultation.jpg', 'rb')  # Измените имя файла и путь к изображению

    # Создание кнопок для разных уровней консультаций
    markup = InlineKeyboardMarkup()

    markup.row(up_button)

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
        parse_mode='Markdown'
    )

    await dp.current_state(chat=callback_query.message.chat.id, user=callback_query.from_user.id).update_data(consultation_name=consultation_name)

@dp.callback_query_handler(lambda query: query.data == 'book')
async def process_callback_book(callback_query: types.CallbackQuery, state: FSMContext):
    # Get the user's information
    user_id = callback_query.from_user.id
    user = get_user_info(user_id)

    # Get the consultation the user chose
    data = await state.get_data()
    consultation = data.get('consultation_name', 'Неизвестная консультация')

    # Answer the callback query
    # Send the message
    message = await bot.send_message(callback_query.from_user.id, text="*Отлично! Я получила твою запись\nСкоро с тобой свяжусь!\n\nВАЖНО!\nЕсли не написала в течении часа, то свяжись со мной сама, через кнопку 'Мои контакты'*", parse_mode='Markdown')

    # Schedule the message to be deleted after 10 seconds
    await asyncio.sleep(30)
    await bot.delete_message(callback_query.from_user.id, message.message_id)
    # Send the user's information and the consultation to the admin
  # Replace with your admin's ID
    admin_message = f"Пользователь *{user.first_name} {user.last_name}*\n*@{user.username}*\n выбрал консультацию: *{consultation}*\n Город: *{user.birth_place}*\n Дата рождения: *{user.birth_date}*"
    await bot.send_message(chat_id=channel_id_order, text=admin_message, parse_mode='Markdown')
        # Answer the callback query
    try:
        await bot.answer_callback_query(callback_query.id)
    except aiogram.utils.exceptions.InvalidQueryID:
        # Обработка ошибки
        pass
        
# Функция для кнопки "Назад" из уровней консультаций
@dp.callback_query_handler(lambda query: query.data == 'back_to_consultation_types')
async def handle_back_to_consultation_types(callback_query: types.CallbackQuery):
    # Редактирование сообщения с новым фото, подписью и клавиатурой для видов консультаций
    new_photo = open('bot/consultation.jpg', 'rb')  # Измените имя файла и путь к изображению



    # Создание кнопок для разных уровней консультаций
    markup = InlineKeyboardMarkup()

    markup.row(up_button)

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


@dp.callback_query_handler(lambda query: query.data == 'back_to_main')
async def handle_back_to_main(callback_query: types.CallbackQuery):
    # Редактирование сообщения обратно на функцию start
    photo = open('bot/start.jpg', 'rb')
    markup = InlineKeyboardMarkup()
    item1 = InlineKeyboardButton("Правила записи", callback_data='booking_rules')
    item2 = InlineKeyboardButton("Виды консультаций", callback_data='consultation_types')
    item3 = InlineKeyboardButton("Мои контакты", callback_data='contact')
    item4 = InlineKeyboardButton("Мой канал", url=chanel_url)  
    markup.row(item1)
    markup.row(item2)
    markup.row(item3)
    markup.row(item4)

    await edit_photo_message(
        callback_query.message.chat.id,
        callback_query.message.message_id,
        photo,
        caption="У тебя всё получится!",  # здесь вы можете добавить свой текст
        markup=markup
    )

# Запуск бота
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling())
    loop.run_forever()
