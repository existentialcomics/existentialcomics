import sqlite3
import markdown
import settings as s
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Markup
from sqlalchemy import create_engine, text

engine = create_engine('mysql://' + s.MYSQL_USER + ':' + s.MYSQL_PASSWORD + '@' + s.MYSQL_HOST + '/' + s.MYSQL_DB, pool_size=20, max_overflow=40, pool_recycle=3600)

def get_db():
    return engine.connect()

def testRegexMatches(level, regex):
	import re
	p = re.compile(regex)
	results = getRegexMatches(level)
	score = 0
	
	resultsMatched = {
		'match': list(),
		'dont' : list(),
		'score': 0
	}

	for i in results['match']:
		m = p.search(i)
		if(m):
			resultsMatched['match'].append(i[:m.start()] + '<b>' + i[m.start():m.end()] + '</b>' + i[m.end():])
		else:
			resultsMatched['match'].append(i)

	for i in results['dont']:
		m = p.search(i)
		if(m):
			resultsMatched['dont'].append(i[:m.start()] + '<b>' + i[m.start():m.end()] + '</b>' + i[m.end():])
		else:
			resultsMatched['dont'].append(i)
	return resultsMatched

def getRegexMatches(level):
	c = get_db()
	t = "select match_word, dont_match_word FROM match_words WHERE level = 'test'"
	results = c.execute(t)
	#results = c.execute(t, level = level)
	resultsMatches = {
		'match' : list(),
		'dont'  : list()
	}
	for row in results:
		resultsMatches['match'].append(row['match_word'])
		resultsMatches['dont'].append(row['dont_match_word'])
	return resultsMatches

def getRandomJoke():
    import random
    c = get_db()
    maxId = 0
    t = text('SELECT MAX(joke_id) as max_id FROM jokes')
    results = c.execute(t)
    for row in results:
        maxId = row['max_id']
    return getJoke(random.randint(1,maxId))


def getJoke(jokeId):
    c = get_db()
    t = text('SELECT joke FROM jokes WHERE joke_id = :joke_id')
    results = c.execute(t, joke_id = jokeId)
    textjoke = ""
    for row in results:
        textjoke = row['joke']
    return textjoke

def updateScores():
    c = get_db()
    t = "select avg(score) as avgScore, philosopher_id, count(*) as votes from sexy_votes GROUP BY philosopher_id"
    results = c.execute(t)
    tu = text("UPDATE sexy_philosopher SET score = :score, vote_total = :votes WHERE philosopher_id = :philosopherId")
    for row in results:
        score = "%0.1f" % row['avgScore']
	votes = row['votes']
        philosopherId = row['philosopher_id']
        c.execute(tu, score = score, philosopherId = philosopherId, votes = votes)
    return 0

def getRandomSexyPhilosopher():
    import random
    c = get_db()
    maxId = 0
    t = text('SELECT MAX(philosopher_id) as max_id FROM sexy_philosopher')
    results = c.execute(t)
    for row in results:
        maxId = row['max_id']
    return getSexyPhilosopher(random.randint(1,maxId))

def getSexyPhilosopher(philosopherId):
    from model.sexyPhilosopher import SexyPhilosopher
    c = get_db()
    name  = None
    image = None
    score = None
    voteTotal = 0
    
    t = text('SELECT name, image, score, vote_total FROM sexy_philosopher WHERE philosopher_id = :philosopherId')
    results = c.execute(t, philosopherId = philosopherId)
    for row in results:
        name = row['name']
        image = row['image']
        score = row['score']
        voteTotal = row['vote_total']

    return SexyPhilosopher(philosopherId, name, image, score, voteTotal)

def getAllSexyPhilosophers():
    from model.sexyPhilosopher import SexyPhilosopher
    c = get_db()
    philosophers = []
    t = text('SELECT philosopher_id, name, image, score, vote_total FROM sexy_philosopher ORDER BY score DESC')
    results = c.execute(t)
    for row in results:
        philosophers.append(SexyPhilosopher(row['philosopher_id'], row['name'], row['image'], row['score'], row['vote_total']))
    return philosophers    

def addVote(philosopherId, score, ip, proxy):
    c = get_db()

    t = text('INSERT INTO sexy_votes (philosopher_id, score, ip, proxy) VALUES (:philosopherId, :score, INET_ATON(:ip), :proxy)')
    c.execute(t, philosopherId=philosopherId, score=score, ip=ip, proxy=proxy)
    return 1

def getAllPhilosophers(orderBy = "birth"):
    c = get_db()

    orderClause = ""
    if orderBy == "birth":
        orderClause = "ORDER BY birth_year"
    elif orderBy == "name":
        orderClause = "ORDER BY name"
    else:
        orderClause = "ORDER BY birth_year"

    t = text('SELECT philosopher_id FROM philosopher ' + orderClause)
    results = c.execute(t)
    philosophers = []
    for row in results:
        philosophers.append(getPhilosopher(row['philosopher_id']))
    return philosophers

def getPhilosophersByComic(comicId):
    c = get_db()

    philosophers = []
    t = text('SELECT philosopher_id FROM philosopher_comic WHERE comic_id = :comicId')
    results = c.execute(t, comicId = comicId)
    for row in results:
        philosophers.append(getPhilosopher(row['philosopher_id']))

    return philosophers

def getPhilosopherByName(philosopherName):
    c = get_db()

    t = text('SELECT philosopher_id FROM philosopher WHERE name = :philosopherName')
    results = c.execute(t, philosopherName = philosopherName)
    philosopherId = None
    for row in results:
        philosopherId = row['philosopher_id']
    if philosopherId is None:
        return None
    return getPhilosopher(philosopherId)

