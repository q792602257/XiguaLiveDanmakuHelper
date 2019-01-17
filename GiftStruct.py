import requests


class GiftStruct:
    ID = 0
    count = 0
    giftList={10001: {"Name": "西瓜", "Price": 0}}
    amount = 0

    def __init__(self, json=None):
        if json:
            self.parse(json)

    def parse(self, json):
        if "Msg" in json:
            if "present_end_info" in json["Msg"]:
                self.ID = json["Msg"]['present_end_info']['id']
                self.count = json["Msg"]['present_end_info']['count']
            elif "present_info" in json["Msg"]:
                self.ID = json["Msg"]['present_info']['id']
                self.count = json["Msg"]['present_info']['repeat_count']
        if self.ID in self.giftList:
            self.amount = self.giftList[self.ID]["Price"] * self.count

    @staticmethod
    def update(roomID):
        p = requests.get("https://live.ixigua.com/api/gifts/{roomID}".format(roomID= roomID))
        d = p.json()
        if isinstance(d, int) or "data" not in d:
            print("错误：礼物更新失败")
        else:
            for i in d["data"]:
                GiftStruct.giftList[i["ID"]] = {"Name": i["Name"], "Price": i["DiamondCount"]}

    def __str__(self):
        if self.ID in self.giftList:
            giftN = self.giftList[self.ID]["Name"]
        else:
            giftN = "未知礼物[{}]".format(self.ID)
        return "{count} 个 {name}".format(count= self.count, name= giftN)

    def __unicode__(self):
        return self.__str__()