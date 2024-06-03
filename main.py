import logging
import pyautogui
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from telegram import ReplyKeyboardMarkup, Update
import re
from telegram import InputFile
import os
from datetime import datetime

log_dir = r"C:\Users\templocaladmin\PycharmProjects\mine_bot\logs"
prison_dir = r"C:\Users\templocaladmin\PycharmProjects\mine_bot\png"
a = 0

set_folders = []
flag_alarm = True

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.CRITICAL
)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

reply_keyboard = [
    ["LOG", "FULL_LOG"],
    ["SHOT"]
]

users = [124768943, 799070257]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


async def make_log(update: Update, context: ContextTypes.DEFAULT_TYPE, count=15) -> None:
    global log_dir
    current_time = datetime.now()
    filename = log_dir + f'\\log_{current_time.strftime(" %d.%m.%Y")}.log'
    print(filename)
    text = ""
    with open(filename, 'r') as file:
        text = "".join(list(file.readlines()[-count:]))

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

                                                                                                                                          
async def make_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("shot")
    screenshot = pyautogui.screenshot()
    print("shot1")
    fn = r'C:\Users\templocaladmin\PycharmProjects\tbot\tbot\screenshot.png'
    screenshot.save(fn)
    print("shot2")
    with open(fn, 'rb') as photo:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)

    with open(fn, 'rb') as photo_file:
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

    text = update.message.text.lower()

    if text == "shot":
        await make_screenshot(update, context)
        await make_log(update, context, count=1)
    elif "log" in text:
        integer_value = 10
        try:
            integer_value = int(''.join(re.findall(r'\d+', text)))
        except ValueError:
            pass

        await make_log(update, context, count=integer_value)

    await update.message.reply_text("", reply_markup=markup )

    if flag_alarm:
        context.job_queue.run_repeating(alarm, 1, chat_id=chat_id, name=str(chat_id))
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
