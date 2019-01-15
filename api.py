import sys

import requests
import time
import ctypes
import os


class UserStruct:
    ID = 0
    name = ""
    brand= ""
    level= 0
    type = 0

    def __init__(self, json=None):
        if json:
            self.parse(json)

    def parse(self, json):
        if "Msg" in json:
            if "user" in json["Msg"]:
                self.ID = json["Msg"]['user']['user_id']
                self.name = json["Msg"]['user']['name']
                self.type = json["Msg"]['user']['user_type']
            if "discipulus_info" in json["Msg"]:
                self.level = json["Msg"]["discipulus_info"]["level"]
                self.brand = json["Msg"]["discipulus_info"]["discipulus_group_title"]
        if self.type is None:
            self.type = 0

    def __str__(self):
        if self.level == 0:
            if self.type != 0:
                return "[]{}".format(self.name)
            return "{}".format(self.name)
        else:
            if self.type != 0:
                return "[{}{}]{}".format(self.brand, self.level, self.name)
            return "<{}{}>{}".format(self.brand,self.level,self.name)


    def __unicode__(self):
        return self.__str__()


class GiftStruct:
    ID = 0
    count = 0

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


def readInput(caption, default, timeout=5):
    start_time = time.time()
    print('{}({})\r\n>'.format(caption,default), end="")
    input = ''
    while True:
        if msvcrt.kbhit():
            chr = msvcrt.getche()
            if ord(chr) == 13:  # enter_key
                break
            elif ord(chr) == 27:
                break
            elif ord(chr) >= 32:  # space_char
                input += str(chr)
        if len(input) == 0 and (time.time() - start_time) > timeout:
            break

    if len(input) > 0:
        print()
        return input
    else:
        print("使用默认值")
        return default


STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12
std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
# 字体颜色定义 ,关键在于颜色编码，由2位十六进制组成，分别取0~f，前一位指的是背景色，后一位指的是字体色
#由于该函数的限制，应该是只有这16种，可以前景色与背景色组合。也可以几种颜色通过或运算组合，组合后还是在这16种颜色中

# Windows CMD命令行 字体颜色定义 text colors
FOREGROUND_BLACK = 0x00 # black.
FOREGROUND_DARKBLUE = 0x01 # dark blue.
FOREGROUND_DARKGREEN = 0x02 # dark green.
FOREGROUND_DARKSKYBLUE = 0x03 # dark skyblue.
FOREGROUND_DARKRED = 0x04 # dark red.
FOREGROUND_DARKPINK = 0x05 # dark pink.
FOREGROUND_DARKYELLOW = 0x06 # dark yellow.
FOREGROUND_DARKWHITE = 0x07 # dark white.
FOREGROUND_DARKGRAY = 0x08 # dark gray.
FOREGROUND_BLUE = 0x09 # blue.
FOREGROUND_GREEN = 0x0a # green.
FOREGROUND_SKYBLUE = 0x0b # skyblue.
FOREGROUND_RED = 0x0c # red.
FOREGROUND_PINK = 0x0d # pink.
FOREGROUND_YELLOW = 0x0e # yellow.
FOREGROUND_WHITE = 0x0f # white.


# Windows CMD命令行 背景颜色定义 background colors
BACKGROUND_BLUE = 0x10 # dark blue.
BACKGROUND_GREEN = 0x20 # dark green.
BACKGROUND_DARKSKYBLUE = 0x30 # dark skyblue.
BACKGROUND_DARKRED = 0x40 # dark red.
BACKGROUND_DARKPINK = 0x50 # dark pink.
BACKGROUND_DARKYELLOW = 0x60 # dark yellow.
BACKGROUND_DARKWHITE = 0x70 # dark white.
BACKGROUND_DARKGRAY = 0x80 # dark gray.
BACKGROUND_BLUE = 0x90 # blue.
BACKGROUND_GREEN = 0xa0 # green.
BACKGROUND_SKYBLUE = 0xb0 # skyblue.
BACKGROUND_RED = 0xc0 # red.
BACKGROUND_PINK = 0xd0 # pink.
BACKGROUND_YELLOW = 0xe0 # yellow.
BACKGROUND_WHITE = 0xf0 # white.


s = requests.Session()

def set_cmd_text_color(color, handle=std_out_handle):
    Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    return Bool

def resetColor():
    set_cmd_text_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)

