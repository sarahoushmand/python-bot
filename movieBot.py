import logging
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)
import os
from decouple import config
import mysql.connector

os.environ['https_proxy'] = config('PROXY')
os.environ['HTTPS_PROXY'] = config('PROXY')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

MOVIE = range(1)
DELETE = range(1)
TOKEN = config('TELEGRAM_TOKEN')


def keyboard(ls, text, bot, update):
    reply_keyboard = ls
    update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                              one_time_keyboard=True,
                              resize_keyboard=True))


def start(bot, update):

    keyboard([{'/Add'}, {'/Show', '/Delete'}], "سلام🙋‍♀\nبه روبات ما خوش اومدی🥰\nحالا با فیلمات میخوای چیکار کنی؟😋", bot,update)


def add(bot, update):
    message = update.message.text
    user = update.message.from_user
    chat_id = user.id
    update.message.reply_text('حالا اسم فیلماتو وارد کن')

    return MOVIE


def add_movie(bot, update, user_data):
    message = update.message.text
    user = update.message.from_user
    chat_id = user.id
    db = mysql.connector.connect(
                                  user=config('DB_USERNAME'), password=config('DB_PASSWORD'),
                                  host='localhost',
                                  database='movie'
                                 )
    cursor = db.cursor()
    sql = "INSERT INTO movies (chat_id, movie) VALUES (%s, %s)"
    val = (chat_id, message)
    cursor.execute(sql, val)
    db.commit()
    keyboard([["/back"]], 'فیلمت اضافه شد😎', bot, update)


def show(bot, update):
    user = update.message.from_user
    chatid = user.id

    db = mysql.connector.connect(
        user=config('DB_USERNAME'), password=config('DB_PASSWORD'),
        host='localhost',
        database='movie'
    )
    cursor = db.cursor()
    sql = "SELECT movie FROM movies where chat_id = %s"
    cid = (chatid,)

    cursor.execute(sql, cid)

    all = cursor.fetchall()
    movie = ''
    for i in range(len(all)):
        movie += str(i+1) + ' : ' + all[i][0] + '\n'
    if movie == '':
        update.message.reply_text('فیلمی موجود نیست')
    else:
        update.message.reply_text(movie)
    keyboard([{'/Add'}, {'/Show', '/Delete'}], "دیگه میخوای چیکارا بکنی؟🙊", bot, update)


def delete(bot, update):
    user = update.message.from_user
    chatid = user.id

    db = mysql.connector.connect(
        user=config('DB_USERNAME'), password=config('DB_PASSWORD'),
        host='localhost',
        database='movie'
    )
    cursor = db.cursor()
    sql = "SELECT movie, id FROM movies where chat_id = %s"
    cid = (chatid,)

    cursor.execute(sql, cid)

    all = cursor.fetchall()
    movie = ''
    for i in range(len(all)):
        movie += '/' + str(all[i][1]) + ' : ' + all[i][0] + '\n'

    if movie != '':
        update.message.reply_text(movie)
        update.message.reply_text('حالا اسم فیلمیو که میخواهی حذف کنی انتخاب کن')
    else:
        update.message.reply_text('فیلمی موجود نیست')

    return DELETE


def delete_movie(bot, update, user_data):
    movie_id = update.message.text.replace("/", "")
    db = mysql.connector.connect(
        user=config('DB_USERNAME'), password=config('DB_PASSWORD'),
        host='localhost',
        database='movie'
    )
    cursor = db.cursor()
    sql = "DELETE FROM movies WHERE id = %s"
    cursor.execute(sql, (int(movie_id),))
    db.commit()
    keyboard([["/back"]], "فیلم مورد نظر حذف شد", bot, update)


def back(bot, update):
    keyboard([{'/Add'}, {'/Show', '/Delete'}], "دیگه میخوای چیکارا بکنی؟🙊", bot, update)
    return ConversationHandler.END


def main():

    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    add_movie_conversation = ConversationHandler(
        entry_points=[
            CommandHandler('add', add)
        ],
        states={
            MOVIE: [
                MessageHandler(Filters.text & (~ Filters.command), add_movie, pass_user_data=True)
            ]
        },
        fallbacks=[MessageHandler(Filters.command, back)]
    )

    delete_movie_conversation = ConversationHandler(
        entry_points=[
            CommandHandler('delete', delete)
        ],
        states={
            DELETE: [
                MessageHandler(Filters.command & Filters.regex('^\/\d+'), delete_movie, pass_user_data=True)
            ]
        },
        fallbacks=[MessageHandler(Filters.command, back)]
    )
    dp.add_handler(CommandHandler('show', show))
    dp.add_handler(add_movie_conversation)
    dp.add_handler(delete_movie_conversation)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()



