import asyncio
import json
import re
import shutil
from datetime import datetime
import time
import pathlib
import os

import pyautogui
from PIL import Image
from telegram.ext import ContextTypes


log_dir = ""
prison_dir = ""
commands_dir = ""
except_dir = ""
token = ""

workers = 7 + 1

def split_text_into_chunks(text: str, lines_per_chunk: int = 30) -> list:
    lines = text.splitlines()
    chunks = [lines[i:i + lines_per_chunk] for i in range(0, len(lines), lines_per_chunk)]
    chunks = ['\n'.join(chunk) for chunk in chunks]
    return chunks

def format_text(text):
    text = text.replace('agt', 'a')
    text = text.replace('med', 'm')
    text = text.replace('pob', 'p')
    text = text.replace('ser', 's')
    text = text.replace('kil', 'k')
    text = text.replace("'", "")
    text = "```log\n" + text + "\n```"
    print(text)
    return text

    print(text)

    lines = [line for line in text.strip().split('\n') if line]

    formatted_lines = []
    flag = False
    for line in lines:
        if 'AH' in line:
            flag = True
        if '{' in line and '}' in line:
            line = re.sub(r'\s+', ' ', line.strip())
            match = re.match(r"(\{.*\})\s+(\d+)", line)
            if match:
                l = line
                if flag or len(l) > 35:
                    l = l.replace(': ', ':')
                if len(l) > 35:
                    l = l.replace(', ', ',')
                print(f"l :[{l}]")
                formatted_lines.append(l)

            else:
                line = line.replace(': ', ':')
                if len(line) > 35:
                    line = line.replace(', ', ',')

                formatted_lines.append(line)
        else:
            formatted_lines.append(line)

    return '\n'.join(formatted_lines)

async def create_command(chat_id, context: ContextTypes.DEFAULT_TYPE, text="") -> None:
    l = text.split(" ")
    print(l)
    if len(l) != 2 or "comm" not in l[0]:
        await context.bot.send_message(chat_id=chat_id, text="bad command")
        return
    fn = commands_dir + f'\\{l[1]}'

    print(fn)

    file = pathlib.Path(fn)
    if not file.exists():
        f = open(fn, 'tw', encoding='utf-8')
        f.close()
        await context.bot.send_message(chat_id=chat_id, text=f"create command [{l[1]}]")
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"command already exist")

async def make_history(chat_id, context: ContextTypes.DEFAULT_TYPE) -> None:
    global log_dir
    from datetime import datetime, timedelta

    print("make_history")

    today = datetime.now()  # Текущая дата и время
    for i in range(14):
        text = ""
        ss = 0
        current_time = today - timedelta(days=i)
        text = current_time.strftime('%d-%m-%Y')

        all_a = eval("{'agt':0, 'kil':0, 'med':0,'pob':0,'ser':0}")

        for i in range(1, workers):
            try:
                filename = log_dir + f'\\{current_time.strftime("%d.%m.%Y")}_A{i}.sold'

                with open(filename, 'r') as file:
                    first_line = file.readline().strip()
                    apples = eval(first_line)
                    apples = dict(sorted(apples.items()))
                    s = 0
                    for k, v in apples.items():
                        s += v
                        all_a[k] += v
                    ss += s
                    if first_line:
                        text += "\n" + str(apples).replace(" ", "") + f' {s}'
            except Exception as e:
                text += "\n err"
        text += f'\n\n{str(all_a).replace(" ", "")}  {ss}\n\nAH:'

        text = format_text(text)

        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')

def create_inventory_log() -> str:
    global log_dir

    fn = log_dir + f'/inventory.ah'
    try:
        with open(fn, 'r') as file:
            first_line = file.readline().strip()
            apples = eval(first_line)
            apples = dict(sorted(apples.items()))
            s = sum(apples.values())
            print(apples)
            return f"\ninventory:\n{str(apples)} {s}"
    except Exception as e:
        print(f"except: {e}")
    return "\nNo data"

