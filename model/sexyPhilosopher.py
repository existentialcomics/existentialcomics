class SexyPhilosopher:
    def __init__(self, philosopherId, name, image, score):
        import urllib
        self.philosopherId = philosopherId
        self.name = name
        self.image = image
        self.score = score
        self.color = '%0.2X15%0.2X' % (score * 25, (10 - score) * 25); 
