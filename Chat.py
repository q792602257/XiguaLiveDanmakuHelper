from User import User

class Chat:

    content: str =""
    user:    User=None

    def __init__(self, json=None):
        if json:
            self.parse(json)

    def parse(self, json):
        self.user = User(json)
        if "extra" in json:
            if "content" in json["extra"]:
                self.content = json["extra"]['content']

    def __str__(self):
        return "{} : {}".format(self.user,self.content)

    def __unicode__(self):
        return self.__str__()

