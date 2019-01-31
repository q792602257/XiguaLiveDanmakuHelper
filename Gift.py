import requests
from User import User


class Gift:
    ID:int = 0
    count:int = 0
    roomID:int = 0
    giftList:dict = {10001: {"Name": "西瓜", "Price": 0}}
    amount:int = 0
    user:User = None

    def __init__(self, json=None):
        if json:
            self.parse(json)

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
        if self.ID in self.giftList:
            self.amount = self.giftList[self.ID]["Price"] * self.count
        else:
            self.update()

    def update(self):
        p = requests.get("https://i.snssdk.com/videolive/gift/get_gift_list?room_id={roomID}".format(roomID = self.roomID))
        d = p.json()
        if "gift_info" not in d:
            print("错误：礼物更新失败")
        else:
            for i in d["gift_info"]:
                _id = int(i["id"])
                Gift.giftList[_id] = {"Name": i["name"], "Price": i["diamond_count"]}

    def __str__(self):
        if self.ID in self.giftList:
            giftN = self.giftList[self.ID]["Name"]
        else:
            giftN = "未知礼物[{}]".format(self.ID)
        return "{user} 送出的 {count} 个 {name}".format(user= self.user, count= self.count, name= giftN)

    def __unicode__(self):
        return self.__str__()