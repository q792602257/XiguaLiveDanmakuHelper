# coding=utf-8
import json
import sys
import random

from Struct.MemberMsg import MemberMsg
from Struct.User import User
from Struct.Gift import Gift
from Struct.Chat import Chat
from Struct.Lottery import Lottery
import requests
import time
from datetime import datetime, timedelta

DEBUG = False
COMMON_GET_PARAM = (
    "&iid=96159232732&device_id=55714661189&channel=xiaomi&aid=32&app_name=video_article&version_code=816"
    "&version_name=8.1.6&device_platform=android&ab_version=941090,785218,668858,1046292,1073579,830454,956074,929436,"
    "797199,1135476,1179370,994679,959010,900042,1113833,668854,1193963,901277,1043330,1038721,994822,1002058,1230687,"
    "1189797,1143356,1143441,1143501,1143698,1143713,1371009,1243997,1392586,1395695,1395486,1398858,668852,668856,"
    "668853,1186421,668851,668859,999124,668855,1039075&device_type=MI+8+SE&device_brand=Xiaomi&language=zh"
    "&os_api=28&os_version=9&openudid=70d6668d41512c39&manifest_version_code=412&update_version_code=81606"
    "&_rticket={TIMESTAMP:.0f}&cdid_ts={TIMESTAMP:.0f}&fp=a_fake_fp&tma_jssdk_version=1290000"
    "&cdid=ed4295e8-5d9a-4cb9-b2a2-04009a3baa2d&oaid=a625f466e0975d42")
SEARCH_USER_API = (
    "https://security.snssdk.com/video/app/search/live/?format=json&search_sug=0&forum=0&m_tab=live&is_native_req=0"
    "&offset=0&from=live&en_qc=1&pd=xigua_live&ssmix=a{COMMON}&keyword={keyword}")
USER_INFO_API = "https://is.snssdk.com/video/app/user/home/v7/?to_user_id={userId}{COMMON}"
COMMON_HEADERS = {
    "sdk-version": '1',
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9) VideoArticle/8.1.6 cronet/TTNetVersion:b97574c0 2019-09-24",
    "Accept-Encoding": "gzip, deflate"
}


