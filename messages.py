import asyncio
import json
import re
import shutil
from datetime import datetime
import time
import pathlib
import os
import config

import pyautogui
from PIL import Image
from telegram.ext import ContextTypes



short_to_full = {
    "kil": "Зелье Киллера",
    "pob": "Зелье Победителя",
    "med": "Зелье Медика",
    "agt": "Зелье Агента",
    "ser": "Серная кислота",
}

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
    fn = config.commands_dir + f'\\{l[1]}'

    print(fn)

    file = pathlib.Path(fn)
    if not file.exists():
        f = open(fn, 'tw', encoding='utf-8')
        f.close()
        await context.bot.send_message(chat_id=chat_id, text=f"create command [{l[1]}]")
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"command already exist")

async def make_history(chat_id, context: ContextTypes.DEFAULT_TYPE) -> None:
    l_dir = config.log_dir
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
                filename = l_dir + f'\\{current_time.strftime("%d.%m.%Y")}_A{i}.sold'

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
    l_dir = config.log_dir

    fn = l_dir + f'/inventory.ah'
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
    l_dir = config.log_dir
    current_time = datetime.now()
    text = "sold:"
    print("make_sum")
    ss = 0
    all_a = eval("{'agt':0, 'med':0, 'kil':0, 'pob':0,'ser':0}")

    for i in range(1, workers):
        try:
            filename = l_dir + f'\\{current_time.strftime("%d.%m.%Y")}_A{i}.sold'

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
        f_list.append(dir + f'\\A{i}.ah')

    s_f = l_dir + f'\\storage.ah'
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
    filename = l_dir + f'\\money.txt'
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

    fn = config.config_json

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

async def make_conf_buyer(chat_id, context: ContextTypes.DEFAULT_TYPE) -> None:
    fn = config.config_json

    # Проверка существования файла
    if not os.path.isfile(fn):
        text = f"file not found: {fn}"
        await context.bot.send_message(chat_id=chat_id, text=text)
        return

    try:
        with open(fn, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        text = f"error parse json: {e}"
        await context.bot.send_message(chat_id=chat_id, text=text)
        return
    # Проверка структуры
    if not isinstance(data, dict) or "autobuy" not in data:
        print("Файл не содержит ключа 'autobuy'.")
        text = f"error parse json: no autobuy key"
        await context.bot.send_message(chat_id=chat_id, text=text)
        return

    autobuy = data["autobuy"]

    lines = []
    for short, full_name in short_to_full.items():
        item = autobuy.get(full_name)
        if not item:
            continue
        price = item.get("buyPrice")
        if not isinstance(price, (int, float)):
            lines.append(f"Некорректная цена для '{full_name}': {price}")
            continue
        lines.append(f"{short}: {price / 1_000_000:.1f}")

    await context.bot.send_message(chat_id=chat_id, text="\n".join(lines), parse_mode='Markdown')

async def set_conf(chat_id, context: ContextTypes.DEFAULT_TYPE, text="") -> None:
    prison_dir = config.prison_dir
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

async def set_conf_buyer(chat_id, context: ContextTypes.DEFAULT_TYPE, text="") -> None:
    fn = config.config_json  # path to autobuy.json

    parts = text.strip().split()

    if len(parts) != 2 or parts[0].lower() != "setconf":
        await context.bot.send_message(
            chat_id=chat_id,
            text="Invalid command format.\nExample: `setconf ser=4.5`",
            parse_mode='Markdown'
        )
        return

    command = parts[1]

    if not re.fullmatch(r"^[a-z]{3}=[0-9]+([.,][0-9]+)?$", command):
        await context.bot.send_message(chat_id=chat_id, text="Invalid format.\nExample: `setconf ser=4.5`", parse_mode='Markdown')
        return

    key, val = command.split("=")
    key = key.lower()
    val = val.replace(",", ".")

    try:
        cost = int(float(val) * 1_000_000)
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="Invalid price value.")
        return

    if cost < 100_000 or cost > 11_000_000:
        await context.bot.send_message(chat_id=chat_id, text="Price must be between 0.1 and 11.0 million.")
        return

    if key not in short_to_full:
        await context.bot.send_message(chat_id=chat_id, text=f"Unknown item code: `{key}`", parse_mode='Markdown')
        return

    full_name = short_to_full[key]

    try:
        with open(fn, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"Failed to read JSON: {e}")
        return

    if "autobuy" not in data or not isinstance(data["autobuy"], dict):
        await context.bot.send_message(chat_id=chat_id, text="Invalid JSON structure: 'autobuy' key missing.")
        return

    if full_name not in data["autobuy"]:
        await context.bot.send_message(chat_id=chat_id, text=f"Item '{full_name}' not found in JSON.")
        return

    backup_fn = fn + ".bak"
    try:
        shutil.copyfile(fn, backup_fn)
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"Could not create backup: {e}")
        return

    data["autobuy"][full_name]["buyPrice"] = cost
    temp_fn = fn + ".tmp"

    try:
        with open(temp_fn, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        with open(temp_fn, "r", encoding="utf-8") as f:
            json.load(f)

        shutil.move(temp_fn, fn)

        await make_conf_buyer(chat_id, context)

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"Write error: {e}\nRestoring backup...")
        if os.path.exists(backup_fn):
            shutil.copyfile(backup_fn, fn)
        if os.path.exists(temp_fn):
            os.remove(temp_fn)


async def make_log(chat_id, context: ContextTypes.DEFAULT_TYPE, count=30, full=False) -> None:
    l_dir = config.log_dir
    current_time = datetime.now()
    filename = l_dir + f'/log_{current_time.strftime("%d.%m.%Y")}.log'
    print(filename)

    if not full:
        current_time = datetime.now()
        filename = l_dir + f'/log_{current_time.strftime("%d.%m.%Y")}.log'
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
    l_dir = config.log_dir

    fn = text.replace("get", "").replace(" ", "")

    filename = l_dir + f'/{fn}'
    name = fn.split("/")[-1]
    print(filename)
    try:
        with open(filename, 'rb') as text_file:
            await context.bot.send_document(chat_id=chat_id, document=text_file, filename=name)
            return
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f'err {e}')

async def make_ss(chat_id, context: ContextTypes.DEFAULT_TYPE, text) -> None:
    l_dir = config.log_dir

    dir_ss = l_dir + "\\ss"

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
    l_dir = config.log_dir
    dir_ss = l_dir + "\\ss"
    crop_file = l_dir + "/cropped_money.png"

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
    l_dir = config.log_dir
    dir_ss = os.path.join(l_dir, "ss")

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
    l_dir = config.log_dir
    dir_ss = l_dir

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

    filename = l_dir + f'/money.txt'
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

