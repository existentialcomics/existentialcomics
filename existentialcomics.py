from flask import Flask, render_template, url_for, g, Response, request, make_response, redirect
#from flaskext.markdown import Markdown
#import markdown
from flask.ext.sqlalchemy import SQLAlchemy

import settings as s
import sys
reload(sys)
sys.setdefaultencoding('latin-1')

app = Flask(__name__, static_folder=s.STATIC_URL)
app.debug = True
#Markdown(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost:3036/comic'
db = SQLAlchemy(app)

@app.route('/rss.xml')
def rss():
    import dao
    comics = dao.getLatestComics(s.RSS_LIMIT)
    rss = render_template('rss.xml', comics=comics)
    return Response(rss, mimetype='text/xml')

@app.route('/grammar', methods=['GET', 'POST'])
def grammar():
    import dao
    error = None
    titleImg = s.STATIC_URL + '/titleBlank.jpg'
    if request.method == 'POST':
        solved = dao.checkCaptcha(request.form['captchaSession'], request.form['captchaAnswer'])
        if solved == 1:
            return render_template('grammarSuccess.html', titleImg=titleImg, statis=s.STATIC_URL)
        else:
            error = "Sorry, but you either failed to enter the letters correctly, or failed to identify the grammar mistake"
    captcha = dao.getCaptcha()
    return render_template('grammar.html', titleImg=titleImg, captcha=captcha, error=error, static=s.STATIC_URL)

@app.route('/comic/random')
def random():
    import dao
    import random
    maxComic = dao.getMaxComic()
    curComic = random.randint(1,maxComic)

    seenComics = request.cookies.get('seen')
    seenSet = set()
    seenAry = list()
    if seenComics != None:
        seenAry = seenComics.split(':');
        for i in seenAry:
            seenSet.add(int(i))
        if len(seenSet) + 1 >= maxComic:
            seenAry = list()
        while curComic in seenSet:
            if curComic == maxComic:
                curComic = 1
            else:
                curComic += 1
    return redirect("/comic/" + str(curComic))

@app.route("/")
def home():
    import dao
    return serveComic(dao.getMaxComic())

@app.route('/about')
def serveAbout():
    titleImg = s.STATIC_URL + '/titleArchive.jpg'
    return render_template('about.html', titleImg=titleImg, static=s.STATIC_URL)

@app.route('/archive')
def serveArchiveDefault():
    return serveArchive('byCategory')

@app.route('/archive/<displayMode>')
def serveArchive(displayMode = "byCategory"):
    import dao

    mode = "category"
    if (displayMode.lower() == "byphilosopher"):
        mode = "philosopher"
    
    if (mode == "category"):
        comics = dao.getAllComics()
        seriousComics = list()
        dialogComics  = list()
        jokeComics    = list()
        philosophersPlayComics    = list()
        for comic in comics:
            if (comic.comicType == 'serious'):
                seriousComics.append(comic)
            elif (comic.comicType == 'dialog'):
                dialogComics.append(comic)
            elif (comic.comicType == 'joke'):
                jokeComics.append(comic)
            elif (comic.comicType == 'philosophers play'):
                philosophersPlayComics.append(comic)

        titleImg = s.STATIC_URL + '/titleArchive.jpg'
        return render_template('archive.html', seriousComics=seriousComics, dialogComics=dialogComics, jokeComics=jokeComics, philosophersPlayComics=philosophersPlayComics, titleImg=titleImg, static=s.STATIC_URL)
    if (mode == "philosopher"):
        philosophers = dao.getAllPhilosophers()
        nonPhilosophers = dao.getNonPhilosopherComics()
        titleImg = s.STATIC_URL + '/titleArchive.jpg'
        return render_template('archivePhilosophers.html', philosophers=philosophers, nonPhilosophers=nonPhilosophers, titleImg=titleImg, static=s.STATIC_URL)

@app.route('/comic/<lang>/<curComic>')
def serveComicLang(curComic=None, lang='es'):
    return serveComic(curComic, lang)

@app.route('/comic/<curComicInput>')
def serveComic(curComicInput=None, lang='en'):
    import dao
 
    # cookie which tracks which comics have been seen already   
    seenComics = request.cookies.get('seen')

    curComic = None
    try:
        curComic = long(curComicInput)
    except ValueError:
        return page_not_found(None) 

    maxComic = dao.getMaxComic()
    if curComic is None:
        curComic = maxComic

    comic = dao.getComic(curComic, lang)
    if comic is None:
        return page_not_found(None) 
   
    navMaps = []
    titleMaps = []

    langUrl = ""
    if (lang != 'en'):
        langUrl = lang + '/'

    nextComic = int(comic.comicId) + 1
    firstComic = 1
    prevComic = int(comic.comicId) - 1
    lastComic = int(maxComic)
    if int(comic.comicId) == int(maxComic):
        titleImg = s.STATIC_URL + '/title_last.jpg'
        navImg   = s.STATIC_URL + '/nav_last.jpg'
        lastComic = None
        nextComic = None
    elif int(comic.comicId) == 1:
        titleImg = s.STATIC_URL + '/title_first.jpg'
        navImg   = s.STATIC_URL + '/nav_first.jpg'
        firstComic = None
        prevComic = None
    else:
        titleImg = s.STATIC_URL + '/title.jpg'
        navImg   = s.STATIC_URL + '/nav.jpg'

    seenSet = set()
    seenAry = list()
    seen = 0
    if seenComics != None:
        seenAry = seenComics.split(':');
        for i in seenAry:
            if i == curComic:
                seen = 1
            seenSet.add(int(i))
        if len(seenSet) + 1 >= maxComic:
            seenAry = list()
    if seen == 0:
        seenAry.append(curComic)     

    resp = make_response(render_template('comic.html', comic=comic, titleImg=titleImg, navImg=navImg, titleMaps=titleMaps, firstComic=firstComic, prevComic=prevComic, nextComic=nextComic, lastComic=lastComic, langUrl = langUrl, static=s.STATIC_URL, showAds = s.SHOW_ADS))
    resp.set_cookie('seen', ':'.join(str(x) for x in seenAry))
    resp.set_cookie('len', str(len(seenSet)))
    return resp

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', titleImg='titleBlank.jpg', static=s.STATIC_URL), 404

if __name__ == "__main__":
    app.debug = True
    app.run()
