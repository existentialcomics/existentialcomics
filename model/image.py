class Image:
    def __init__(self, filename, comicId, imageId, titleText, altText, altTextReviewed, link):
        self.filename = filename
        self.comicId = comicId
        self.imageId = imageId
        self.titleText = titleText
        self.altTextReviewed = altTextReviewed
        if altText is None:
            self.altText = ""
        else:
            self.altText = altText.decode('utf8')
        self.link    = link
