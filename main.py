import logging
import pyautogui
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from telegram import ReplyKeyboardMarkup, Update
import io
from telegram import InputFile
import os

prison_dir = "/home/dev/tmp/"
set_folders = []
flag_alarm = True

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.CRITICAL
)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

reply_keyboard = [
    ["LOG"
     , "SHOT"]
]

users = [124768943, 799070257]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

async def make_log(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text_file_path = "/home/dev/Pictures/log.txt"
    with open(text_file_path, 'r') as text_file:
        text = text_file.read()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def make_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    screenshot = pyautogui.screenshot()

    # Сохраняем скриншот в файл
    screenshot.save('screenshot.png')

    photo_path = "screenshot.png"
    # Отправка изображения
    with open(photo_path, 'rb') as photo:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)

    with open(photo_path, 'rb') as photo_file:
        await context.bot.send_document(chat_id=update.effective_chat.id,
                                        document=photo_file,
                                        filename='photo.jpg')

async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    content = os.listdir(prison_dir)
    # Фильтруем только папки
    global set_folders
    new_set_folders = set([folder for folder in content if os.path.isdir(os.path.join(prison_dir, folder))])

    diff = new_set_folders - set_folders
    set_folders = new_set_folders
    if len(diff) > 0:
        for id in users:
            await context.bot.send_message(id, text=str(diff))

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    global flag_alarm

    if chat_id not in users:
        return

    if update.message.text.lower() == "shot":
        await make_screenshot(update, context)
    elif update.message.text.lower() == "log":
        await make_log(update, context)
    await update.message.reply_text(
        "нажми на кнопку :)", reply_markup=markup, )



    if flag_alarm:
        context.job_queue.run_repeating(alarm, 10, chat_id=chat_id, name=str(chat_id))
        flag_alarm = False



def main() -> None:
    content = os.listdir(prison_dir)
    global set_folders
    set_folders = set([folder for folder in content if os.path.isdir(os.path.join(prison_dir, folder))])


    application = Application.builder().token("7390205437:AAFKGhDIVlyGlkknUaIQx4L0vEp-ukm9eFM").build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
