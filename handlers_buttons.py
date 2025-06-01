# handlers.py

import asyncio
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import config
from file_utils import files_tree, split_text_into_chunks
from messages import *
import subprocess
from telegram.error import TelegramError

def get_last_commit_message() -> str:
    result = subprocess.run(
        ['git', 'log', '-1', '--pretty=%h [%cd]', '--date=format:%Y-%m-%d %H:%M:%S'],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

# Дерево меню для кнопок
if config.mode == config.mode_buyer:
    menu_tree = {
        "root": ["ScreenShot", "config", "log"],
        "ScreenShot": ["Bots name", "File name", "PC"],
        "config": ["med", "pob", "ser", "kil", "agt"]
    }
elif config.mode == config.mode_worker:
    menu_tree = {
        "root": ["Summary", "ScreenShot", "config", "log"],
        "ScreenShot": ["Bots name", "File name"],
        "config": ["med", "pob", "ser", "kil", "agt"]
    }

async def send_menu(chat_id: int, context: ContextTypes.DEFAULT_TYPE, level: str = "root", path: str = None, message_id: int = None):
    if path is None:
        path = level  # для корня path == "root"

    # Получаем список подменю для текущего уровня
    items = menu_tree.get(level, [])

    # Если в меню пусто, значит подменю нет, можно отправить сообщение с выбором
    if not items:
        await context.bot.send_message(chat_id, text=f"Вы выбрали: {level}")
        return

    buttons = []
    for item in items:
        new_path = f"{path}>{item}"
        buttons.append([InlineKeyboardButton(item, callback_data=new_path)])

    reply_markup = InlineKeyboardMarkup(buttons)
    text = f"Выбери опцию: {level}"

    if message_id:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=reply_markup
            )
        except TelegramError as e:
            print(f"[edit_message_text ERROR] {e}")
            # fallback — отправить новое сообщение
            await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_menu(update.effective_chat.id, context, "root")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    print(f"Callback data: {data}")

    # data — это строка с путем: "root>ScreenShot>PC" и т.п.
    path_parts = data.split(">")

    # Определяем текущий уровень меню — последний элемент пути
    current_level = path_parts[-1]

    # Проверяем, есть ли у current_level подменю
    if current_level in menu_tree and menu_tree[current_level]:
        # Есть подменю — показываем следующее меню
        await send_menu(chat_id, context, level=current_level, path=data, message_id=message_id)
        return

    # Если подменю нет — выполняем действия для конкретных пунктов
    if data == "root>ScreenShot>PC":
        await make_screenshot(chat_id, context)
    elif data == "root>Summary":
        await make_money(chat_id, context)
        await make_sum(chat_id, context)
    elif data == "root>config":
        config_dict = get_config()  # твой метод, возвращает dict
        # Формируем текст с текущими настройками
        lines = [f"{k}: {v}" for k, v in config_dict.items()]
        text = "Текущий конфиг:\n" + "\n".join(lines)

        # Формируем кнопки из ключей конфига
        buttons = [
            [InlineKeyboardButton(key, callback_data=f"{data}>{key}")]
            for key in config_dict.keys()
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=reply_markup
        )
        return
    else:
        # Если это какой-то другой пункт без подменю — просто отправляем сообщение
        await context.bot.send_message(chat_id, text=f"Вы выбрали: {current_level}")

# Показать дерево файлов
async def make_files(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    text = files_tree()
    chunks = split_text_into_chunks(text)
    for item in chunks:
        await context.bot.send_message(chat_id=chat_id, text=f"```\n{item}```", parse_mode='Markdown')
        await asyncio.sleep(0.2)

# Эхо-обработчик команд
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    text = update.message.text.lower()

    if chat_id == config.martin:
        await context.bot.send_message(chat_id=config.andrei, text=f"Martin say: {text}")

    if "ss" in text:
        await make_ss(chat_id, context, text=text)
    elif "--" in text or "++" in text:
        await change_value(chat_id, context, text=text)
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
        try:
            integer_value = int(''.join(re.findall(r'\d+', text)))
        except ValueError:
            integer_value = 5
        await make_log(chat_id, context, count=integer_value)
    elif "comm" in text:
        await create_command(chat_id, context, text)
    elif "sum" in text:
        await make_money(chat_id, context)
        await make_sum(chat_id, context)
    elif "setconf" in text:
        if config.mode == config.mode_worker:
            await set_conf(chat_id, context, text)
        else:
            await set_conf_buyer(chat_id, context, text)
    elif "conf" in text:
        if config.mode == config.mode_worker:
            await make_conf(chat_id, context)
        else:
            await make_conf_buyer(chat_id, context)
    elif "history" in text:
        await make_history(chat_id, context)
    else:
        if chat_id not in config.users:
            return
        await send_menu(chat_id, context, "root")
