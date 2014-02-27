import sqlite3
import settings as s

def get_db():
    return sqlite3.connect(s.DATABASE)

def getComic(comicId):
    from model.comic import Comic
    from model.image import Image

    c = get_db().cursor()
    params = (comicId,)
    c.execute('SELECT title, pub_date, explanation FROM comic WHERE comic_id = ?', params)

    results = c.fetchone()
    if results is None:
        return None

    title   = results[0]
    pubDate = results[1]
    explanation = results[2]

    c.execute('SELECT filename, image_id, alt_text FROM image WHERE comic_id = ?', params)
    images = []
    for row in c:
        newImage = Image(s.STATIC_URL + row[0], comicId, row[1], row[2])
        images.append(newImage)

    return Comic(title, images, comicId, pubDate, explanation)

def getLatestComics(comicsToGet):
    c = get_db().cursor()
    params = (comicsToGet,)
    #c.execute('SELECT comic_id FROM comic ORDER BY pub_date DESC limit ?', params)
    c.execute('SELECT comic_id FROM comic ORDER BY comic_id DESC limit ?', params)
    comics = []
    for row in c:
        comics.append(getComic(row[0]))
    return comics

def getMaxComic():    
    c = get_db().cursor()
    c.execute('SELECT MAX(comic_id) FROM comic')
    maxRow = c.fetchone()
    return maxRow[0]