class XiGuaLiveApi:

    def __init__(self, name=None):
        """
        Api类
        Init Function
        :param name: class:str|User: 主播名
        """
        if name is None:
            name = "永恒de草薙"
        if type(name) == User:
            self.roomLiver = name
            self.name = name.name
        else:
            self.name = str(name)
        self.isLive = False
        self.isValidRoom = False
        self._rawRoomInfo = {}
        self.roomID = 0
        self.roomLiver = None
        self.roomPopularity = 0
        self._cursor = "0"
        self.lottery = None
        self.s = requests.session()
        self.s.headers.update(COMMON_HEADERS)
        self._updRoomAt = datetime.now()
        self.updRoomInfo(True)

    def _updateRoomPopularity(self, _data):
        """
        更新房间人气的方法
        Update Room Popularity
        :param _data: Received Message
        """
        if "extra" in _data:
            if "member_count" in _data["extra"] and _data["extra"]["member_count"] > 0:
                self.roomPopularity = _data["extra"]["member_count"]
        elif "data" in _data:
            if "popularity" in _data["data"]:
                self.roomPopularity = _data["data"]["popularity"]

    @staticmethod
    def apiChangedError(msg: str, *args):
        """
        API发生更改时的提示
        Warning while Detected Api has Changed
        :param msg: 提示信息
        :param args: DEBUG模式下，显示更多信息
        """
        print(msg)
        if DEBUG:
            print(*args)

    def onPresent(self, gift: Gift):
        """
        礼物连击中的消息
        Message On Sending Presents
        :param gift: Struct of Gift Message
        """
        print("礼物连击 :", gift)

    def onPresentEnd(self, gift: Gift):
        """
        礼物送完了的提示信息
        Message On Finished Send Present
        :param gift: Struct of Gift Message
        """
        print("感谢", gift)

    def onAd(self, i):
        """
        全局广播
        All Channel Broadcasting Message( Just An Ad )
        :param i: JSON DATA if you wanna using it
        """
        # print(i)
        pass

    def onChat(self, chat: Chat):
        """
        聊天信息
        On Chatting
        :param chat: Struct of Chat Message
        """
        if not chat.isFiltered:
            print(chat)

    def onEnter(self, msg: MemberMsg):
        """
        进入房间消息
        On Entering Room
        :param msg: Struct of Member Message
        """
        print("提示 :", msg)

    def onSubscribe(self, user: User):
        """
        关注主播时的消息
        On Subscribe
        :param user: Struct of User Message
        """
        print("消息 :", user, "关注了主播")

    def onJoin(self, user: User):
        """
        加入粉丝团消息
        :param user:
        """
        print("欢迎", user, "加入了粉丝团")

    def onMessage(self, msg: str):
        """
        系统消息
        :param msg:
        """
        print("消息 :", msg)

    def onLike(self, user: User):
        """
        点击喜欢的消息
        On Like
        :param user:
        """
        print("用户", user, "点了喜欢")

    def onLeave(self, json: any):
        """
        下播消息
        On Liver Leave
        :param json:
        """
        print("消息 :", "主播离开了")
        self.updRoomInfo()

    def onLottery(self, i: Lottery):
        """
        中奖的内容
        :param i:
        """
        print("中奖消息 :", i)

    def _checkUsernameIsMatched(self):
        """
        验证主播名字是自己想要的那个
        Check name matched
        :return: bool: 是否匹配
        """
        return True
        if self.name is None or self.roomLiver is None:
            return False
        return self.name == self.roomLiver.__str__() or self.roomLiver.__str__() in self.name or self.name in self.roomLiver.__str__()

    def _forceSearchUser(self):
        """
        搜索主播名
        :return:
        """
        _results = self.searchUser(self.name)
        if len(_results) > 0:
            self.isValidRoom = True
            self.roomLiver = _results[0]
        return self._updateUserOnly()

    def _updateUserOnly(self):
        """
        获取用户信息
        :return:
        """
        if self.roomLiver is None:
            return False
        _formatData = {"COMMON": COMMON_GET_PARAM, "TIMESTAMP": time.time() * 1000, "userId": self.roomLiver.ID}
        _url = USER_INFO_API.format_map(_formatData).format_map(_formatData)
        try:
            p = self.s.get(_url)
        except Exception as e:
            self.apiChangedError("更新用户信息接口请求失败", e.__str__())
            return False
        try:
            d = p.json()
        except Exception as e:
            self.apiChangedError("更新房间接口错误", e.__str__())
            return False
        self.isValidRoom = d["status"] == 0
        if "user_info" not in d and d["user_info"] is None:
            self.apiChangedError("Api发生改变，请及时联系我", d)
            return False
        self.roomLiver = User(d)
        if not self._checkUsernameIsMatched():
            self.isLive = False
            return False
        self.isLive = d["user_info"]["is_living"]
        self._rawRoomInfo = d["user_info"]['live_info']
        if self.isLive:
            self.roomID = d["user_info"]['live_info']['room_id']
            # 处理抽奖事件
            l = Lottery(self._rawRoomInfo)
            if l.isActive:
                # 因为现在每个房间只能同时开启一个抽奖，所以放一个就行了
                self.lottery = l
        return True

    def updRoomInfo(self, force=False):
        """
        更新房间信息
        :return:
        """
        if not force and self._updRoomAt > (datetime.now() - timedelta(minutes=3)):
            return self.isLive
        self._updRoomAt = datetime.now()
        if self.isValidRoom:
            return self._updateUserOnly()
        else:
            return self._forceSearchUser()

    @staticmethod
    def getUserInfoByUserId(userId):
        """
        通过UserId查找用户的房间号
        :param userId: 用户ID
        :return: XiGuaLiveApi
        """
        _formatData = {"COMMON": COMMON_GET_PARAM, "TIMESTAMP": time.time() * 1000, "userId": userId}
        _url = USER_INFO_API.format_map(_formatData).format_map(_formatData)
        try:
            p = requests.get(_url, headers=COMMON_HEADERS)
        except Exception as e:
            XiGuaLiveApi.apiChangedError("更新用户信息接口请求失败", e.__str__())
            return None
        try:
            d = p.json()
        except Exception as e:
            XiGuaLiveApi.apiChangedError("更新房间接口错误", e.__str__())
            return None
        return XiGuaLiveApi(User(d))

    @staticmethod
    def searchUser(keyword):
        """
        通过关键词搜索主播
        :param keyword: 关键词
        :return: array: 搜索结果
        """
        ret = []
        _formatData = {"COMMON": COMMON_GET_PARAM, "TIMESTAMP": time.time() * 1000, "keyword": keyword}
        _url = SEARCH_USER_API.format_map(_formatData).format_map(_formatData)
        try:
            p = requests.get(_url)
            d = p.json()
        except json.decoder.JSONDecodeError as e:
            XiGuaLiveApi.apiChangedError("搜索接口错误", e.__str__())
            return ret
        if "data" in d and d["data"] is not None:
            for i in d["data"]:
                if i["block_type"] != 0:
                    continue
                if "cells" not in i or len(i["cells"]) == 0:
                    break
                for _j in i["cells"]:
                    ret.append(User(_j))
        return ret

    def getDanmaku(self):
        """
        获取弹幕
        """
        if not self.isValidRoom:
            self.updRoomInfo()
            return
        p = self.s.get("https://i.snssdk.com/videolive/im/get_msg?cursor={cursor}&room_id={roomID}"
                       "&version_code=800&device_platform=android".format(
            roomID=self.roomID,
            cursor=self._cursor
        ))
        d = p.json()
        if "data" not in d or "extra" not in d or "cursor" not in d["extra"]:
            if "base_resp" in d and d["base_resp"]["status_code"] != 10038:
                print(d["base_resp"]["status_message"])
                self.apiChangedError("接口数据返回错误", d)
            return
        else:
            self._cursor = d["extra"]["cursor"]
            if DEBUG:
                print("Cursor:\t", self._cursor)
        for i in d['data']:
            if DEBUG:
                print(i)
            if "common" not in i and "method" not in i["common"]:
                continue
            if i["common"]['method'] == "VideoLivePresentEndTipMessage":
                self.onPresentEnd(Gift(i))
            # elif i["common"]['method'] == "VideoLiveRoomAdMessage":
            #     self.onAd(i)
            # elif i["common"]['method'] == "VideoLiveChatMessage":
            #     self.onChat(Chat(i, self.lottery))
            # elif i["common"]['method'] == "VideoLiveMemberMessage":
            #     self.onEnter(MemberMsg(i))
            #     self._updateRoomPopularity(i)
            # elif i["common"]['method'] == "VideoLiveSocialMessage":
            #     self.onSubscribe(User(i))
            # elif i["common"]['method'] == "VideoLiveJoinDiscipulusMessage":
            #     self.onJoin(User(i))
            # elif i["common"]['method'] == "VideoLiveControlMessage":
            #     print("消息：", "主播离开一小会")
            #     # 这个消息代表主播下播了，直接更新房间信息
            #     self.updRoomInfo(True)
            # elif i["common"]['method'] == "VideoLiveDiggMessage":
            #     self.onLike(User(i))
            else:
                pass
            if self.lottery is None or self.lottery.ID == 0:
                self.lottery = Lottery(i)
        # 更新抽奖信息
        if self.lottery is not None and self.lottery.ID != 0:
            self.lottery.update()
            if self.lottery.isFinished:
                self.onLottery(self.lottery)
                self.lottery = None
        # 2分钟自动更新下房间信息
        self.updRoomInfo(len(d['data']) == 0)


if __name__ == "__main__":
    name = "永恒de草薙"
    if len(sys.argv) > 2:
        if sys.argv[-1] == "d":
            DEBUG = True
        name = sys.argv[1]
    print("西瓜直播弹幕助手 by JerryYan")
    api = XiGuaLiveApi(name)
    if not api.isValidRoom:
        input("房间不存在")
        sys.exit()
    print("进入", api.roomLiver, "的直播间")
    print("=" * 30)
    while True:
        if api.isLive:
            try:
                api.getDanmaku()
                time.sleep(1)
            except requests.exceptions.BaseHTTPError:
                print("网络错误，请确认网络")
                time.sleep(5)
            except Exception as e:
                print(e)
            else:
                print("主播未开播，等待2分钟后重试")
                time.sleep(60)
                api.updRoomInfo()
