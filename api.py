import sys

from MemberMsg import MemberMsg
from User import User
from Gift import Gift
from Chat import Chat
from Lottery import Lottery
import requests
import time

s = requests.Session()

DEBUG: bool = False


class XiGuaLiveApi:
    isLive: bool = False
    isValidRoom: bool = False
    _rawRoomInfo = {}
    name: str = ""
    roomID: int = 0
    roomTitle: str = ""
    roomLiver: User = None
    roomPopularity: int = 0
    _cursor:str = "0"
    _updRoomCount:int = 0
    lottery:Lottery = None

    def __init__(self, name: str = "永恒de草薙"):
        self.name = name
        self.updRoomInfo()

    def _updateRoomInfo(self, json):
        if "extra" in json:
            if "member_count" in json["extra"] and json["extra"]["member_count"] > 0:
                self.roomPopularity = json["extra"]["member_count"]
        elif "data" in json:
            if "popularity" in json["data"]:
                self.roomPopularity = json["data"]["popularity"]

    def apiChangedError(self, msg: str, *args):
        print(msg)
        print(*args)

    def onPresent(self, gift: Gift):
        print("礼物连击 :", gift)

    def onPresentEnd(self, gift: Gift):
        print("感谢", gift)

    def onAd(self, i):
        # print(i)
        pass

    def onChat(self, chat: Chat):
        if not chat.isFiltered:
            print(chat)

    def onEnter(self, msg: MemberMsg):
        print("提示 :", msg)

    def onSubscribe(self, user: User):
        print("消息 :", user, "关注了主播")

    def onJoin(self, user: User):
        print("欢迎", user, "加入了粉丝团")

    def onMessage(self, msg: str):
        print("消息 :", msg)

    def onLike(self, user: User):
        print("用户", user, "点了喜欢")

    def onLeave(self, json: any):
        print("消息 :", "主播离开了")

    def onLottery(self, i:Lottery):
        print("中奖消息 :", i)

    def updRoomInfo(self):
        if self.isLive:
            p = s.post("https://i.snssdk.com/videolive/room/enter?version_code=730"
                       "&device_platform=android",
                       data="room_id={roomID}&version_code=730"
                       "&device_platform=android".format(roomID=self.roomID),
                       headers={"Content-Type":"application/x-www-form-urlencoded"})
            d = p.json()
            self.isValidRoom = d["base_resp"]["status_code"] == 0
            if d["base_resp"]["status_code"] != 0:
                return False
            if "room" not in d and d["room"] is None:
                self.apiChangedError("Api发生改变，请及时联系我")
                return False
            self._rawRoomInfo = d["room"]
            self.isLive = d["room"]["status"] == 2
            self.roomLiver = User(d)
            self.roomTitle = d["room"]["title"]
            self.roomPopularity = d["room"]["user_count"]
            l = Lottery(d)
            if l.isActive:
                self.lottery = l
            return True
        else:
            p = s.get("https://security.snssdk.com/video/app/search/live/?version_code=730&device_platform=android"
                      "&format=json&keyword={}".format(self.name))
            d = p.json()
            self.isValidRoom = d["base_resp"]["status_code"] == 0
            if "data" in d and d["data"] is not None:
                for i in d["data"]:
                    if i["block_type"] != 0:
                        continue
                    if len(i["cells"]) == 0:
                        return
                    self.isLive = i["cells"][0]["anchor"]["user_info"]["is_living"]
                    self.roomID = int(i["cells"][0]["anchor"]["room_id"])
                    self.roomLiver = User(i["cells"][0])
            if self.isLive:
                return self.updRoomInfo()
            else:
                return False

    @staticmethod
    def findRoomByUserId(userId:int):
        p = s.get("https://live.ixigua.com/api/room?anchorId={room}".format(room=userId))
        if DEBUG:
            print(p.text)
        d = p.json()
        if "data" not in d or "title" not in d["data"] or "id" not in d["data"]:
            XiGuaLiveApi.apiChangedError("无法获取RoomID，请与我联系")
            return XiGuaLiveApi()
        return XiGuaLiveApi(d["data"]["id"])

    @staticmethod
    def searchLive(keyword):
        ret = []
        p = s.get("https://security.snssdk.com/video/app/search/live/?version_code=730&device_platform=android"
                  "&format=json&keyword={}".format(keyword))
        d = p.json()
        if "data" in d:
            for i in d["data"]:
                if i["block_type"] != 0:
                    continue
                for _i in i["cells"]:
                    ret.append(_i["room"])
        return ret

    def getDanmaku(self):
        if not self.isValidRoom:
            self.updRoomInfo()
            return
        p = s.get("https://i.snssdk.com/videolive/im/get_msg?cursor={cursor}&room_id={roomID}"
                  "&version_code=730&device_platform=android".format(
                      roomID=self.roomID,
                      cursor=self._cursor
                  ))
        d = p.json()
        if "data" not in d or "extra" not in d or "cursor" not in d["extra"]:
            if DEBUG:
                print(d)
            self.apiChangedError("数据结构改变，请与我联系")
            return
        else:
            self._cursor = d["extra"]["cursor"]
            if DEBUG:
                print("Cursor", self._cursor)
        for i in d['data']:
            if DEBUG:
                print(i)
            if "common" not in i and "method" not in i["common"]:
                continue
            if i["common"]['method'] == "VideoLivePresentMessage":
                self.onPresent(Gift(i))
            elif i["common"]['method'] == "VideoLivePresentEndTipMessage":
                self.onPresentEnd(Gift(i))
            elif i["common"]['method'] == "VideoLiveRoomAdMessage":
                self.onAd(i)
            elif i["common"]['method'] == "VideoLiveChatMessage":
                self.onChat(Chat(i, self.lottery))
            elif i["common"]['method'] == "VideoLiveMemberMessage":
                self._updateRoomInfo(i)
                self.onEnter(MemberMsg(i))
            elif i["common"]['method'] == "VideoLiveSocialMessage":
                self.onSubscribe(User(i))
            elif i["common"]['method'] == "VideoLiveJoinDiscipulusMessage":
                self.onJoin(User(i))
            elif i["common"]['method'] == "VideoLiveControlMessage":
                print("消息：", "主播离开一小会")
            elif i["common"]['method'] == "VideoLiveDiggMessage":
                self.onLike(User(i))
            else:
                pass
        self._updRoomCount += 1
        if self.lottery is not None:
            self.lottery.update()
        if self._updRoomCount > 120 or len(d['data']) == 0:
            if self.lottery.isFinished:
                self.onLottery(self.lottery)
                self.lottery = None
            self.updRoomInfo()
            self._updRoomCount = 0
            return


if __name__ == "__main__":
    name = "永恒de草薙"
    if len(sys.argv) > 2:
        if sys.argv[-1] == "d":
            DEBUG = True
        name = sys.argv[1]
    print("西瓜直播弹幕助手 by JerryYan")
    api = XiGuaLiveApi(name)
    if not api.isValidRoom:
        print(api.roomID)
        input("房间不存在")
        sys.exit()
    print("进入", api.roomLiver, "的直播间")
    print("=" * 30)
    while True:
        if api.isLive:
            try:
                api.getDanmaku()
            except Exception as e:
                print(e)
            time.sleep(1)
        else:
            print("主播未开播，等待1分钟后重试")
            time.sleep(60)
            api.updRoomInfo()
