class Topic:
    def __init__(self, topicId, name, comics):
        import urllib
        self.topic = topicId
        self.name = name
        self.comics = comics
        self.link = "/topic/" + urllib.quote(name.replace(" ", "_").encode('utf8'))
