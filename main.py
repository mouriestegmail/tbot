import sys

import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import config
import file_handler
import handlers_buttons
from handlers_buttons import start, echo, handle_callback
from telegram.ext import Application
import asyncio
from watchdog.observers import Observer

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

def main():
    print(f"Using token: {config.token}")
    app = Application.builder().token(config.token).build()

    loop = asyncio.get_event_loop()

    event_handler = file_handler.NewFileHandler(app.bot, loop)

    observer = Observer()
    observer.schedule(event_handler, path=config.watch_dir, recursive=False)
    observer.start()

    app.add_handler(CommandHandler("start", handlers_buttons.start))

    # Добавляем обработчик для кнопок (callback_query)
    app.add_handler(CallbackQueryHandler(handlers_buttons.handle_callback))

    # Добавляем обработчик текстовых сообщений (эхо и команды из текста)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handlers_buttons.echo))


    app.run_polling()

if __name__ == '__main__':
    arg = ""
    if len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg == '-b':
            pass
        elif arg == '-d':
            pass
        elif arg == '-m':
            pass
        else:
            print(f'undefine arg {arg}. use "-b" or "-d" or empty ')
            exit(-1)

    config.read_config(arg)
    main()
