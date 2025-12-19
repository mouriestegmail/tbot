from time import sleep

from watchdog.events import FileSystemEventHandler
from pathlib import Path
import asyncio
import os
import time
import re
# from datetime import datetime

import config
import messages


class NewFileHandler(FileSystemEventHandler):
    def __init__(self, bot, loop):
        self.bot = bot
        self.loop = loop  # loop Telegram Application'а

    def on_moved(self, event):
        print("on_moved", event.dest_path)
        if event.is_directory:
            return

        fut = asyncio.run_coroutine_threadsafe(
            self.notify(event.dest_path),
            self.loop
        )
        # try:
        #     fut.result()
        # except Exception as e:
        #     print(f"[Ошибка notify moved] {e}")

    def on_created(self, event):
        print("on_created", event.src_path)
        if event.is_directory:
            return  # игнорируем директории

        # Игнорируем временные файлы *.tmp
        if event.src_path.endswith("tmp"):
            return




        # запускаем корутину в loop
        fut = asyncio.run_coroutine_threadsafe(
            self.notify(event.src_path),
            self.loop
        )
        # try:
        #     fut.result()  # покажет ошибку прямо в консоли
        # except Exception as e:
        #     print(f"[Ошибка в notify] {e}")

    async def notify(self, filepath):
        filepath = Path(filepath)  # ← вот это добавь
        name = filepath.name

        is_mute = "mute" in name

        print(filepath)

        if self.is_input_file(filepath):

            chat_id = None
            try:
                # chat_id — первая часть имени файла
                chat_id_str = filepath.stem
                print(chat_id_str)
                text = filepath.read_text(encoding="utf-8")
                chat_id = int(chat_id_str)

                await self.read_input_file(text, chat_id)

            except Exception as e:
                print(f"[Error notify] {e}")
                if chat_id is None:
                    return
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=e,
                    parse_mode='Markdown'
                )

            filepath.unlink()
            return

        elif self.is_reply_file(filepath):

            list_attr = filepath.stem.split(".")
            i = 0

            flag_delete = False
            flag_mute = True
            chat_id_str = ""


            for attr in list_attr:
                if i == 0:
                    chat_id_str = filepath.stem
                if i == 1:
                    pass # all message is text. yet
                if i == 2:
                    flag_delete = attr == "del"
                if i == 3:
                    flag_mute = attr == "mute"
                i += 1

            print(chat_id_str, flag_delete, flag_mute, i)

            if chat_id_str == "":
                return

            print(12345)

            text = filepath.read_text(encoding="utf-8")
            text += f"\nреплай, что бы сохранить \n >"
            chat_id = int(chat_id_str)
            for i in 2,3,4,5,6:
                try:
                    msg = await self.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown', disable_notification=flag_mute)
                    del_dir = "./delete_file/"
                    if flag_delete:
                        fn = f"{del_dir}{msg.message_id}.del"
                        open(fn, 'w', encoding="utf-8")
                        # удалим этот файл по реплаю

                    now = time.time()
                    intervale = 5 * 60
                    for f in os.listdir(del_dir):
                        path = Path(del_dir) / f
                        if not path.is_file():
                            continue

                        if now - path.stat().st_mtime > intervale:
                            path.unlink()

                    return
                except Exception as e:
                    text += ">"*i
                    await asyncio.sleep(0.5)

        if name.startswith(".#"):
            return
        if self.is_time_file(str(filepath)):
            print("time")
            await self.handler_time()
            if filepath.is_file():
                filepath.unlink()
        elif self.is_img_file(filepath):
            print("png")
            sleep(2)
            str_path = str(filepath)
            if "photo" in str_path:
                for id_chat in [config.andrei, config.martin]:
                    with open(filepath, 'rb') as photo:
                        await self.bot.send_photo(chat_id=id_chat, photo=photo, caption=name, disable_notification=is_mute)
                return
            await self.bot.send_document(chat_id=config.andrei, document=str(filepath), filename=name, disable_notification=is_mute)
            return
        elif self.is_err_file(str(filepath)):
            print("err")
            await self.bot.send_message(chat_id=config.martin, text=f"{name}", disable_notification=is_mute)
            await self.bot.send_message(chat_id=config.andrei, text=f"{name}", disable_notification=is_mute)
            return
        else:
            print("else")
            await self.bot.send_message(chat_id=config.bot_connect_group, text=f"Появился файл: {name}", disable_notification=is_mute)

    async def read_input_file(self, text, chat_id):
        if "flog" in text:
            await messages.make_full_log(chat_id=chat_id, bot=self.bot)
        elif "log" in text:
            integer_value = 20
            try:
                integer_value = int(''.join(re.findall(r'\d+', text)))
            except ValueError:
                pass
            messages.make_log(chat_id=chat_id, count=integer_value, text=text)
        elif "sum" in text:
            messages.make_sum(chat_id=chat_id)
        elif "day" in text:
            messages.make_day(chat_id, text)

        return None

    def is_input_file(self, file: Path):
        return file.suffix.lower() in ".input"

    def is_reply_file(self, file: Path):
        return file.suffix.lower() in ".reply"

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
