import requests
from .User import User
from XiguaMessage_pb2 import GiftMessage


class Gift:
    roomID = 0
    giftList = {}

    def __init__(self, json=None):
        self.ID = 0
        self.count = 0
        self.amount = 0
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
        self.count = _message.combo
        self.isFinished = _message.isFinished
        self.backupName = _message.commonInfo.displayText.params.gifts.gift.name

    def parse(self, json):
        self.user = User(json)
        if "common" in json and json["common"] is not None:
            if Gift.roomID != int(json["common"]["room_id"]):
                Gift.roomID = int(json["common"]["room_id"])
                self.update()
        if "extra" in json and json["extra"] is not None:
            if "present_info" in json["extra"] and json["extra"]['present_info'] is not None:
                self.ID = int(json["extra"]['present_info']['id'])
                self.count = json["extra"]['present_info']['repeat_count']
            elif "present_end_info" in json["extra"] and json["extra"]['present_end_info'] is not None:
                self.ID = int(json["extra"]['present_end_info']['id'])
                self.count = json["extra"]['present_end_info']['count']
        if self.ID != 0 and self.ID in self.giftList:
            self.amount = self.giftList[self.ID]["Price"] * self.count
        else:
            self.update()

    @staticmethod
    def update():
        p = requests.get("https://i.snssdk.com/videolive/gift/get_gift_list?room_id={roomID}"
                         "&version_code=800&device_platform=android".format(roomID=Gift.roomID))
        d = p.json()
        if "gift_info" not in d:
            print("错误：礼物更新失败")
        else:
            for i in d["gift_info"]:
                _id = int(i["id"])
                Gift.giftList[_id] = {"Name": i["name"], "Price": i["diamond_count"], "Type": i["type"]}

    def isAnimate(self):
        return self.ID != 0 and self.ID in self.giftList and self.giftList[self.ID]["Type"] == 2

    def _getGiftName(self):
        if self.ID in self.giftList:
            return self.giftList[self.ID]["Name"]
        elif self.backupName is not None:
            return self.backupName
        else:
            return "未知礼物[{}]".format(self.ID)

    def __str__(self):
        return "{user} 送出的 {count} 个 {name}".format(user=self.user, count=self.count, name=self._getGiftName())

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return "西瓜礼物【{}(ID:{})】".format(self._getGiftName(), self.ID)
