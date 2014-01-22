from flask import Flask, render_template, url_for, g, Response
import settings as s

app = Flask(__name__, static_folder=s.STATIC_URL)
app.debug = True

@app.route('/rss.xml')
def rss():
    import dao
    comics = dao.getLatestComics(s.RSS_LIMIT)
    rss = render_template('rss.xml', comics=comics)
    return Response(rss, mimetype='text/xml')

@app.route('/comic/random')
def random():
    import dao
    maxComic = dao.getMaxComic()
    import random
    curComic = random.randint(1,maxComic)
    return serveComic(curComic)

@app.route("/")
def home():
    import dao
    return serveComic(dao.getMaxComic())

@app.route('/comic/<curComic>')
def serveComic(curComic=None):
    import dao
    maxComic = dao.getMaxComic()
    if curComic is None:
        curComic = maxComic

    comic = dao.getComic(curComic)
    if comic is None:
        return page_not_found(None) 
   
    navMaps = []
    titleMaps = []

    nextComic = int(comic.comicId) + 1
    firstComic = 1
    prevComic = int(comic.comicId) - 1
    lastComic = int(maxComic)
    if int(comic.comicId) == int(maxComic):
        titleImg = s.STATIC_URL + 'title_last.jpg'
        navImg   = s.STATIC_URL + 'nav_last.jpg'
        lastComic = None
        nextComic = None
    elif int(comic.comicId) == 1:
        titleImg = s.STATIC_URL + 'title_first.jpg'
        navImg   = s.STATIC_URL + 'nav_first.jpg'
        firstComic = None
        prevComic = None
    else:
        titleImg = s.STATIC_URL + 'title.jpg'
        navImg   = s.STATIC_URL + 'nav.jpg'

    return render_template('comic.html', comic=comic, titleImg=titleImg, navImg=navImg, titleMaps=titleMaps, firstComic=firstComic, prevComic=prevComic, nextComic=nextComic, lastComic=lastComic, static=s.STATIC_URL)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', titleImg='titleBlank.jpg', static=s.STATIC_URL), 404

if __name__ == "__main__":
    app.debug = True
    app.run()
