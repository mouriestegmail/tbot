import logging
import time

import pyautogui
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from telegram import ReplyKeyboardMarkup, Update
import re
import os
from datetime import datetime
import configparser
import pathlib
import asyncio
import subprocess

log_dir = ""
prison_dir = ""
commands_dir = ""
except_dir = ""
token = ""
a = 0

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


def read_config():
    global prison_dir
    global log_dir
    global commands_dir
    global except_dir
    global token
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

import re

def format_text(text):
    text = text.replace('agt', 'a')
    text = text.replace('med', 'm')
    text = text.replace('pob', 'p')
    text = text.replace('ser', 's')
    text = text.replace('kil', 'k')
    text = text.replace("'", "")
    text = "```log\n" + text + "\n```"

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
                dictionary_part = match.group(1)
                number_part = match.group(2)
                pairs = re.findall(r'(\w:)(\d+)', dictionary_part)
                formatted_pairs = ', '.join(f"{key}{int(value):2}" for key, value in pairs)
                formatted_dict_part = f"{{{formatted_pairs}}}"
                l = f"{formatted_dict_part} {number_part}"
                if flag or len(l) > 35:
                    l = l.replace(': ', ':')
                if len(l) > 35:
                    l = l.replace(', ', ',')

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
        ss=0
        current_time = today - timedelta(days=i)
        text = current_time.strftime('%d-%m-%Y')

        all_a = eval("{'agt':0, 'kil':0, 'med':0,'pob':0,'ser':0}")

        for i in range (1,7):
            try:
                filename = log_dir + f'\\{current_time.strftime("%d.%m.%Y")}_W{i}.sold'

                with open(filename, 'r') as file:
                    first_line = file.readline().strip()
                    apples = eval(first_line)    
                    apples = dict(sorted(apples.items()))
                    s = 0
                    for k,v in apples.items():
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
    all_a = dict()
    name = 'inventory'
    for i in range (1,7):
        fn = log_dir + f'/W{i}_{name}.ah'
        try:
            with open(fn, 'r') as file:
                first_line = file.readline().strip()
                apples = eval(first_line)
                apples = dict(sorted(apples.items()))

                for k, v in apples.items():
                    all_a[k] = apples.get(k, 0) + v

        except Exception as e:
            print(fn)
            continue
    return f"\n{name}:\n {str(all_a).replace(' ', '')}"

async def make_sum(chat_id, context: ContextTypes.DEFAULT_TYPE) -> None:
    global log_dir
    current_time = datetime.now()
    text = "sold:\n"
    print("make_sum")
    ss = 0
    all_a = eval("{'agt':0, 'med':0, 'kil':0, 'pob':0,'ser':0}")

    for i in range (1,7):
        try:
            filename = log_dir + f'\\{current_time.strftime("%d.%m.%Y")}_W{i}.sold'

            with open(filename, 'r') as file:
                first_line = file.readline().strip()
                apples = eval(first_line)    
                apples = dict(sorted(apples.items()))

                s = 0
                for k,v in apples.items():
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
             f'\n{str(all_a).replace(" ", "")}  {ss}\n\nAH:')

    f_list = []
    for i in range(1, 7):
        f_list.append(log_dir + f'\\W{i}.ah')

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
                        for k, v in apples.items():
                            if k != 'z' and k != 'max':
                                s += v
                                ss += v
                            sum_dict[k] = sum_dict.get(k, 0) + v

                            if k == 'max':
                                ah_max=str(v)

                        text += "\n" + str(apples).replace(" ", "").replace(": ",":") + f' {s}'
                        # text += p + "\n" + str(apples)
                except Exception as e:
                    print(e)
                    text += "\n"+first_line
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
        minutes_passed = time_difference.total_seconds() // 6 /10

        text += "".join(list(file.readlines())) + "    " + str(minutes_passed) + "m"

    text = format_text(text)
    text = text.replace(" z:", "  ")
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')


async def make_log(chat_id, context: ContextTypes.DEFAULT_TYPE, count=30, full=False) -> None:
    global log_dir
    current_time = datetime.now()
    filename = log_dir + f'\\log_{current_time.strftime("%d.%m.%Y")}.log'
    print(filename)

    if not full:
        current_time = datetime.now()
        filename = log_dir + f'\\log_{current_time.strftime("%d.%m.%Y")}.log'
        print(filename)
        text = ""

        with open(filename, 'r') as file:
            text = "".join(list(file.readlines()[-count:]))
        text = "```log\n" + text + "\n```"
        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')
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

    dir_ss = log_dir + "/ss"

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


def get_all_files(template: str, folder: str) -> list:
    res = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if template in file:
                res.append(os.path.join(root, file))

    return res


async def make_fn(chat_id, context: ContextTypes.DEFAULT_TYPE, text):
    global log_dir
    dir_ss = log_dir + "/ss"

    name = text.replace("fn", "").replace(" ", "")

    fns = get_all_files(name, dir_ss)

    for fn in fns:
        with open(fn, 'rb') as photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo)
        await asyncio.sleep(0.5)

