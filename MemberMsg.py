from User import User


class MemberMsg:
    type:int = 0
    content:str = ""
    user:User = None

    def __init__(self, json=None):
        if json:
            self.parse(json)

    def parse(self, json):
        self.user = User(json)
        if "extra" in json:
            if "action" in json["extra"]:
                self.type = json["extra"]['action']
            elif "content" in json["extra"]:
                self.content = json["extra"]['content']

    def __str__(self):
        if self.type == 3:
            return "{} 被禁言了".format(self.user)
        elif self.type == 4:
            return "{} 被取消禁言了".format(self.user)
        elif self.type == 5:
            return "{} 被任命为房管".format(self.user)
        elif self.type == 1:
            return "{} 进入了房间".format(self.user)
        else:
            print(self.type)
            return self.content.format(self.user)

    def __unicode__(self):
        return self.__str__()