async def make_sum(chat_id, context: ContextTypes.DEFAULT_TYPE) -> None:
    global log_dir
    current_time = datetime.now()
    text = "sold:"
    print("make_sum")
    ss = 0
    all_a = eval("{'agt':0, 'med':0, 'kil':0, 'pob':0,'ser':0}")

    for i in range(1, workers):
        try:
            filename = log_dir + f'\\{current_time.strftime("%d.%m.%Y")}_A{i}.sold'

            with open(filename, 'r') as file:
                first_line = file.readline().strip()
                apples = eval(first_line)
                apples = dict(sorted(apples.items()))

                s = 0
                for k, v in apples.items():
                    s += v
                    all_a[k] += v
                ss += s
                # text += "\n" + str(apples)
                if first_line:
                    text += "\n" + str(apples).replace(" ", "") + f' {s}'
        except Exception as e:
            print(e)
            text += "\n err"
    text += (f"\nsumm:"
             f'\n{str(all_a).replace(" ", "")}  {ss}\nAH:')

    f_list = []
    for i in range(1, workers):
        f_list.append(log_dir + f'\\A{i}.ah')

    s_f = log_dir + f'\\storage.ah'
    f_list.append(s_f)
    ss = 0
    sum_dict = dict()
    for filename in f_list:
        try:
            with open(filename, 'r') as file:
                first_line = file.readline().strip()
                try:
                    apples = eval(first_line)
                    apples = dict(sorted(apples.items()))

                    s = 0
                    if first_line:
                        if filename == s_f:
                            text += "\nsumm:\n" + str(sum_dict).replace(" ", "") + f' {ss}' + "\nstorage:\n"
                        ah_max = "?"

                        last_modified_time = os.path.getmtime(filename)
                        current_time = time.time()
                        h = datetime.now().hour
                        delta_t = 60 * 5
                        if 1 < h < 9:
                            delta_t = 60 * 30

                        delta_t_real = current_time - last_modified_time

                        if delta_t_real <= delta_t:
                            for k, v in apples.items():
                                if k != 'z' and k != 'max':
                                    s += v
                                    ss += v
                                sum_dict[k] = sum_dict.get(k, 0) + v

                                if k == 'max':
                                    ah_max = str(v)
                            text += "\n" + str(apples).replace(" ", "").replace(": ", ":") + f' {s}'
                        else:
                            t = delta_t_real // 6 / 10
                            text += f"\ntimeout : {t}"
                        # text += p + "\n" + str(apples)
                except Exception as e:
                    print(e)
                    text += "\n" + first_line
        except Exception as e:
            text += "\n err"
    text += create_inventory_log()
    text += "\n"
    filename = log_dir + f'\\money.txt'
    with open(filename, 'r') as file:
        modification_time = os.path.getmtime(filename)
        modification_datetime = datetime.fromtimestamp(modification_time)
        current_datetime = datetime.now()
        time_difference = current_datetime - modification_datetime
        minutes_passed = time_difference.total_seconds() // 6 / 10

        text += "".join(list(file.readlines())) + "    " + str(minutes_passed) + "m"

    text = format_text(text)
    text = text.replace(" z:", "  ")
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')
    import shutil

    total, used, free = shutil.disk_usage("C:\\")

    await context.bot.send_message(chat_id=chat_id, text=f"free space: {free // (2 ** 30)} GB")
    make_money(chat_id, )

async def make_conf(chat_id, context: ContextTypes.DEFAULT_TYPE) -> None:
    global prison_dir
    fn = prison_dir + f'\\config.json'

    print(fn)

    with open(fn, "r") as f:
        data = json.load(f)

    lines = []
    for item in data["apples"]:
        name = item["name"]
        cost_mil = item["cost"] / 1_000_000
        lines.append(f"{name}: {cost_mil:.1f}")

    lines.append(f"\ninv: {data['max_inventory']}")

    text = "\n".join(lines)

    text = "```conf\n" + text + "\n```"
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')

