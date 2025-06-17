from time import sleep

from watchdog.events import FileSystemEventHandler
from pathlib import Path
import asyncio
import os
import time
# from datetime import datetime

import config


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
        name = Path(filepath).name
        if name.startswith(".#"):
            return  # игнорировать временные файлы
        if self.is_time_file(filepath):
            await self.handler_time()
            if os.path.isfile(filepath):
                os.remove(filepath)
        elif self.is_img_file(filepath):
            await self.bot.send_document(chat_id=config.andrei, document=filepath, filename=name)
            return

        elif self.is_err_file(filepath):
            await self.bot.send_message(chat_id=config.martin, text=f"{name}")
            await self.bot.send_message(chat_id=config.andrei, text=f"{name}")
            return
        else:
            await self.bot.send_message(chat_id=config.bot_connect_group, text=f"Появился файл: {name}")
            return

    def is_img_file(self, file: Path) -> bool:
        return file.suffix.lower() in (".png", ".jpg", ".jpeg")

    def is_time_file(self, file):
        return "time" in file
    def is_err_file(self, file):
        return "err" in file

    async def handler_time(self):
        watched_key = ["med", "pob"]

        s_f = config.log_dir + '/storage.ah'
        i_f = config.log_dir + '/inventory.ah'

        i_apples = self.read_ah_file(i_f)
        s_apples = self.read_ah_file(s_f)

        for key in watched_key:
            value = s_apples.get(key, 0)
            value += i_apples.get(key,0)

            if value < 10:
                print(f"wb++{key}")
                await self.bot.send_message(chat_id=config.bot_connect_group, text=f"wb++{key}")
            if value > 40:
                print(f"b--{key}")
                await self.bot.send_message(chat_id=config.bot_connect_group, text=f"b--{key}")

            if value > 70:
                print(f"wb--{key}")
                await self.bot.send_message(chat_id=config.bot_connect_group, text=f"wb--{key}")

            sleep(1)




    def read_ah_file(self, fn):
        if not self.is_file_recent(fn):
            return None
        try:
            with open(fn, 'r') as file:
                first_line = file.readline().strip()
                apples = eval(first_line)

                return apples
        except Exception as e:
            print(f"except: {e}")
        return "\nNo data"



    def is_file_recent(self, fn ):
        max_age_minutes = 30
        if not os.path.isfile(fn):
            print(f"Файл {fn} не найден.")
            return False

        mtime = os.path.getmtime(fn)
        age_seconds = time.time() - mtime

        if age_seconds > max_age_minutes * 60:
            print(f"Файл {fn} старше {max_age_minutes} минут.")
            return False

        return True
