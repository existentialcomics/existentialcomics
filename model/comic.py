class Comic:
    def __init__(self, title, images, comicId, pubDate, explanation):
        import settings as s
        self.title = title
        self.images = images
        self.comicId = comicId
        self.pubDate = pubDate
        self.explanation = explanation
        self.link = "http://" + s.DOMAIN + '/comic/' + str(comicId)
