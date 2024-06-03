import logging
import pyautogui
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from telegram import ReplyKeyboardMarkup, Update
import re
import os
from datetime import datetime
import configparser
import pathlib

log_dir = ""
prison_dir = ""
commands_dir = ""
a = 0

set_folders = []
flag_alarm = True

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

reply_keyboard = [
    ["LOG", "FULL_LOG"],
    ["SHOT"]
]

users = [124768943, 799070257]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def read_config():
    sect = "general"
    config = configparser.ConfigParser()
    fn = "./config.ini"
    res = config.read(fn)

    if len(res) == 0:
        print(f"check {fn} file")
        exit(-1)

    sections = config.sections()

    if sect not in sections:
        print(f"no section in config file. section = {sect}")
        print(sections)
        exit(-1)

    s_log_dir = "log_dir"
    s_prison_dir = "prison_dir"
    s_commands_dir = "commands_dir"
    for i in s_log_dir, s_prison_dir, s_commands_dir:
        if i not in config[sect]:
            print(f"check {fn} file: {i}")
            exit(-1)

    log_dir = config[sect][s_log_dir]
    prison_dir = config[sect][s_prison_dir]
    commands_dir = config[sect][s_commands_dir]

    print(log_dir, prison_dir, commands_dir, sep="\n")

async def create_command(update: Update, context: ContextTypes.DEFAULT_TYPE, text = "") -> None:
    l = text.split("")
    print(l)
    if l != 2 or "comm" not in l[0]:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="bad command")
        return
    fn = commands_dir + f'\\{l[1]}'
    file = pathlib.Path(fn)
    if not file.exists():
        f = open(fn, 'tw', encoding='utf-8')
        f.close()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"create command [{l[1]}]")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"command already exist")



async def make_log(update: Update, context: ContextTypes.DEFAULT_TYPE, count=15, full = False) -> None:
    global log_dir
    current_time = datetime.now()
    filename = log_dir + f'\\log_{current_time.strftime(" %d.%m.%Y")}.log'
    print(filename)

    if not full:
        current_time = datetime.now()
        filename = log_dir + f'\\log_{current_time.strftime(" %d.%m.%Y")}.log'
        print(filename)
        text = ""

        with open(filename, 'r') as file:
            text = "".join(list(file.readlines()[-count:]))
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    else:
        with open(filename, 'rb') as text_file:
            await context.bot.send_document(chat_id=update.effective_chat.id, document=text_file, filename='full.log')

                                                                                                                                          
async def make_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE, full=False) -> None:
    screenshot = pyautogui.screenshot()
    fn = r'C:\Users\templocaladmin\PycharmProjects\tbot\tbot\screenshot.png'
    screenshot.save(fn)

    if not full:
        with open(fn, 'rb') as photo:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
    else:
        with open(fn, 'rb') as file:
            await context.bot.send_document(chat_id=update.effective_chat.id, document=file, filename='photo.jpg')


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    content = os.listdir(prison_dir)
    global set_folders
    new_set_folders = set([folder for folder in content if os.path.isdir(os.path.join(prison_dir, folder))])

    diff = new_set_folders - set_folders
    set_folders = new_set_folders
    if len(diff) > 0:
        for user in users:
            await context.bot.send_message(user, text=str(diff))



async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    global flag_alarm

    if chat_id not in users:
        return

    text = update.message.text.lower()

    if "fshot" in text :
        await make_screenshot(update, context, full=True)
    elif "shot" in text:
        await make_screenshot(update, context)
    elif "fulllog" in text:
        await make_log(update, context, full=True)
    elif "log" in text:
        integer_value = 10
        try:
            integer_value = int(''.join(re.findall(r'\d+', text)))
        except ValueError:
            pass
        await make_log(update, context, count=integer_value)
    elif "comm" in text:
        await  create_command(update, context, text)


    # await update.message.reply_text("нажми на кнопку :)", reply_markup=markup, )

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
    read_config()
    main()
