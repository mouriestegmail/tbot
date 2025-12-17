import messages
from messages import *
from telegram.ext import ContextTypes, MessageHandler, filters
from telegram.ext import Application
from telegram import Update
import subprocess
import sys
import asyncio
import config
import file_handler
import os
import signal


from watchdog.observers import Observer



set_folders_prison = set()
set_folders_except = set()



def get_last_commit_message() -> str:
    result = subprocess.run(
        ['git', 'log', '-1', '--pretty=%h [%cd]', '--date=format:%Y-%m-%d %H:%M:%S'],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

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
    text = files_tree()

    chunks = split_text_into_chunks(text)

    for item in chunks:
        text = "```\n" + item + "```"
        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')
        await asyncio.sleep(0.2)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    global flag_alarm

    # if chat_id not in config.users:
    #     return
    if update.message.text:
        text = update.message.text.lower()
    else:
        return None

    # await context.bot.send_message(chat_id=chat_id, text=get_last_commit_message())

    if chat_id == config.martin:
        await context.bot.send_message(chat_id=config.andrei, text=f"Martin say: {text}")

    fn = config.watch_dir + f"/{chat_id}."
    tmp = fn + "tmp"
    reply = fn + "input"
    with open(tmp, 'w', encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, reply)

    if "log" in text or \
        "sum" in text or \
        "day" in text \
        :
        return None
    elif "ss" in text:
        await make_ss(chat_id, context, text=text)
        return None
    elif "don" in text:
        await make_don(chat_id, context)
        return None
    elif "get" in text:
        await make_get_file(chat_id=chat_id, context=context, text=text)
        return None
    elif "file" in text:
        await make_files(chat_id, context)
        return None
    elif "fn" in text:
        await make_fn(chat_id, context, text=text)
        return None
    elif "time" in text:
        await make_time(chat_id, context)
        return None
    elif "fshot" in text:
        await make_screenshot(chat_id, context, full=True)
        return None
    elif "shot" in text:
        await make_screenshot(chat_id, context)
        return None
    elif "comm" in text:
        print(text)
        await create_command(chat_id, context, text)
        return None
    # elif "sum" in text:
    #     # await make_log(chat_id, context, count=5)
    #     # await make_money(chat_id, context)
    #     await make_sum(chat_id, context)
    #     return None

    elif "setbconf" in text:
        await set_bconf(chat_id, context, text)
        return None

    elif "bconf" in text:
        await make_bconf(chat_id, context)
        return None


    elif "setconf" in text:
        if config.mode == config.mode_worker:
            await set_conf(chat_id, context, text)
            return None
        else:
            await set_conf_buyer(chat_id, context, text)
            return None
    elif "conf" in text:
        if config.mode == config.mode_worker:
            await make_conf(chat_id, context)
            return None
        else:
            await make_conf_buyer(chat_id, context)
            return None

    elif "history" in text:
        await make_history(chat_id, context)
        return None
    else:
        if chat_id not in config.users:
            return None
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
        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')
        return None


# Запуск дочернего скрипта
#child = subprocess.Popen(
#    [sys.executable, '../mnbot/parser_png.py'],
#    preexec_fn=os.setsid if os.name != 'nt' else None,  # только на Unix
#    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
#)


def main() -> None:


    # content = os.listdir(messages.prison_dir)
    # set_folders_prison = set([folder for folder in content if os.path.isdir(os.path.join(messages.prison_dir, folder))])
    #
    # content = os.listdir(messages.except_dir)
    # set_folders_except = set([folder for folder in content if os.path.isfile(os.path.join(messages.except_dir, folder))])

    app = Application.builder().token(config.token).build()

    loop = asyncio.get_event_loop()
    observer = Observer()
    print(f"watch dir: {config.watch_dir}")
    observer.schedule(file_handler.NewFileHandler(app.bot, loop),
                      path=config.watch_dir,
                      recursive=False)
    observer.start()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.run_polling()





if __name__ == "__main__":
    arg = ""
    if len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg in ['-b', '-d', '-m']:
            pass
        else:
            print(f'undefine arg {arg}. use "-b", "-d", "-m" or empty ')
            exit(-1)
    print(arg)
    config.read_config(arg)

    print(config.log_dir,
          config.prison_dir,
          config.commands_dir,
          config.except_dir,
          config.token,
          config.config_json,
          config.watch_dir,

          sep="\n")

    try:
        main()
    except Exception as e:
        print("Завершение родителя.", e)
        try:
            pass
            #if os.name == 'nt':
            #    child.send_signal(signal.CTRL_BREAK_EVENT)
            #else:
            #    os.killpg(os.getpgid(child.pid), signal.SIGTERM)
        except Exception as e:
            print(f"Ошибка при завершении дочернего: {e}")
