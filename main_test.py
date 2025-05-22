import logging

from telegram.ext import Application, ContextTypes, MessageHandler, filters
from telegram import ReplyKeyboardMarkup, Update
import configparser
import subprocess
import sys
import os
import asyncio
from telegram.ext import Application
from telegram import Update
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

log_dir = ""
prison_dir = ""
commands_dir = ""
except_dir = ""
token = ""
a = 0
workers = 7 + 1
isBuyer = False

set_folders_prison = set()
set_folders_except = set()
flag_alarm = True

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

reply_keyboard = [
    ["LOG", "FULL_LOG"],
    ["SHOT"]
]

martin = 799070257
andrei = 124768943
users = [andrei, martin]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def read_config(name):
    global prison_dir
    global log_dir
    global commands_dir
    global except_dir
    global token
    sect = "general"
    config = configparser.ConfigParser()
    fn = "./config" + name + ".ini"
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
    s_except_dir = "except_dir"
    s_token = "token"

    print(s_log_dir)
    for i in s_log_dir, s_prison_dir, s_commands_dir, s_except_dir, s_token:
        if i not in config[sect]:
            print(f"check {fn} file: {i}")
            exit(-1)

    log_dir = config[sect][s_log_dir]
    prison_dir = config[sect][s_prison_dir]
    commands_dir = config[sect][s_commands_dir]
    except_dir = config[sect][s_except_dir]
    token = config[sect][s_token]

    print(log_dir, prison_dir, commands_dir, except_dir, token, sep="\n")




def get_last_commit_message() -> str:
    result = subprocess.run(
        ['git', 'log', '-1', '--pretty=%h [%cd]', '--date=format:%Y-%m-%d %H:%M:%S'],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()



async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    global flag_alarm

    if chat_id not in users:
        return
    text = update.message.text.lower()

    print(f"new message: {text}")

    await context.bot.send_message(chat_id=chat_id, text=get_last_commit_message())


def main() -> None:
    global prison_dir
    global set_folders_except
    global set_folders_prison
    global token
    global log_dir
    global isBuyer

    content = os.listdir(prison_dir)
    set_folders_prison = set([folder for folder in content if os.path.isdir(os.path.join(prison_dir, folder))])

    content = os.listdir(except_dir)
    set_folders_except = set([folder for folder in content if os.path.isfile(os.path.join(except_dir, folder))])

    app = Application.builder().token(token).build()

    loop = asyncio.get_event_loop()
    observer = Observer()
    observer.schedule(NewFileHandler(app.bot, loop),
                      path="/home/andreysokolov/project/minecraft/share/capcha",
                      recursive=False)
    observer.start()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


class NewFileHandler(FileSystemEventHandler):
    def __init__(self, bot, loop):
        self.bot = bot
        self.loop = loop  # loop Telegram Application'а

    def on_created(self, event):
        if not event.is_directory:
            asyncio.run_coroutine_threadsafe(
                self.notify(event.src_path),
                self.loop
            )

    async def notify(self, filepath):
        filename = Path(filepath).name
        if filename.startswith(".#"):
            return  # игнорировать временные файлы

        print("file")
        await self.bot.send_message(chat_id=andrei, text=f"Появился файл: {filename}")


if __name__ == "__main__":
    name = ""
    if len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg == '-b':
            name = "_buyer"
        elif arg == '-d':
            name = "_dev"
        else:
            print(f'undefine arg {arg}. use "-b" or "-d" or empty ')
            exit(-1)
    print(name)
    read_config(name)
    main()
