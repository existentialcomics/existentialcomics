class Comic:
    def __init__(self, title, images, comicId, pubDate):
        self.title = title
        self.images = images
        self.comicId = comicId
        self.pubDate = pubDate
        self.link = 'http://existentialcomics.com/comic/' + str(comicId)
