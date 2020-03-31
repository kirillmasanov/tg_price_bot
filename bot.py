from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from handlers import *
from settings import *

log = logging.getLogger()
log.setLevel(logging.INFO)
# handler = logging.FileHandler('bot.log', 'w', 'utf-8')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)


def main():
    mybot = Updater(TOKEN, request_kwargs=PROXY, use_context=True)

    logging.info('Бот запускается')

    dp = mybot.dispatcher

    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(MessageHandler(Filters.regex('^(Прислать данные)$'), send_data))

    mybot.start_polling()
    mybot.idle()


if __name__ == '__main__':
    main()
