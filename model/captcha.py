class Captcha:
    def __init__(self, question, answer):
        import settings as s
        import uuid
        session = uuid.uuid1()
        self.session   = session.hex
        self.question  = question
        self.answer    = answer
        self.imageUrl  = s.STATIC_LOCAL_URL + 'captcha/' + session.hex + '.gif'
        self.imageFile = s.STATIC_LOCAL_DIR + 'captcha/' + session.hex + '.gif'
