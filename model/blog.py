class Blog:
    def __init__(self, title, text, blogId, pubDate):
        import settings as s
        import re
        self.title = title
        self.text = text
        self.blogId = blogId
        self.pubDate = pubDate
        cleanTitle = re.sub('\s', '_', title)
        cleanTitle = re.sub('[^A-Za-z0-0]', '', cleanTitle)
        self.link = "http://" + s.DOMAIN + '/blog/' + str(blogId) + '/' + cleanTitle
