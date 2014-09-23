class Language:
    def __init__(self, lang, langName):
        self.lang = lang
        self.langName = langName
        self.comicLink = None

    # when attached to a specific comic, it will have the link to that comic in this language
    def setComicLink(self, link):
        self.link = link
