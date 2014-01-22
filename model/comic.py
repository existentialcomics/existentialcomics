class Comic:
    def __init__(self, title, images, comicId, pubDate):
        import settings as s
        self.title = title
        self.images = images
        self.comicId = comicId
        self.pubDate = pubDate
        self.link = "http://" + s.DOMAIN + '/comic/' + str(comicId)
