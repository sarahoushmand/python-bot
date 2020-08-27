from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
import mysql.connector
import os
import logging

os.environ['https_proxy'] = 'socks5h://127.0.0.1:1050/'
os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:1050/'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
MOVIE = range(1)
DELETE = range(1)
TOKEN = "1013928629:AAFsBMNqz4crCjMuCyrxS073V8a9wSukKc8"


def start(bot, update):
    # user = update.message.from_user
    # send = f"{user.username} started your bot. \n First name {user.first_name} \n ID:{user.id}"
    # bot.send_message(chat_id=user.id, text=send)
    update.message.reply_text('به ربات ما خوش اومدی 😉')
    update.message.reply_text('بزا اول دفترچه راهنما رو برات بفرستم😂')
    update.message.reply_text(' ۱. برای اضافه کردن فیلم ها و یا سریال هایت میتونی از  دستور add/ استفاده کنی و هر چندتا فیلم و یا سریالت رو اد کنی و هر موقع نخواستی دستور cancel/ رو بزنی.😃 ۲. برای دیدن لیست فیلم ها و سریال هات میتونی از دستور show/ استفاده کنی. ۳. و در آخر خواستی فیلمیو از تو لیستت حذف کنی دستور delete/ و بزن.🤩' )


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
                                  user='root', password='sara717880',
                                  host='localhost',
                                  database='movie'
                                 )
    cursor = db.cursor()
    sql = "INSERT INTO movies (chat_id, movie) VALUES (%s, %s)"
    val = (chat_id, message)
    cursor.execute(sql, val)
    db.commit()
    update.message.reply_text('فیلمت اضافه شد😎')

    # return ConversationHandler.END


def show(bot, update):
    user = update.message.from_user
    chatid = user.id

    db = mysql.connector.connect(
        user='root', password='sara717880',
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

    update.message.reply_text(movie)


def delete(bot, update):
    user = update.message.from_user
    chatid = user.id

    db = mysql.connector.connect(
        user='root', password='sara717880',
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

    update.message.reply_text(movie)
    update.message.reply_text('حالا اسم فیلمیو که میخواهی حذف کنی انتخاب کن')
    return DELETE


def delete_movie(bot, update, user_data):
    movie_id = update.message.text.replace("/", "")
    db = mysql.connector.connect(
        user='root', password='sara717880',
        host='localhost',
        database='movie'
    )
    cursor = db.cursor()
    sql = "DELETE FROM movies WHERE id = %s"
    cursor.execute(sql, (int(movie_id),))
    db.commit()
    update.message.reply_text("فیلم مورد نظر حذف شد")

    return ConversationHandler.END


def cancel(bot, update):
    update.message.reply_text('قول میدم دیگه چیزی به فیلمات اضافه نکنم🤪')
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
        fallbacks=[CommandHandler('cancel', cancel)]
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
        fallbacks=[]
    )
    dp.add_handler(CommandHandler('show', show))
    dp.add_handler(add_movie_conversation)
    dp.add_handler(delete_movie_conversation)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()



