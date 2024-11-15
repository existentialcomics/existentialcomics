from flask import Flask, render_template, url_for, g, Response, request, make_response, redirect, session
#from flaskext.markdown import Markdown
#import markdown
# from flask.ext.sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
# from werkzeug.contrib.cache import MemcachedCache
from datetime import date

import settings as s
import sys
# reload(sys)
# sys.setdefaultencoding('latin-1')
#sys.setdefaultencoding('utf8')

app = Flask(__name__, static_folder=s.STATIC_URL)
app.debug = False
app.secret_key = app.config['SECRET_KEY']
app.config['SESSION_TYPE'] = 'filesystem'

#Markdown(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['CACHE_TYPE'] = 'memcached'
app.config['CACHE_MEMCACHED_SERVERS'] = ['localhost:11211']

app.cache = Cache(app)
# cache = MemcachedCache(['localhost:11211'])
db = SQLAlchemy(app)

def is_cache_off():
    return False

@app.route("/")
def home():
    import dao
    import re
    p = re.compile('.*philosophy.sexy', re.IGNORECASE)
    if ('Host' in request.headers):
        host = request.headers['Host']
        m = p.match(host)
        if (m):
            return sexyRandom()
    return serveComic(dao.getMaxComic())

#@app.route('/marx-vs-smith', methods=['GET', 'POST'])
#def marxVsSmith():
#    import dao
#
#    if not 'correct' in session:
#        session['correct'] = 0
#    if not 'incorrect' in session:
#        session['incorrect'] = 0
#    if not 'questionsTaken' in session:
#        session['questionsTaken'] = 0
#
#    maxId = dao.getLastQuestion(1)
#    questionCount = dao.getQuestionNumber(1)
#    print "begin"
#
#    if request.method == 'POST':
#        if (request.form['nextQuestion'] == '1'):
#            if 'lastQuestionId' in session:
#                nextQuestion = dao.getNextQuestion(1,session['lastQuestionId'])
#            else:
#                nextQuestion = dao.getNextQuestion(1)
#
#            if not nextQuestion is None:
#                session['lastQuestionId'] = nextQuestion['question_id']
#            else:
#                questions = dao.getQuestions(1)
#                answers = {}
#                for question in questions:
#                    print question['answer']
#                    if question['answer'] == session['answerFor_' + str(question['question_id'])]:
#                        answers[question['question_id']] = 1
#                    else:
#                        answers[question['question_id']] = 0
#
#                totalQuestions = session['correct'] + session['incorrect']
#                questions = dao.getQuestions(1)
#
#                return render_template('marxVsSmithDone.html', answers=answers, questions=questions, totalCorrect=session['correct'], totalIncorrect=session['incorrect'], totalQuestions=totalQuestions, static=s.STATIC_URL)
#                    
#            return render_template('marxVsSmith.html', nextQuestion=nextQuestion, answer=0, static=s.STATIC_URL)
#
#        ### submitted an answer
#        else: 
#            nextQuestion = dao.getQuestion(session['lastQuestionId'])
#
#            lastAnswer = dao.checkQuestion(request.form['questionId'])
#            correct = (str(lastAnswer) == str(request.form['questionAnswer']))
#            session['answerFor_' + str(request.form['questionId'])] = str(request.form['questionAnswer'])
#
#            if correct == True:
#                session['correct'] += 1
#            else:
#                session['incorrect'] += 1
#
#            isLastQuestion = (str(nextQuestion['question_id']) == str(maxId))
#            return render_template('marxVsSmith.html', correct=correct, isLastQuestion=isLastQuestion, totalCorrect=session['correct'], totalIncorrect=session['incorrect'], nextQuestion=nextQuestion, answer=lastAnswer, static=s.STATIC_URL)
#        
#    else: # GET
#        session.clear()
#        if 'lastQuestionId' in session:
#            nextQuestion = dao.getQuestion(session['lastQuestionId'])
#        else:
#            nextQuestion = dao.getNextQuestion(1)
#            session['lastQuestionId'] = nextQuestion['question_id']
#                
#        return render_template('marxVsSmith.html', nextQuestion=nextQuestion, static=s.STATIC_URL)