async def set_conf(chat_id, context: ContextTypes.DEFAULT_TYPE, text="") -> None:
    global prison_dir
    fn = prison_dir + f'\\config.json'
    l = text.split(" ")
    print(fn, text)
    print(l)

    if len(l) != 2 or "setconf" not in l[0]:
        await context.bot.send_message(chat_id=chat_id, text="bad setconf")
        return

    command = l[1]

    # Проверка формата команды
    pattern = re.compile(r"^[a-z]+=.+$")
    if not pattern.fullmatch(command):
        await context.bot.send_message(chat_id=chat_id, text="Неверный формат команды. \nПример: setconf pob=4.3")
        return

    key, val = command.split("=")

    cost = int(float(val.replace(',', '.')) * 1_000_000)

    if cost < 100_000 or cost > 11_000_000:
        await context.bot.send_message(chat_id=chat_id,
                                       text="Неверное значение стоимости. [0-11]")
        return

    # Загрузка JSON
    try:
        with open(fn, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        await context.bot.send_message(chat_id=chat_id, text=f"Файл не найден: {fn}")
        return
    except json.JSONDecodeError as e:
        await context.bot.send_message(chat_id=chat_id, text=f"Ошибка разбора JSON: {e}")
        return
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"Ошибка при чтении: {e}")
        return

    # Проверка структуры
    if "apples" not in data or not isinstance(data["apples"], list):
        await context.bot.send_message(chat_id=chat_id,
                                       text="Ошибка: структура JSON некорректна — отсутствует список 'apples'")
        return

    # Обновление стоимости
    found = False
    for item in data["apples"]:
        if item.get("name") == key:
            item["cost"] = cost
            found = True
            break

    if not found:
        await context.bot.send_message(chat_id=chat_id,
                                       text=f"Элемент с именем '{key}' не найден в apples — файл не изменён")
        return

    # Создание резервной копии
    backup_filename = fn + ".bak"
    try:
        shutil.copyfile(fn, backup_filename)
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id,
                                       text=f"Не удалось создать резервную копию. Файл не будет изменён.\nОшибка: {e}")
        return

    # Запись во временный файл
    temp_filename = fn + ".tmp"
    try:
        with open(temp_filename, "w") as f:
            json.dump(data, f, indent=2)

        with open(temp_filename, "r") as f:
            json.load(f)  # проверка валидности

        shutil.move(temp_filename, fn)  # атомарная замена
        await make_conf(chat_id, context)

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id,
                                       text=f"Ошибка при записи. \nВосстановление из резервной копии... {e}")
        print("Ошибка при записи. Восстановление из резервной копии...")

        if os.path.exists(backup_filename):
            shutil.copyfile(backup_filename, fn)

        if os.path.exists(temp_filename):
            os.remove(temp_filename)

async def make_log(chat_id, context: ContextTypes.DEFAULT_TYPE, count=30, full=False) -> None:
    global log_dir
    current_time = datetime.now()
    filename = log_dir + f'/log_{current_time.strftime("%d.%m.%Y")}.log'
    print(filename)

    if not full:
        current_time = datetime.now()
        filename = log_dir + f'/log_{current_time.strftime("%d.%m.%Y")}.log'
        print(filename)
        try:
            with open(filename, 'r') as file:
                text = "".join(list(file.readlines()[-count:]))
            text = "```log\n" + text + "\n```"
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')
        except Exception as e:
            await context.bot.send_message(chat_id=chat_id, text=f"file open error {filename}")
    else:
        with open(filename, 'rb') as text_file:
            await context.bot.send_document(chat_id=chat_id, document=text_file, filename='full.log')

async def make_get_file(chat_id, context: ContextTypes.DEFAULT_TYPE, text) -> None:
    global log_dir

    fn = text.replace("get", "").replace(" ", "")

    filename = log_dir + f'/{fn}'
    name = fn.split("/")[-1]
    print(filename)
    try:
        with open(filename, 'rb') as text_file:
            await context.bot.send_document(chat_id=chat_id, document=text_file, filename=name)
            return
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f'err {e}')

