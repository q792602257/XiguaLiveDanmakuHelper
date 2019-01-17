import msvcrt
import sys
from UserStruct import UserStruct
from GiftStruct import GiftStruct
import requests
import time
import ctypes
import os


def warning(*args):
    print(*args)


def debug(*args):
    # print(args)
    pass




def readInput(caption, default, timeout:int=5):
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
            elif ord(chr) == 8:
                if input != "":
                    input = input[:-1]
            elif 32 <= ord(chr) <= 126:  # space_char
                input += chr.decode("utf8")
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

    def __init__(self, room: int):
        self.room = room
        self.updRoomInfo()
        GiftStruct.update(self.roomID)

    def notLiveError(self):
        print("主播未开播")

    def apiChangedError(self, msg:str):
        print(msg)

    def onPresent(self, user:UserStruct, gift:GiftStruct):
        return
        # print("礼物连击：", user, "的", gift)

    def onPresentEnd(self, user:UserStruct, gift:GiftStruct):
        set_cmd_text_color(BACKGROUND_WHITE | FOREGROUND_BLACK)
        print("感谢", user, "送出的", gift)
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
        debug(json)
        return

    def enterRoom(self):
        p = s.post("https://live.ixigua.com/api/room/enter/{roomID}".format(roomID=self.roomID))
        debug(p.json())

    def updRoomInfo(self):
        p = s.get("https://live.ixigua.com/api/room/{room}".format(room=self.room))
        d = p.json()
        debug(d)
        if "data" not in d:
            self.apiChangedError("数据结构改变，请与我联系")
            debug(d)
            return
        self.roomInfo = d["data"]
        print("进入", self.roomInfo["anchorInfo"]["name"], "的直播间")
        if "Id" in d["data"]:
            self.roomID = d["data"]["Id"]
        else:
            warning("无法获取RoomID，请与我联系")
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
        debug(d)
        if "data" not in d:
            self.apiChangedError("数据结构改变，请与我联系")
            debug(d)
            return
        if "Extra" not in d["data"]:
            self.apiChangedError("数据结构改变，请与我联系")
            debug(d["data"])
            return
        if "Cursor" not in d["data"]["Extra"]:
            self.apiChangedError("数据结构改变，请与我联系")
            debug(d["data"])
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
                debug(i)


if __name__ == "__main__":
    room = 97621754276 #永恒
    # room = 75366565294
    # room = 83940182312 #Dae
    resetColor()
    if len(sys.argv)>1:
        room = int(sys.argv[1])
    else:
        try:
            room = int(readInput("请输入房间号，默认为永恒的直播间", room, 3))
        except ValueError:
            pass
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
                warning(e)
            time.sleep(1)
        else:
            print("主播未开播，等待1分钟后重试")
            time.sleep(60)
            api.updRoomInfo()