@app.route('/store')
def store():
    return redirect('http://www.shareasale.com/r.cfm?B=793288&U=1186465&M=5108&urlink=', code=302)

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

@app.route('/blog')
def blogMain():
    return blog(None, None)

@app.route('/vote', methods=['GET', 'POST'])
def sexyRandom():
    return sexyMain(None)

@app.route('/vote/<philosopherId>', methods=['GET', 'POST'])
def sexyMain(philosopherId = None):
    import dao
    titleImg = s.STATIC_URL + '/sexyHeader.png'
    prevPhilosopher = None

    if request.method == 'POST':
        ip = request.remote_addr
        proxy = None
        if request.headers.getlist("X-Forwarded-For"):
            proxy = ', '.join(request.headers.getlist("X-Forwarded-For"))
        dao.addVote(request.form['philosopherId'], request.form['score'], ip, proxy)
        prevPhilosopher = dao.getSexyPhilosopher(request.form['philosopherId'])


    philosopher = None
    if philosopherId is None:
        philosopher = dao.getRandomSexyPhilosopher()
    else:
        philosopher = dao.getSexyPhilosopher(philosopherId)
    
    return render_template('sexy.html', titleImg=titleImg, philosopher=philosopher, prevPhilosopher = prevPhilosopher, name = philosopher.name, static=s.STATIC_URL, showAds = s.SHOW_ADS)

@app.route('/comics/319')
def secretUrl():
    #d0 = date(2013, 11, 12)
    d0 = date(2023, 11, 13)
    today = date.today()
    delta = today - d0
    kantDays = delta.days

    return render_template('secret.html', static=s.STATIC_URL, showAds = s.SHOW_ADS, kantDays=kantDays)

@app.route('/ranking')
def sexyRanking():
    import dao
    titleImg = s.STATIC_URL + '/sexyHeader.png'
    philosophers = dao.getAllSexyPhilosophers()
    return render_template('sexyRanking.html', titleImg=titleImg, philosophers = philosophers, static=s.STATIC_URL, showAds = s.SHOW_ADS)

@app.route('/sexy/upload', methods=['GET', 'POST'])
def sexyUpload():
    import dao
    titleImg = s.STATIC_URL + '/titleArchive.jpg'
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
        dao.createPhilosopher(request.form['philosopherId'], request.form['score'], request.remote_addr)
    return render_template('sexyUploadDone.html', titleImg=titleImg, static=s.STATIC_URL, showAds = s.SHOW_ADS)

@app.route('/blog/<blogId>/<blogTitle>')
@app.cache.memoize(50, unless=is_cache_off)
def blog(blogId=None, blogTitle=None):
    import dao

    titleImg = s.STATIC_URL + '/titleArchive.jpg'

    if blogId is None:
        blogId = dao.getMaxBlog()
    blog = dao.getBlog(blogId)   
    return render_template('blog.html', titleImg=titleImg, blog=blog, static=s.STATIC_URL, showAds = s.SHOW_ADS)

@app.route('/patreon')
def patreon():
    return serveComic(53, "en")

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
            if i.isdigit():
                seenSet.add(int(i))
        if len(seenSet) + 1 >= maxComic:
            seenAry = list()
        while curComic in seenSet:
            if curComic == maxComic:
                curComic = 1
            else:
                curComic += 1
    return redirect("/comic/" + str(curComic))


@app.route('/about')
def serveAbout():
    titleImg = s.STATIC_URL + '/titleArchive.jpg'
    return render_template('about.html', titleImg=titleImg, static=s.STATIC_URL)

@app.route('/unofficialComics')
def serveArchiveOther():
    import dao
    comics = dao.getAllAlternateComics("date", "en")
    titleImg = s.STATIC_URL + '/titleArchive.jpg'
    return render_template('archiveOther.html', comics=comics, titleImg=titleImg, static=s.STATIC_URL)

@app.route('/archive')
def serveArchiveDefault():
    return serveArchive('byCategory')

