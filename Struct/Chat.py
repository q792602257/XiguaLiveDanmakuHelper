from .User import User
from .Lottery import Lottery


class Chat:

    content: str =""
    user:    User=None
    filterString:list = ["",]
    isFiltered = False

    def __init__(self, json=None, lottery:Lottery = None):
        if json:
            self.parse(json)
        if lottery:
            self.filterString.append(lottery.content)

    def parse(self, json):
        self.user = User(json)
        if "extra" in json:
            if "content" in json["extra"]:
                self.content = json["extra"]['content']
        if self.content in self.filterString:
            self.isFiltered = True

    def __str__(self):
        return "{} : {}".format(self.user,self.content)

    def __unicode__(self):
        return self.__str__()

