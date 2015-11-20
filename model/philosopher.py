class Philosopher:
    def __init__(self, philosopherId, name, birthYear, deathYear, comics, bio, portrait):
        import urllib
        self.philosopherId = philosopherId
        self.name = name
        self.birthYear = birthYear
        self.deathYear = deathYear
        self.comics = comics
        self.bio = bio
        self.portrait = portrait
        self.link = "/philosopher/" + urllib.quote(name.replace(" ", "_").encode('utf8'))

    # reverses order of comics.
    def reverseComics(self):
        self.comics = list(reversed(self.comics))

