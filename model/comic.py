class Comic:
    def __init__(self, title, images, comicId, pubDate, explanation, comicType):
        import settings as s
        self.title = title
        self.images = images
        self.comicId = comicId
        self.pubDate = pubDate
        self.explanation = explanation
        self.comicType = comicType
        self.altLangs = list()
        self.link = "http://" + s.DOMAIN + '/comic/' + str(comicId)

    def setAltLangs(self, languages):
        langs = list()
        for lang in languages:
            lang.setComicLink(self.getLangLink(lang.lang))
        self.altLangs = languages

    def getLangLink(self, lang):
        import settings as s
        return "http://" + s.DOMAIN + '/comic/' + lang + "/" + str(self.comicId)
