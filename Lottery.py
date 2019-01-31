import requests

from LuckyUser import LuckyUser


class Lottery:
    ID: int = 0
    isActive = False
    content = ""
    isFinished = False
    luckyUsers = []
    joinedUserCount = 0
    prizeName = ""

    def __init__(self, json=None):
        if json:
            self.parse(json)

    def parse(self, json):
        if "lottery_info" not in json or json["lottery_info"] is not None:
            self.isActive = int(json["lottery_info"]["status"]) > 0
            self.ID = json["lottery_info"]["lottery_id"]
            for i in json["lottery_info"]['conditions']:
                if i['type'] != 3:
                    continue
                self.content = i["content"]
            self.joinedUserCount = int(json["lottery_info"]["candidate_num"])
            self.prizeName = json["lottery_info"]["prize_info"]["name"]

    def checkFinished(self):
        p = requests.get("https://i.snssdk.com/videolive/lottery/check_user_right?lottery_id={}"
                         "&version_code=730&device_platform=android".format(
            self.ID
        ))
        d = p.json()
        if d["base_resp"]["status_code"] != 0:
            self.isActive = False
            self.isFinished = False
            return
        self.isActive = int(d["lottery_info"]["status"]) == 1
        self.isFinished = int(d["lottery_info"]["status"]) == 2
        self.joinedUserCount = int(d["lottery_info"]["candidate_num"])
        if self.isFinished:
            for i in d["lottery_info"]["lucky_users"]:
                self.luckyUsers.append(LuckyUser(i))

    def __str__(self):
        if self.isFinished:
            ret = "恭喜以下中奖用户：\n"
            for i in self.luckyUsers:
                ret += "> {} {}\n".format(i,self.prizeName)
            ret += "> 参与人数：{}".format(self.joinedUserCount)
            return ret
        elif self.isActive:
            return "正在抽奖中。。。\n" \
                   "> 参与人数：{}".format(self.joinedUserCount)
        else:
            return "抽奖已失效"
