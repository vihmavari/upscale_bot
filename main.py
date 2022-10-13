import os
import time
import subprocess
from pathlib import Path
from PIL import Image
import telebot

TOKEN = '5506670345:AAGKCVsSJMZY8BZyaHu0nNh1RCyipAeLudM'

bot = telebot.TeleBot(TOKEN, parse_mode=None)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Just send an image that you want to upscale.")


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "This bot can only work with images less than 276000 pixels.\n" +
                                      "Also, please upload your images as a document.")


@bot.message_handler(content_types=["document"])
def get_image_messages(message):
    bot.reply_to(message, "Wait a minute...")

    # информация о присланном документе (изображении)
    file_name = message.document.file_name
    file_id = message.document.file_id
    file_id_info = bot.get_file(file_id)

    downloaded_file = bot.download_file(file_id_info.file_path)

    # скачиваем присланный файл
    with open("./ESRGAN/LR/" + file_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    sent_file = Path('./ESRGAN/LR/' + file_name)
    while not sent_file.is_file():
        time.sleep(2)

    # проверка на возможность обработки
    try:
        sent_image = Image.open(sent_file)
    except():
        bot.send_message(message.chat.id, "Error: Not an image")
        os.remove('./ESRGAN/LR/' + file_name)
        return None

    if (sent_image.size[0] * sent_image.size[1]) > 276000:
        sent_image.close()
        bot.send_message(message.chat.id, "Error: Image is too big")
        os.remove('./ESRGAN/LR/' + file_name)
        return None

    sent_image.close()

    # обработка присланного изображения с помощью нейросети
    bot.send_message(message.chat.id, "Picture is upscaling now...")

    command = "cd ESRGAN && python test.py"
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    while (p.wait() != 0):
        time.sleep(2)

    # отправляем картинку с разрешением увеличенным в 4 раза
    upgraded_file_name = file_name[:file_name.find('.')]
    upgraded_file = open('./ESRGAN/results/' + upgraded_file_name + '_rlt.png', "rb")

    bot.send_document(message.chat.id, upgraded_file)
    upgraded_file.close()

    # чистим папки с изображениями
    os.remove('./ESRGAN/results/' + upgraded_file_name + '_rlt.png')
    os.remove('./ESRGAN/LR/' + file_name)


bot.infinity_polling()