class XiGuaLiveApi:
    isLive = False
    roomInfo = {}
    roomID = 0
    cursor = ""
    giftList = {10001:"西瓜"}

    def __init__(self, room: int):
        self.room = room
        self.updRoomInfo()
        self.updGiftList()

    def notLiveError(self):
        print("主播未开播")

    def apiChangedError(self, msg:str):
        print(msg)

    def onPresent(self, user:UserStruct, gift:GiftStruct):
        if gift.ID not in self.giftList:
            giftN = "未知礼物：{}".format(gift.ID)
        else:
            giftN = self.giftList[gift.ID]
        return
        print("礼物连击：", user, giftN, "x", gift.count)

    def onPresentEnd(self, user:UserStruct, gift:GiftStruct):
        if gift.ID not in self.giftList:
            self.updGiftList()
            giftN = "未知礼物：{}".format(gift.ID)
        else:
            giftN = self.giftList[gift.ID]
        set_cmd_text_color(BACKGROUND_WHITE | FOREGROUND_BLACK)
        print("感谢", user, "送出的", giftN, "x", gift.count)
        resetColor()

    def onAd(self, i):
        # print(i)
        pass

    def onChat(self, user:UserStruct, content:str):
        print(user, "：", content)
        # pass

    def onEnter(self, user:UserStruct, content:str == ""):
        if content == "":
            if user.name == "三国空白" or user.name == "四维v":
                set_cmd_text_color(FOREGROUND_DARKGRAY)
                print("消息：", user, "进入直播间")
                resetColor()
        else:
            set_cmd_text_color(FOREGROUND_DARKGRAY)
            print("消息：", content.format(user))
            resetColor()

    def onSubscribe(self, user:UserStruct):
        if user.level >= 6 and user.brand == "永恒":
            set_cmd_text_color(FOREGROUND_DARKGRAY)
            print("消息：", user, "关注了主播")
            resetColor()

    def onJoin(self, user:UserStruct):
        set_cmd_text_color(BACKGROUND_WHITE | FOREGROUND_BLACK)
        print("感谢", user, "加入了粉丝团")
        resetColor()

    def onMessage(self, msg:str):
        set_cmd_text_color(FOREGROUND_DARKGRAY)
        print("消息：", msg)
        resetColor()

    def onLike(self, user:UserStruct):
        return
        # set_cmd_text_color(FOREGROUND_DARKGRAY)
        # print("用户", user, "点了喜欢")
        # resetColor()

    def onLeave(self, json:any):
        print("消息：", "主播离开一小会")
        self.debug(json)
        return

    def updGiftList(self):
        p = s.get("https://live.ixigua.com/api/gifts/{roomID}".format(roomID=self.roomID))
        d = p.json()
        self.debug(d)
        if "data" not in d:
            self.warning("Warning: Api Has Changed")
            return
        for i in d["data"]:
            self.debug(i["ID"], i["Name"])
            self.giftList[i["ID"]] = i["Name"]

    def warning(self, *args):
        print(args)

    def debug(self, *args):
        # print(args)
        pass

    def enterRoom(self):
        p = s.post("https://live.ixigua.com/api/room/enter/{roomID}".format(roomID=self.roomID))
        self.debug(p.json())

    def updRoomInfo(self):
        p = s.get("https://live.ixigua.com/api/room/{room}".format(room=self.room))
        d = p.json()
        self.debug(d)
        if "data" not in d:
            self.apiChangedError("数据结构改变，请与我联系")
            self.debug(d)
            return
        self.roomInfo = d["data"]
        print("进入", self.roomInfo["anchorInfo"]["name"], "的直播间")
        if "Id" in d["data"]:
            self.roomID = d["data"]["Id"]
        else:
            self.warning("无法获取RoomID，请与我联系")
        if "FinishTime" in d["data"]:
            self.isLive = False
            self.notLiveError()
        else:
            self.isLive = True

    def getDanmaku(self):
        p = s.get("https://live.ixigua.com/api/msg/list/{roomID}?AnchorID={room}&Cursor={cursor}".format(
            roomID=self.roomID,
            room=self.room,
            cursor=self.cursor
        ))
        d = p.json()
        self.debug(d)
        if "data" not in d:
            self.apiChangedError("数据结构改变，请与我联系")
            self.debug(d)
            return
        if "Extra" not in d["data"]:
            self.apiChangedError("数据结构改变，请与我联系")
            self.debug(d["data"])
            return
        if "Cursor" not in d["data"]["Extra"]:
            self.apiChangedError("数据结构改变，请与我联系")
            self.debug(d["data"])
            return
        else:
            self.cursor = d["data"]["Extra"]["Cursor"]
        if "LiveMsgs" not in d["data"]:
            return
        for i in d['data']['LiveMsgs']:
            if i['Method'] == "VideoLivePresentMessage":
                self.onPresent(UserStruct(i), GiftStruct(i))
            elif i['Method'] == "VideoLivePresentEndTipMessage":
                self.onPresentEnd(UserStruct(i), GiftStruct(i))
            elif i['Method'] == "VideoLiveRoomAdMessage":
                self.onAd(i)
            elif i['Method'] == "VideoLiveChatMessage":
                self.onChat(UserStruct(i), i["Msg"]['content'])
            elif i['Method'] == "VideoLiveMemberMessage":
                self.onEnter(UserStruct(i), i["Msg"]["content"])
            elif i['Method'] == "VideoLiveSocialMessage":
                self.onSubscribe(UserStruct(i))
            elif i['Method'] == "VideoLiveJoinDiscipulusMessage":
                self.onJoin(UserStruct(i))
            elif i['Method'] == "VideoLiveControlMessage":
                print("消息：", "主播离开一小会")
            elif i['Method'] == "VideoLiveDiggMessage":
                self.onLike(UserStruct(i))
            else:
                self.debug(i)


if __name__ == "__main__":
    room = 97621754276 #永恒
    # room = 75366565294
    # room = 83940182312 #Dae
    if len(sys.argv)>1:
        room = int(sys.argv[1])
    resetColor()
    print("西瓜直播弹幕助手 by JerryYan")
    print("正在进入房间", room)
    api = XiGuaLiveApi(room)
    os.system("title {} {}".format(api.roomInfo["anchorInfo"]["name"],"的直播间 --西瓜直播弹幕助手 by JerryYan"))
    api.enterRoom()
    print("="*30)
    while True:
        if api.isLive:
            try:
                api.getDanmaku()
            except Exception as e:
                api.warning(e)
            time.sleep(1)
        else:
            print("主播未开播，等待1分钟后重试")
            time.sleep(60)
            api.updRoomInfo()
