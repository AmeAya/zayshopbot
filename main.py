import os
import telebot
import requests
from dotenv import load_dotenv

load_dotenv()


bot = telebot.TeleBot(os.environ.get('TOKEN'))


@bot.message_handler(commands=['start'], content_types=['text'])
def start(message):
    bot.send_message(message.chat.id, 'Привет. Выберите номер категории из списка:\n'
                                      '1. Мужская одежда\n'
                                      '2. Женская одежда\n'
                                      '3. Детская одежда\n'
                                      '4. Акссесуары\n')
    bot.register_next_step_handler(message, getCategories)


def getCategories(message):
    try:
        gender_id = int(message.text)
        if gender_id < 1 or gender_id > 4:
            bot.send_message(message.chat.id, 'Введите только целое число от 1 до 4!')
            bot.register_next_step_handler(message, getCategories)
        response = requests.get(url=f"{os.environ.get('BACK_URL')}/api/category_by_gender?id={gender_id}")
        data = response.json()
        text = "Выберите подкатегорию из списка:\n"
        for elem in data:
            text += f"{elem['id']}. {elem['name']}\n"
        bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(message, getProducts)
    except ValueError:
        bot.send_message(message.chat.id, 'Введите только целое число от 1 до 4!')
        bot.register_next_step_handler(message, getCategories)


def getProducts(message):
    try:
        category_id = int(message.text)
        response = requests.get(url=f"{os.environ.get('BACK_URL')}/api/products_by_category?id={category_id}")
        if response.status_code == 500:
            bot.send_message(message.chat.id, 'Введите только целое число из списка!')
            bot.register_next_step_handler(message, getProducts)
        data = response.json()
        text = "Выберите товар из списка:\n"
        for elem in data:
            text += (f"{elem['id']}. {elem['name']} - {elem['brand']['name']}\n"
                     f"{os.environ.get('BACK_URL')}{elem['thumb']}\n")
        bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(message, getProduct)
    except ValueError:
        bot.send_message(message.chat.id, 'Введите только целое число из списка!')
        bot.register_next_step_handler(message, getProducts)


def getProduct(message):
    try:
        product_id = int(message.text)
        response = requests.get(url=f"{os.environ.get('BACK_URL')}/api/product_detail?id={product_id}")
        if response.status_code == 500:
            bot.send_message(message.chat.id, 'Введите только целое число из списка!')
            bot.register_next_step_handler(message, getProduct)
        data = response.json()
        images = ''
        for elem in data['images']:
            images += f"{os.environ.get('BACK_URL')}{elem['image']}\n"
        text = (f"Название: {data['name']}\n"
                f"Описание: {data['description']}\n\n"
                f"Цена: {data['price']}\n"
                f"Бренд: {data['brand']['name']}\n"
                f"Фото: {os.environ.get('BACK_URL')}{data['thumb']}\n"
                f"Другие фото: {images}")
        bot.send_message(message.chat.id, text)
    except ValueError:
        bot.send_message(message.chat.id, 'Введите только целое число из списка!')
        bot.register_next_step_handler(message, getProduct)


bot.polling(non_stop=True, interval=0)