@app.route('/archive/<displayMode>/<minorSort>')
@app.cache.memoize(600, unless=is_cache_off)
def serveArchiveSorted(displayMode = "byCategory", minorSort = None):
    return serveArchive(displayMode, minorSort)

@app.route('/archive/<displayMode>')
@app.cache.memoize(600, unless=is_cache_off)
def serveArchive(displayMode = "byCategory", minorSort = None):
    import dao

    mode = "category"
    if (displayMode.lower() == "byphilosopher"):
        mode = "philosopher"
    if (displayMode.lower() == "bydate"):
        mode = "date"
    if (displayMode.lower() == "other"):
        mode = "other"
    if (displayMode.lower() == "bypopularity"):
        mode = "popularity"
    if (displayMode.lower() == "bytopic"):
        mode = "topic"

    if (mode == "other"):
        comics = dao.getAllAlternateComics("date", "en")
        titleImg = s.STATIC_URL + '/titleArchive.jpg'
        return render_template('archiveOther.html', comics=comics, titleImg=titleImg, static=s.STATIC_URL)

    if (mode == "popularity"):    
        comics = dao.getAllComics("popularity", "en")
        titleImg = s.STATIC_URL + '/titleArchive.jpg'
        return render_template('archivePopularity.html', comics=comics, titleImg=titleImg, static=s.STATIC_URL)

    if (mode == "date"):    
        comics = dao.getAllComics("date", "en")
        titleImg = s.STATIC_URL + '/titleArchive.jpg'
        return render_template('archiveDate.html', comics=comics, titleImg=titleImg, static=s.STATIC_URL)

    if (mode == "category"):
        comics = dao.getAllComics()
        seriousComics = list()
        dialogComics  = list()
        jokeComics    = list()
        philosophersPlayComics    = list()
        superheroComics = list()
        for comic in comics:
            if (comic.comicType == 'serious'):
                seriousComics.append(comic)
            elif (comic.comicType == 'dialog'):
                dialogComics.append(comic)
            elif (comic.comicType == 'joke'):
                jokeComics.append(comic)
            elif (comic.comicType == 'philosophers play'):
                philosophersPlayComics.append(comic)
            elif (comic.comicType == 'superhero'):
                superheroComics.append(comic)

        titleImg = s.STATIC_URL + '/titleArchive.jpg'
        return render_template('archiveCategory.html', seriousComics=seriousComics, dialogComics=dialogComics, jokeComics=jokeComics, philosophersPlayComics=philosophersPlayComics, superheroComics=superheroComics, titleImg=titleImg, static=s.STATIC_URL)

    if (mode == "philosopher"):
        philosophers = dao.getAllPhilosophers()
        if minorSort == 'appearance':
	        philosophers.sort(key=lambda x: len(x.comics), reverse=True)
        if minorSort == 'name':
	        philosophers.sort(key=lambda x: x.name, reverse=False)
        # nonPhilosophers = dao.getNonPhilosopherComics()
        nonPhilosophers = []
        titleImg = s.STATIC_URL + '/titleArchive.jpg'
        return render_template('archivePhilosophers.html', philosophers=philosophers, nonPhilosophers=nonPhilosophers, titleImg=titleImg, static=s.STATIC_URL)

    if (mode == "topic"):
        topics = dao.getAllTopics()
        #nonPhilosophers = dao.getNonPhilosopherComics()
        titleImg = s.STATIC_URL + '/titleArchive.jpg'
        return render_template('archiveTopics.html', topics=topics, titleImg=titleImg, static=s.STATIC_URL)

@app.route('/philosopher/<philosopherName>')
@app.cache.memoize(600, unless=is_cache_off)
def servePhilosopher(philosopherName=None, lang='en'):
    import dao
    import urllib
 
    philosopher = dao.getPhilosopherByName(urllib.parse.unquote(philosopherName.replace("_", " ")))
    if philosopher is None:
        return page_not_found(None) 
    
    titleImg = s.STATIC_URL + '/title.jpg'

    philosopher.reverseComics()

    return render_template('comicPhilosopher.html', philosopher=philosopher, titleImg=titleImg, static=s.STATIC_URL, showAds = s.SHOW_ADS)