def getPhilosopher(philosopherId):
    from model.philosopher import Philosopher
    c = get_db()
    name = ""
    birthYear = ""
    deathYear = ""
    bio = None
    portrait = None
    orderClause = ""
    t = text('SELECT name, birth_year, death_year, bio, portrait FROM philosopher WHERE philosopher_id = :philosopherId')
    results = c.execute(t, philosopherId = philosopherId)
    for row in results:
        name = row['name']
        bio  = row['bio']
        portrait = row['portrait']
        if (row['birth_year'] is None):
            birthYear = 'Infinity B.C.'
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
    return Philosopher(philosopherId, name, birthYear, deathYear, comics, bio, portrait)

def getAllTopics():
    c = get_db()
    topics = []
    t = text('SELECT topic_id FROM topic ORDER BY topic_name')
    results = c.execute(t)
    for row in results:
        topics.append(getTopic(row['topic_id']))
    return topics      

def getTopic(topicId):
    from model.topic import Topic
    c = get_db()
    t = text('SELECT topic_name FROM topic WHERE topic_id = :topicId')
    results = c.execute(t, topicId = topicId)
    for row in results:
        name = row['topic_name']

    comics = []
    tC = text('SELECT comic_id from topic_comic WHERE topic_id = :topicId')
    resultsComic = c.execute(tC, topicId=topicId)
    for rowCom in resultsComic:
        comics.append(getComic(rowCom['comic_id']))
    return Topic(topicId, name, comics)

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
    #status = call(['perl' , '/home/corey/captchaGen.pl', captcha.question, captcha.imageFile], shell=False)
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

def getAllAlternateComics(orderBy = "date", lang = "en"):
    comics = getComics(None, lang, orderBy, "alternate_comic", "alternate_image")
    comicsWithAlt = []
    for comic in comics:
        comic.link = comic.link.replace('/comic/', '/comic/other/')
        comicsWithAlt.append(comic)
    return comicsWithAlt

def getAllComics(orderBy = "date", lang = "en"):
    comics = getComics(None, lang, orderBy)
    comicsWithAlt = []
    for comic in comics:
        comic.setAltLangs(getAltLanguages(comic.comicId))
        comicsWithAlt.append(comic)
    return comicsWithAlt

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

def getBlog(blogId):
    from model.blog import Blog
    
    c = get_db()
    t = text("SELECT blog_title, blog_text, DATE_FORMAT(date_published,'%m-%d-%Y') as date_published FROM blog WHERE blog_id = :blogId")
    results = c.execute(t, blogId=blogId)
    if results is None:
        return None
    blogTitle, blogText, blogDate = ("", "", "")
    for row in results:
        blogTitle = row['blog_title']
        blogText = Markup(markdown.markdown(row['blog_text']))
        blogDate  = row['date_published']

    return Blog(blogTitle, blogText, blogId, blogDate)

def getAlternateComic(comicId = None, lang="en", orderBy = "date"):
    comics = getComics(comicId, lang, orderBy, "alternate_comic", "alternate_image")
    if comics is None:
        return None
    else:
        comics[0].link = comics[0].link.replace('/comic/', '/comic/other/')
        return comics[0]

def getComic(comicId = None, lang="en", orderBy = "date"):
    comics = getComics(comicId, lang, orderBy)
    if comics is None:
        return None
    elif len(comics) == 0:
        return None
    else:
        return comics[0]

def getComics(comicId = None, lang="en", orderBy = "date", table = "comic", imageTable = "image"):
    from model.comic import Comic
    from model.image import Image

    c = get_db()

    langClause = " WHERE lang = :lang "

    idClause = ""
    if comicId is not None:
        idClause = "AND comic_id = :comicId "

    orderClause = ""
    if orderBy == "date":
        orderClause = "ORDER BY pub_date "
    elif orderBy == "popularity":
        orderClause = "ORDER BY popularity DESC"

    t = text("SELECT comic_id, title, DATE_FORMAT(pub_date, '%a, %d %b %Y %T') as pub_date_rss, explanation, type FROM " + table + " WHERE status = 'active' AND lang = :lang " + idClause + orderClause) 
    results = c.execute(t, comicId = comicId, lang = lang)

    if results is None:
        return None

    title, pubDate, explanation, comicType = ("", "", "", "")

    comics = []
    for row in results:
        title = row['title']
        pubDate = row['pub_date_rss']
        comicIdRow = None
        if (row['explanation']):
            explanation = Markup(markdown.markdown(row['explanation']))
        else:
            explanation = ""
        comicType = row['type']
        comicIdRow = row['comic_id']

        t = text('SELECT filename, image_id, alt_text, external_link FROM ' + imageTable + ' WHERE comic_id = :comicId AND lang = :lang')
        results = c.execute(t, comicId = comicId, lang = lang)
        images = []
        for row in results:
            newImage = Image(s.STATIC_URL + row['filename'], comicId, row['image_id'], row['alt_text'], row['external_link'])
            images.append(newImage)

        comics.append(Comic(title, images, comicIdRow, pubDate, explanation, comicType))
    return comics

def getLatestComics(comicsToGet):
    c = get_db()
    
    t = text('SELECT comic_id FROM comic WHERE lang = "en" AND status = "active" ORDER BY comic_id DESC limit :limit')
    results = c.execute(t, limit = comicsToGet)
    comics = []
    for row in results:
        comics.append(getComic(row['comic_id']))
    return comics

def getMaxBlog():
    c = get_db()
    results = c.execute('SELECT MAX(blog_id) as comic_id FROM blog')
    for row in results:
        return row['comic_id']

def getMaxComic():    
    c = get_db()
    results = c.execute('SELECT MAX(comic_id) as comic_id FROM comic WHERE status = "active"')
    for row in results:
        return row['comic_id']
