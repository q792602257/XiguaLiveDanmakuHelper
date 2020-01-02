from .User import User
from .Lottery import Lottery
from XiguaMessage_pb2 import ChatMessage

class Chat:
    content = ""
    user = None
    filterString = ["", ]
    isFiltered = False

    def __init__(self, json=None, lottery: Lottery = None):
        if lottery:
            self.filterString.append(lottery.content)
        if json:
            if type(json) == bytes:
                self.parsePb(json)
            else:
                self.parse(json)

    def parsePb(self, raw):
        _message = ChatMessage()
        _message.ParseFromString(raw)
        self.user = User(_message.user)
        self.content = _message.content
        if self.content in self.filterString:
            self.isFiltered = True

    def parse(self, json):
        self.user = User(json)
        if "extra" in json:
            if "content" in json["extra"]:
                self.content = json["extra"]['content']
        if self.content in self.filterString:
            self.isFiltered = True

    def __str__(self):
        return "{} : {}".format(self.user, self.content)

    def __unicode__(self):
        return self.__str__()