@app.route('/comic/<lang>/<curComic>')
@app.cache.memoize(50, unless=is_cache_off)
def serveComicLang(curComic=None, lang='es'):
    return serveComic(curComic, lang)

@app.route('/update-text/<curComicInput>', methods=['GET', 'POST'])
def updateText(curComicInput=None, lang='en'):
    import dao

    curComic = None
    try:
        curComic = curComicInput
    except ValueError:
        return page_not_found(None) 

    if curComic is None:
        return page_not_found(None) 

    if request.method == 'POST':
        for fieldname, value in request.form.items():
            fieldAry = fieldname.split('-')

            if fieldAry[0] == 'imagetext':
                if s.CAN_UPDATE:
                    dao.updateText(fieldAry[1], value)
                else:
                    dao.suggestText(fieldAry[1], value)
        return suggestEdit();

    comic = dao.getComic(curComic, lang)
    if comic is None:
        return page_not_found(None) 

    philosophers = dao.getPhilosophersByComic(comic.comicId)

    langUrl = ""
    if (lang != 'en'):
        langUrl = lang + '/'

    maxComic = dao.getMaxComic()
    if curComic is None:
        curComic = maxComic

    resp = make_response(render_template('editText.html', comic=comic, philosophers=philosophers,maxComic=maxComic,langUrl = langUrl, static=s.STATIC_URL))
    return resp

@app.route('/suggestEdit')
def suggestEdit():
    import dao

    comicId = dao.getReviewableComicId()

    dao.suggestTextPageload(comicId)

    if comicId is None:
        return redirect('/', code=302)

    return redirect('/update-text/' + str(comicId), code=302)

@app.route('/comic/<curComicInput>')
@app.cache.memoize(50, unless=is_cache_off)
def serveComic(curComicInput=None, lang='en'):
    import dao

    #d0 = date(2013, 11, 12)
    d0 = date(2023, 11, 13)
    today = date.today()
    delta = today - d0
    kantDays = delta.days

    # cookie which tracks which comics have been seen already   
    seenComics = request.cookies.get('seen')

    curComic = None
    try:
        curComic = curComicInput
    except ValueError:
        return page_not_found(None) 

    maxComic = dao.getMaxComic()
    if curComic is None:
        curComic = maxComic

    comic = dao.getComic(curComic, lang)
    if comic is None:
        return page_not_found(None) 
   
    philosophers = dao.getPhilosophersByComic(comic.comicId)

    joke = dao.getRandomJoke()

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
            if i.isdigit():
                if i == curComic:
                    seen = 1
                seenSet.add(int(i))
        if len(seenSet) + 1 >= maxComic:
            seenAry = list()
    if seen == 0:
        seenAry.append(curComic)     

    resp = make_response(render_template('comic.html', comic=comic, philosophers=philosophers,titleImg=titleImg, navImg=navImg, titleMaps=titleMaps, firstComic=firstComic, prevComic=prevComic, nextComic=nextComic, lastComic=lastComic, langUrl = langUrl, static=s.STATIC_URL, showAds = s.SHOW_ADS, kantDays=kantDays, joke=joke))
    resp.set_cookie('seen', ':'.join(str(x) for x in seenAry))
    resp.set_cookie('len', str(len(seenSet)))
    return resp

@app.route('/comic/other/<curComicInput>')
@app.cache.memoize(50, unless=is_cache_off)
def serveAlternateComic(curComicInput=None, lang='en'):
    import dao
    curComic = None
    try:
        curComic = curComicInput
    except ValueError:
        return page_not_found(None)
    comic = dao.getAlternateComic(curComic)
    if comic is None:
        return page_not_found(None)
    titleImg = s.STATIC_URL + '/title.jpg'
    return make_response(render_template('comicOther.html', comic=comic, titleImg=titleImg, static=s.STATIC_URL, showAds = s.SHOW_ADS))

@app.route('/joke/random')
def random_joke():
	import dao
	joke = dao.getRandomJoke()
	return joke

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', titleImg='titleBlank.jpg', static=s.STATIC_URL), 404

if __name__ == "__main__":
    app.debug = True
    app.run()
