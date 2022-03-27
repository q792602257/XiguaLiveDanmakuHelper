import requests
from .User import User
from XiguaMessage_pb2 import GiftMessage


class Gift:
    giftList = {}

    def __init__(self, json=None):
        self.ID = 0
        self.count = 0
        self.user = None
        self.isFinished = False
        self.backupName = None
        if json:
            if type(json) == bytes:
                self.parsePb(json)
            else:
                self.parse(json)

    def parsePb(self, raw):
        _message = GiftMessage()
        _message.ParseFromString(raw)
        self.user = User(_message.user)
        self.ID = _message.giftId
        self.count = _message.repeated
        self.isFinished = _message.isFinished
        self.backupName = _message.commonInfo.displayText.params.gifts.gift.name

    def parse(self, json):
        self.user = User(json)
        if "extra" in json and json["extra"] is not None:
            if "present_info" in json["extra"] and json["extra"]['present_info'] is not None:
                self.ID = int(json["extra"]['present_info']['id'])
                self.count = json["extra"]['present_info']['repeat_count']
            elif "present_end_info" in json["extra"] and json["extra"]['present_end_info'] is not None:
                self.ID = int(json["extra"]['present_end_info']['id'])
                self.count = json["extra"]['present_end_info']['count']

    def isAnimate(self):
        if self.ID != 0 and self.ID in self.giftList:
            if 'combo' in self.giftList[self.ID]:
                return self.giftList[self.ID]["combo"] == False
            elif 'meta' in self.giftList[self.ID] and 'combo' in self.giftList[self.ID]['meta']:
                return self.giftList[self.ID]['meta']["combo"] == False
            elif 'type' in self.giftList[self.ID]:
                return self.giftList[self.ID]["type"] == 2
        return False

    @property
    def name(self):
        if self.ID in self.giftList:
            return self.giftList[self.ID]["name"]
        elif self.backupName is not None:
            return self.backupName
        else:
            return "未知礼物[{}]".format(self.ID)

    def __str__(self):
        return "{user} 送出的 {count} 个 {name}".format(user=self.user, count=self.count, name=self.name)

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return "西瓜礼物【{}(ID:{})】".format(self.name, self.ID)

    @classmethod
    def addGift(cls, _gift):
        if 'id' not in _gift:
            return
        _id = int(_gift["id"])
        cls.giftList[_id] = _gift
