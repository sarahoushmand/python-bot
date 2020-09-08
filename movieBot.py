import logging
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)
import os
from decouple import config
import mysql.connector
from bs4 import BeautifulSoup
import requests

os.environ['https_proxy'] = config('PROXY')
os.environ['HTTPS_PROXY'] = config('PROXY')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

MOVIE, SELECT = range(2)
IMDB = range(1)
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
    ls = 'فیلم مورد نظر خود را انتخاب کنید:\n'
    count = 1
    message = update.message.text
    user = update.message.from_user
    chat_id = user.id
    text = message
    response = requests.get("https://www.imdb.com/find", params={"q": text})

    soup = BeautifulSoup(response.content, "html.parser")
    result = soup.find_all("td", attrs={"class": "result_text"})
    if not result:
        keyboard([{'/Add'}, {'/Show', '/Delete'}], "فیلمت تو imdb نیست.", bot, update)
        return ConversationHandler.END
    for item in result:
        imdb_link = item.find('a').attrs['href']
        name = item.text
        if imdb_link.startswith('/title'):
            ls += str(count) + ': ' + imdb_link.replace('/title', '')[0:-1] + ' - ' + name + '\n'
            count += 1
    update.message.reply_text(ls)
    return SELECT

def add_movie_imdb(bot, update, user_data):
    image_link = ''
    summary = ''
    imdb_id = update.message.text
    user = update.message.from_user
    chat_id = user.id
    response = requests.get("https://www.imdb.com/title" + imdb_id + '/')
    soup = BeautifulSoup(response.content, "html.parser")
    name = soup.find('h1').text
    result = soup.find_all("div", attrs={"class": "poster"})
    for item in result:
        imdb_link = item.find('a').attrs['href']
        image_link = ('https://www.imdb.com/' + imdb_link)

    result = soup.find("span", attrs={"itemprop": "ratingValue"})
    rate = result.text

    items = soup.find_all("div", attrs={"class": "plot_summary "})
    for item in items:
        summary = (item.find("div", attrs={"class": "summary_text"}).text.strip())

    db = mysql.connector.connect(
        user=config('DB_USERNAME'), password=config('DB_PASSWORD'),
        host='localhost',
        database='Movie'
    )
    cursor = db.cursor()
    sql = 'INSERT INTO users_movies (user_id, imdb_id, name, image_link, rate, summary) VALUES (%s, %s, %s, %s, %s, %s)'
    val = (int(chat_id), imdb_id, name, image_link, float(rate), summary)
    cursor.execute(sql, val)
    db.commit()
    keyboard([["/back"]], "فیلمت اضافه شد", bot, update)


def show(bot, update):
    user = update.message.from_user
    chatid = user.id

    db = mysql.connector.connect(
        user=config('DB_USERNAME'), password=config('DB_PASSWORD'),
        host='localhost',
        database='Movie'
    )
    cursor = db.cursor()
    sql = "SELECT id,name FROM users_movies where user_id = %s"
    cid = (int(chatid),)

    cursor.execute(sql, cid)

    all = cursor.fetchall()
    movie = ''
    for i in range(len(all)):
        movie += '/' + str(all[i][0]) + ' : ' + all[i][1] + '\n'
    if movie == '':
        update.message.reply_text('فیلمی موجود نیست')
    else:
        update.message.reply_text("حالا از بین فیلم های پایین فیلمتو انتخاب کن تا اطلاعات بیشتری بهت بدم")
        update.message.reply_text(movie)

    return IMDB


def show_movie(bot, update, user_data):
    id = update.message.text.replace("/", "")
    user = update.message.from_user
    chat_id = user.id
    db = mysql.connector.connect(
        user=config('DB_USERNAME'), password=config('DB_PASSWORD'),
        host='localhost',
        database='Movie'
    )
    cursor = db.cursor()
    sql = "SELECT name,image_link, rate, summary FROM users_movies where user_id = %s and id = %s "
    cid = (int(chat_id), id)
    cursor.execute(sql, cid)

    all = cursor.fetchall()
    movie = ''
    for i in range(len(all)):
        movie += "Name: " + all[i][0] + '\n' + "Image_Link: " + all[i][1] + '\n' + "Rate: " + str(all[i][2]) \
                 + "/10" + '\n' + "Summary: " + all[i][3] + '\n'

    if movie == '':
        update.message.reply_text('فیلمی موجود نیست')
    else:
        update.message.reply_text(movie)
    keyboard([["/back", "/show(All Movie)"]], "دیگه چی میخوای؟😎", bot, update)


def delete(bot, update):
    user = update.message.from_user
    chatid = user.id

    db = mysql.connector.connect(
        user=config('DB_USERNAME'), password=config('DB_PASSWORD'),
        host='localhost',
        database='Movie'
    )
    cursor = db.cursor()
    sql = "SELECT id, name FROM users_movies where user_id = %s"
    cid = (chatid,)

    cursor.execute(sql, cid)

    all = cursor.fetchall()
    movie = ''
    for i in range(len(all)):
        movie += '/' + str(all[i][0]) + ' : ' + all[i][1] + '\n'

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
        database='Movie'
    )
    cursor = db.cursor()
    sql = "DELETE FROM users_movies WHERE id = %s"
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
            ],
            SELECT: [
                MessageHandler(Filters.command & Filters.regex('^\/tt'), add_movie_imdb, pass_user_data=True)
            ]
        },
        fallbacks=[MessageHandler(Filters.command, back)]
    )

    show_movie_conversation = ConversationHandler(
        entry_points=[
            CommandHandler('show', show)
        ],
        states={
            IMDB: [
                MessageHandler(Filters.command & Filters.regex('^\/\d+'), show_movie, pass_user_data=True)
            ],
        },
        fallbacks=[MessageHandler(Filters.command & Filters.regex('^\/back'), back),
                   MessageHandler(Filters.command & Filters.regex('^\/show'), show)]
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
    dp.add_handler(add_movie_conversation)
    dp.add_handler(show_movie_conversation)
    dp.add_handler(delete_movie_conversation)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()



