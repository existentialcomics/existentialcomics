import sqlite3
import markdown
import settings as s
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Markup
from sqlalchemy import create_engine, text

engine = create_engine('mysql://' + s.MYSQL_USER + ':' + s.MYSQL_PASSWORD + '@' + s.MYSQL_HOST + '/' + s.MYSQL_DB)

def get_db():
    return engine.connect()

def getAllPhilosophers():
    c = get_db()
    t = text('SELECT philosopher_id FROM philosopher ORDER BY birth_year')
    results = c.execute(t)
    philosophers = []
    for row in results:
        philosophers.append(getPhilosopher(row['philosopher_id']))
    return philosophers

def getPhilosopher(philosopherId):
    from model.philosopher import Philosopher
    c = get_db()
    name = ""
    birthYear = ""
    deathYear = ""
    t = text('SELECT name, birth_year, death_year FROM philosopher WHERE philosopher_id = :philosopherId')
    results = c.execute(t, philosopherId = philosopherId)
    philosophers = []
    for row in results:
        name = row['name']
        if (row['birth_year'] is None):
            birthYear = '-'
        elif (row['birth_year'] < 0):
            birthYear = str(abs(row['birth_year'])) + " B.C."
        else:
            birthYear = str(row['birth_year'])

        if (row['death_year'] is None):
            deathYear = 'present'
        elif (row['death_year'] < 0):
            deathYear = str(abs(row['death_year'])) + " B.C."
        else:
            deathYear = str(row['death_year'])

    comics = []
    tC = text('SELECT comic_id from philosopher_comic WHERE philosopher_id = :philosopherId')
    resultsComic = c.execute(tC, philosopherId=philosopherId)
    for rowCom in resultsComic:
        comics.append(getComic(rowCom['comic_id']))
    return Philosopher(philosopherId, name, birthYear, deathYear, comics)

def getNonPhilosopherComics():
    c = get_db()
    results = c.execute('SELECT c.comic_id, pc.philosopher_id FROM comic c LEFT JOIN philosopher_comic pc ON c.comic_id = pc.comic_id WHERE philosopher_id IS NULL AND lang="en"');
    comics = []
    for row in results:
        comics.append(getComic(row['comic_id']))
    return comics
 

def getCaptcha():
    import random
    import uuid
    from subprocess import call
    from model.captcha import Captcha
    sessionId = uuid.uuid1()
    c = get_db()
    maxId = 0
    results = c.execute('SELECT MAX(id) as id FROM captcha')
    for row in results:
        maxId = row['id']
    captchaId = random.randint(1,maxId)
    question = "error"
    answer = "error"
    t = text('SELECT question, answer FROM captcha WHERE id = :captchaId')
    results = c.execute(t, captchaId=captchaId)
    for row in results:
        question = row['question']
        answer = row['answer']
    captcha = Captcha(question, answer)
    status = call(['perl' , '/home/corey/captchaGen.pl', captcha.question, captcha.imageFile], shell=False)
    t = text('INSERT INTO captcha_session (captcha_id, session_id, time) VALUES (:captchaId, :sessionId, NOW())')
    c.execute(t, captchaId=captchaId, sessionId=captcha.session)
    return captcha;

def checkCaptcha(sessionId, testAnswer):
    c = get_db()
    t = text('SELECT c.answer as answer FROM captcha_session cs LEFT JOIN captcha c ON cs.captcha_id = c.id WHERE cs.session_id = :sessionId')
    answer = None
    results = c.execute(t, sessionId=sessionId)
    for row in results:
        answer = row['answer']
    if answer is None:
        return 0
    if answer.lower() != testAnswer.lower():
        return 0
    return 1

def getAllComics():
    maxComic = getMaxComic()
    comics = list()
    for i in range(1, maxComic + 1):
        comic = getComic(i)
        comic.setAltLangs(getAltLanguages(i))
        comics.append(comic)
    return comics

def getAltLanguages(comicId, lang="en"):
    from model.language import Language
    c = get_db()
    t = text('SELECT l.code, l.name FROM comic c LEFT JOIN language l ON c.lang = l.code WHERE c.comic_id = :comicId AND c.lang != :lang')
    results = c.execute(t, comicId=comicId, lang=lang)
    if results is None:
        return None
    languages = list()
    for row in results:
        languages.append( Language(row['code'], row['name'] ))
    return languages


def getComic(comicId, lang="en"):
    from model.comic import Comic
    from model.image import Image

    c = get_db()

    t = text("SELECT title, DATE_FORMAT(pub_date, '%a, %d %b %Y %T') as pub_date_rss, explanation, type FROM comic WHERE comic_id = :comicId AND lang = :lang")
    results = c.execute(t, comicId = comicId, lang = lang)

    if results is None:
        return None

    title, pubDate, explanation, comicType = ("", "", "", "")

    for row in results:
        title = row['title']
        pubDate = row['pub_date_rss']
        if (row['explanation']):
            explanation = Markup(markdown.markdown(row['explanation']))
        else:
            explanation = ""
        comicType = row['type']


    t = text('SELECT filename, image_id, alt_text FROM image WHERE comic_id = :comicId AND lang = :lang')
    results = c.execute(t, comicId = comicId, lang = lang)
    images = []
    for row in results:
        newImage = Image(s.STATIC_URL + row['filename'], comicId, row['image_id'], row['alt_text'])
        images.append(newImage)

    return Comic(title, images, comicId, pubDate, explanation, comicType)

def getLatestComics(comicsToGet):
    c = get_db()
    
    t = text('SELECT comic_id FROM comic WHERE lang = "en" ORDER BY comic_id DESC limit :limit')
    results = c.execute(t, limit = comicsToGet)
    comics = []
    for row in results:
        comics.append(getComic(row['comic_id']))
    return comics

def getMaxComic():    
    c = get_db()
    results = c.execute('SELECT MAX(comic_id) as comic_id FROM comic')
    for row in results:
        return row['comic_id']