async def make_time(chat_id, context:ContextTypes.DEFAULT_TYPE):
    global log_dir
    dir_ss = log_dir

    text = "```time\n"

    for i in range(1,7):
        name = f"W{i}"
        fn = f'{dir_ss}/{name}.time'

        try:
            with open(fn, 'r') as file:
                items = file.readline().split(" ")
                t = float(items[0].replace(" ", ""))
                c = items[1]
                cur_t = time.time()
                diff = int((cur_t - t)//60)

                text += f'{name}: {diff}m  [{c}]\n'
        except Exception as e:
            print(e)
            text += f'{name}: err \n'
    text += "```"
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')


async def make_screenshot(chat_id, context: ContextTypes.DEFAULT_TYPE, full=False) -> None:
    screenshot = pyautogui.screenshot()
    fn = r'C:\Users\templocaladmin\PycharmProjects\tbot\tbot\screenshot.png'
    screenshot.save(fn)

    if not full:
        with open(fn, 'rb') as photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo)
    else:
        with open(fn, 'rb') as file:
            await context.bot.send_document(chat_id=chat_id, document=file, filename='photo.jpg')


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    content_prison = os.listdir(prison_dir)
    content_except = os.listdir(except_dir)


    global set_folders_prison
    global set_folders_except
    new_set_folders_prison = set(
        [folder for folder in content_prison if os.path.isdir(os.path.join(prison_dir, folder))])
    new_set_folders_except = set(
        [folder for folder in content_except if os.path.isfile(os.path.join(except_dir, folder))])

    diff_prison = new_set_folders_prison - set_folders_prison
    diff_except = new_set_folders_except - set_folders_except
    set_folders_prison = new_set_folders_prison
    set_folders_except = new_set_folders_except
    if len(diff_prison) > 0:
        for user in users:
            await context.bot.send_message(user, text=str(diff_prison))
    for file in diff_except:
        fn = except_dir + '\\' + file
        with open(fn, 'rb') as file:
            await make_log(chat_id=andrei, context=context, count=30)
            await context.bot.send_document(chat_id=andrei, document=file, filename='except.jpg')

def get_last_commit_message() -> str:
    result = subprocess.run(
        ['git', 'log', '-1', '--pretty=%h [%cd]', '--date=format:%Y-%m-%d %H:%M:%S'],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()


import os


def files_tree() -> str:
    global log_dir
    start_dir = os.path.expanduser(log_dir)
    def build_tree(dir_path: str, prefix: str = "") -> str:
        tree_str = ""
        entries = sorted(os.listdir(dir_path))  # Сортируем файлы и каталоги по имени
        total_entries = len(entries)

        for index, entry in enumerate(entries):
            path = os.path.join(dir_path, entry)
            is_last = index == total_entries - 1

            # Добавляем текущий элемент к дереву
            tree_str += prefix + ("└── " if is_last else "├── ") + entry + "\n"

            # Если это директория, рекурсивно строим дерево
            if os.path.isdir(path):
                new_prefix = prefix + ("    " if is_last else "│   ")
                tree_str += build_tree(path, new_prefix)

        return tree_str

    return build_tree(start_dir).rstrip()

async def make_files(chat_id, context:ContextTypes.DEFAULT_TYPE):
    text = "```tree\n" + files_tree() + "```"
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    global flag_alarm

    if chat_id not in users:
        return
    text = update.message.text.lower()

    await context.bot.send_message(chat_id=chat_id, text=get_last_commit_message())

    if chat_id == martin:
        await context.bot.send_message(chat_id=andrei, text=f"Martin say: {text}")

    if "ss" in text:
        await make_ss(chat_id, context, text=text)
    elif "get" in text:
        await make_get_file(chat_id=chat_id, context=context, text=text)
    elif "file" in text:
        await make_files(chat_id, context)
    elif "fn" in text:
        await make_fn(chat_id, context, text=text)
    elif "time" in text:
        await make_time(chat_id, context)
    elif "fshot" in text:
        await make_screenshot(chat_id, context, full=True)
    elif "shot" in text:
        await make_screenshot(chat_id, context)
    elif "full" in text or "flog" in text:
        await make_log(chat_id, context, full=True)
    elif "log" in text:
        integer_value = 5
        try:
            integer_value = int(''.join(re.findall(r'\d+', text)))
        except ValueError:
            pass
        await make_log(chat_id, context, count=integer_value)
    elif "comm" in text:
        print(text)
        await create_command(chat_id, context, text)
    elif "sum" in text:
        await make_log(chat_id, context, count=5)
        await make_sum(chat_id, context)
    elif "history" in text:
        await make_history(chat_id, context)
    else:
        text = """ss    - shot from workers [ss w1]
get   - get file      [get w1.ah]
file  - get tree of files 
fn    - screenshot name   [fn ah]
time  - last ah update 
full  - get curr file log
log   - log               [log30]
comm  - create command [comm buy]
sum   - summary
history - 14 day history
        """
        text = "```help\n" + text + "\n```"
        await context.bot.send_message(chat_id=andrei, text=text, parse_mode='Markdown')

    if flag_alarm:
        context.job_queue.run_repeating(alarm, 1, chat_id=chat_id, name=str(chat_id))
        flag_alarm = False






def main() -> None:
    global prison_dir
    global set_folders_except
    global set_folders_prison
    global token
    global log_dir

    name = 'inventory'
    fn1 = log_dir + f'/W1_{name}.ah'
    fn6 = log_dir + f'/W6_{name}.ah'

    with open(fn1, 'w', encoding="utf-8") as f:
        f.write("{'agt':7, 'med':2, 'kil':8, 'pob':4,'ser':9}")
    with open(fn6, 'w', encoding="utf-8") as f:
        f.write("{'agt':1, 'med':2, 'kil':3, 'pob':4,'ser':5}")

    print(fn1)
    print(fn6)
    print("=====")

    # {'agt':8, 'med':4, 'kil':11, 'pob':8,'ser':14 }


    content = os.listdir(prison_dir)
    set_folders_prison = set([folder for folder in content if os.path.isdir(os.path.join(prison_dir, folder))])

    content = os.listdir(except_dir)
    set_folders_except = set([folder for folder in content if os.path.isfile(os.path.join(except_dir, folder))])

    application = Application.builder().token(token).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    read_config()
    main()