async def make_ss(chat_id, context: ContextTypes.DEFAULT_TYPE, text) -> None:
    global log_dir

    dir_ss = log_dir + "\\ss"

    if not os.path.exists(dir_ss):
        await context.bot.send_message(chat_id=chat_id, text=f'[{dir_ss}] not exist')
        return

    folder = text.replace("ss", "").replace(" ", "")
    dir_worker = dir_ss + "/" + folder.upper()

    if not os.path.exists(dir_worker):
        await context.bot.send_message(chat_id=chat_id, text=f'[{dir_worker}] not exist')
        return

    files_list = []
    for f in os.listdir(dir_worker):
        full_path = os.path.join(dir_worker, f)
        if os.path.isfile(full_path):
            files_list.append(full_path)

    for fn in files_list:
        with open(fn, 'rb') as file:
            await context.bot.send_document(chat_id=chat_id, document=file, filename=file.name)
        await asyncio.sleep(0.5)

async def make_money(chat_id, context: ContextTypes.DEFAULT_TYPE) -> None:
    global log_dir
    dir_ss = log_dir + "\\ss"
    crop_file = log_dir + "/cropped_money.png"

    money = "money.png"
    name = "storage"

    fns = get_all_files(name, dir_ss)
    print(fns)

    latest_file = max(fns, key=os.path.getmtime)

    print(latest_file)
    try:
        dir_path = os.path.dirname(latest_file)
        print(dir_path)  # /some/long/path/to
    except Exception as e:
        print(e)

    latest_file = dir_path + "/money.png"

    print(latest_file)

    img = Image.open(latest_file)

    crop_box = (110, 370, 80 + 150, 360 + 100)
    cropped_img = img.crop(crop_box)

    cropped_img.save(crop_file)

    with open(crop_file, 'rb') as photo:
        await context.bot.send_photo(chat_id=chat_id, photo=photo)
        await asyncio.sleep(0.5)

def get_all_files(template: str, folder: str) -> list:
    res = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if template in file:
                res.append(os.path.join(root, file))

    return res

import os
import asyncio
from telegram.ext import ContextTypes

import os
import asyncio
from telegram.ext import ContextTypes

async def make_fn(chat_id, context: ContextTypes.DEFAULT_TYPE, text):
    global log_dir
    dir_ss = os.path.join(log_dir, "ss")

    name = text.replace("fn", "").replace(" ", "")
    fns = get_all_files(name, dir_ss)

    # сортировка по имени родительской папки
    fns = sorted(fns, key=lambda fn: os.path.basename(os.path.dirname(fn)))

    for fn in fns:
        try:
            folder_name = os.path.basename(os.path.dirname(fn))
            with open(fn, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=folder_name,
                    parse_mode='HTML'
                )
            await asyncio.sleep(0.5)
        except Exception as e:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"<b>Error sending file:</b> <code>{fn}</code>",
                parse_mode='HTML'
            )



async def make_time(chat_id, context: ContextTypes.DEFAULT_TYPE):
    global log_dir
    dir_ss = log_dir

    text = "```time\n"

    for i in range(1, workers):
        name = f"A{i}"
        fn = f'{dir_ss}/{name}.time'

        try:
            with open(fn, 'r') as file:
                items = file.readline().split(" ")
                t = float(items[0].replace(" ", ""))
                c = items[1]
                cur_t = time.time()
                diff = (cur_t - t) // 6 / 10

                text += f'{name}: {diff}m  [{c.strip()}]\n'
        except Exception as e:
            print(e)
            text += f'{name}: err \n'

    filename = log_dir + f'/money.txt'
    with open(filename, 'r') as file:
        text += "".join(list(file.readlines()))
    text += "```"
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')

async def make_screenshot(chat_id, context: ContextTypes.DEFAULT_TYPE, full=False) -> None:
    try:
        screenshot = pyautogui.screenshot()
        fn = '../screenshot.png'
        screenshot.save(fn)
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=str(e))
        return


    if not full:
        with open(fn, 'rb') as photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo)
    else:
        with open(fn, 'rb') as file:
            await context.bot.send_document(chat_id=chat_id, document=file, filename='photo.jpg')

