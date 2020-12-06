# coding=utf-8
import sys

from Struct.MemberMsg import MemberMsg
from Struct.User import User
from Struct.Gift import Gift
from Struct.Chat import Chat
import requests
import time
from datetime import datetime, timedelta
from Xigua_pb2 import XiguaLive
from XiguaMessage_pb2 import FansClubMessage, SocialMessage

DEBUG = False
# 自己抓的自己设备的参数，建议开发者自己抓一个长期使用
# 如果有大佬破解初次激活设备时的数据也行，可以自己生成一堆用
CUSTOM_INFO = {
    'iid': "96159232732",
    'device_id': "55714661189",
    'cdid': "ed4295e8-5d9a-4cb9-b2a2-04009a3baa2d",
    'openudid': "70d6668d41512c39",
    # 'aid': "32", # 又是一个不变的值
    'channel': "xiaomi",
    'device_brand': "Xiaomi",
    'device_type': "MI+8+SE",
    'os_api': "28",
    'os_version': "9",
    'rom_version': "miui_V12_V12.0.2.0.QEBCNXM",
}
VERSION_INFO = {
    'app_name': "video_article",
    'version_code': "926",
    'version_code_full': "92609",
    'version_name': "9.2.6",
    'ab_version': "941090,785218,668858,1046292,1073579,830454,956074,929436,797199,1135476,1179370,994679,959010,"
                  "900042,1113833,668854,1193963,901277,1043330,1038721,994822,1002058,1230687,1189797,1143356,1143441,"
                  "1143501,1143698,1143713,1371009,1243997,1392586,1395695,1395486,1398858,668852,668856,668853,"
                  "1186421,668851,668859,999124,668855,1039075",
    'manifest_version_code': "518",
    'tma_jssdk_version': "1830001",
    # 'oaid': "a625f466e0975d42", # 一个定值，几个版本换设备都没变过
}
COMMON_GET_PARAM = (
    "&iid={iid}&device_id={device_id}&channel={channel}&aid=32&app_name={app_name}&version_code={version_code}&"
    "version_name={version_name}&device_platform=android&ab_version={ab_version}&device_type={device_type}&"
    "device_brand={device_brand}&language=zh&os_api={os_api}&os_version={os_version}&openudid={openudid}&fp=a_fake_fp&"
    "manifest_version_code={manifest_version_code}&update_version_code={version_code_full}&_rticket={{TIMESTAMP:.0f}}&"
    "_rticket={{TIMESTAMP:.0f}}&cdid_ts={{TIMESTAMP:.0f}}&tma_jssdk_version={tma_jssdk_version}&"
    "rom_version={rom_version}&cdid={cdid}&oaid=a625f466e0975d42").format_map({**VERSION_INFO, **CUSTOM_INFO})
SEARCH_USER_API = (
    "https://search-hl.ixigua.com/video/app/search/search_content/?format=json"
    "&fss=search_subtab_switch&target_channel=video_search&keyword_type=search_subtab_switch&offset=0&count=10"
    "&search_sug=1&forum=1&is_native_req=0&m_tab=video&pd=user&tab=user&_s_tma=SEARCH_STANDARD.list.fe_get_data"
    '&_s_page_sub_route=/&_s_ec={{"filterDataType":[],"reserveFilterBar":true}}&__use_xigua_native_bridge_fetch__=1'
    '&ab_param={{"is_show_filter_feature": 1, "is_hit_new_ui": 1}}'
    "&search_start_time={TIMESTAMP:.0f}&from=live&en_qc=1&pd=xigua_live&ssmix=a{COMMON}&keyword={keyword}")
USER_INFO_API = "https://api100-quic-c-hl.ixigua.com/video/app/user/home/v7/?to_user_id={userId}{COMMON}"
ROOM_INFO_API = ("https://webcast3-normal-c-hl.ixigua.com/webcast/room/enter/?room_id={roomId}&webcast_sdk_version=1350"
                 "&webcast_language=zh&webcast_locale=zh_CN&pack_level=4{COMMON}")
DANMAKU_GET_API = ("https://webcast3-normal-c-hl.ixigua.com/webcast/room/{roomId}/_fetch_message_polling/?"
                   "webcast_sdk_version=1350&webcast_language=zh&webcast_locale=zh_CN{COMMON}")
GIFT_DATA_API = ("https://webcast3-normal-c-hl.ixigua.com/webcast/gift/list/?room_id={roomId}&to_room_id={roomId}&"
                 "gift_scene=1&fetch_giftlist_from=2&current_network_quality_info={{}}"
                 "&webcast_sdk_version=1790&webcast_language=zh&webcast_locale=zh_CN{COMMON}")
COMMON_HEADERS = {
    "sdk-version": '2',
    "passport-sdk-version": "19",
    "X-SS-DP": "32",
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10) VideoArticle/9.2.6 cronet/TTNetVersion:828f6f3c 2020-09-06 "
                  "QuicVersion:7aee791b 2020-06-05",
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
        self.broadcaster = None
        self.isValidUser = False
        self.name = str(name)
        if type(name) == User:
            self.broadcaster = name
            self.name = name.name
        elif str(name).isdigit():
            self.broadcaster = User()
            self.isValidUser = True
            self.broadcaster.ID = int(name)
        else:
            self.name = str(name)
        self.isLive = False
        self._rawRoomInfo = {}
        self.roomID = 0
        self.roomPopularity = 0
        self.s = requests.session()
        self.s.headers.update(COMMON_HEADERS)
        self._updRoomAt = datetime.fromtimestamp(0)
        self.updRoomInfo()
        self._ext = ""
        self._cursor = "0"

    def _updateRoomPopularity(self, _data):
        """
        更新房间人气的方法
        Update Room Popularity
        :param _data: Received Message
        """
        if "extra" in _data:
            if "member_count" in _data["extra"] and _data["extra"]["member_count"] > 0:
                self.roomPopularity = _data["extra"]["member_count"]
        if "data" in _data:
            if "popularity" in _data["data"]:
                self.roomPopularity = _data["data"]["popularity"]

    def getJson(self, url, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = 10
        try:
            p = self.s.get(url, **kwargs)
        except Exception as e:
            print("网络请求失败")
            if DEBUG:
                print("GET")
                print("URL", url)
                print("ERR ", e.__str__())
            return None
        try:
            return p.json()
        except Exception as e:
            print("解析请求失败")
            if DEBUG:
                print("GET JSON")
                print("URL", url)
                print("CNT", p.text)
                print("ERR ", e.__str__())
            return None

    def postJson(self, url, data, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = 10
        try:
            p = self.s.post(url, data=data, **kwargs)
        except Exception as e:
            print("网络请求失败")
            if DEBUG:
                print("POST")
                print("URL", url)
                print("ERR ", e.__str__())
            return None
        try:
            return p.json()
        except Exception as e:
            print("解析请求失败")
            if DEBUG:
                print("GET JSON")
                print("URL", url)
                print("CNT", p.text)
                print("ERR ", e.__str__())
            return None

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

    def _checkUsernameIsMatched(self, compare=None):
        """
        验证主播名字是自己想要的那个
        Check name matched
        :return: bool: 是否匹配
        """
        if compare is None:
            compare = self.broadcaster
        if self.name is None or compare is None:
            return False
        return self.name == compare.__str__() or compare.__repr__() in self.name or self.name in compare.__repr__()

    def _forceSearchUser(self):
        """
        搜索主播名
        :return:
        """
        _formatData = {"TIMESTAMP": time.time() * 1000, "keyword": self.name}
        _COMMON = COMMON_GET_PARAM.format_map(_formatData)
        _formatData['COMMON'] = _COMMON
        _url = SEARCH_USER_API.format_map(_formatData)
        d = self.getJson(_url)
        if d is None:
            print("搜索接口请求失败")
            return False
        self.broadcaster = None
        self.isValidUser = False
        if "data" in d and d["data"] is not None:
            for i in d["data"]:
                if self.broadcaster is not None:
                    break
                if i["block_type"] != 2:
                    continue
                if "cells" not in i or len(i["cells"]) == 0:
                    break
                for _j in i["cells"]:
                    if "room" in _j:
                        _user = User(_j["room"])
                        self.roomID = _j["room"]["room_id"]
                        self.isLive = _j["room"]["is_living"]
                        if self._checkUsernameIsMatched(_user):
                            self.isValidUser = True
                            self.broadcaster = _user
                            break
        self._updRoomAt = datetime.now()
        return self._updateUserInfo()

    def _updateUserInfo(self):
        """
        获取用户信息
        :return:
        """
        if self.broadcaster is None:
            self.isValidUser = False
            return False
        _formatData = {"TIMESTAMP": time.time() * 1000, "userId": self.broadcaster.ID}
        _COMMON = COMMON_GET_PARAM.format_map(_formatData)
        _formatData['COMMON'] = _COMMON
        _url = USER_INFO_API.format_map(_formatData)
        d = self.getJson(_url)
        if d is None:
            print("获取用户信息失败")
            return False
        self.isValidUser = d["status"] == 0
        if "user_info" not in d and d["user_info"] is None:
            self.apiChangedError("Api发生改变，请及时联系我", d)
            return False
        self._updRoomAt = datetime.now()
        self.broadcaster = User(d)
        if not self._checkUsernameIsMatched():
            self.isLive = False
            return False
        self.isLive = d["user_info"]["is_living"]
        if d["user_info"]['live_info'] is None:
            if d["live_data"] is None:
                self.isLive = False
            else:
                self._rawRoomInfo = d["live_data"]['live_info']
        else:
            self._rawRoomInfo = d["user_info"]['live_info']
        if self.isLive:
            self.roomID = d["user_info"]['live_info']['room_id']
        return True

    def _getRoomInfo(self, force=False):
        if self.roomID == 0 or not self.roomID:
            self.isLive = False
            return False
        if not force and (self._updRoomAt + timedelta(minutes=10) > datetime.now()):
            return self.isLive
        _formatData = {"TIMESTAMP": time.time() * 1000, "roomId": self.roomID}
        _COMMON = COMMON_GET_PARAM.format_map(_formatData)
        _formatData['COMMON'] = _COMMON
        _url = ROOM_INFO_API.format_map(_formatData)
        d = self.getJson(_url)
        if d is None:
            print("获取房间信息接口请求失败")
            return False
        if d["status_code"] != 0:
            print("接口提示：【{}】".format(d["data"]["message"]))
            return False
        self._rawRoomInfo = d["data"]
        self.isLive = d["data"]["status"] == 2
        self._updRoomAt = datetime.now()
        self._updateRoomPopularity(d)
        return self.isLive

    def updRoomInfo(self, force=False):
        """
        更新房间信息
        :return:
        """
        if not force and (self._updRoomAt + timedelta(minutes=2) > datetime.now()):
            return self.isLive
        if not self.isValidUser:
            return self._forceSearchUser()
        elif not self.isLive:
            return self._updateUserInfo()
        else:
            return self._getRoomInfo(force)

    def updGiftInfo(self):
        self.updRoomInfo()
        _formatData = {"TIMESTAMP": time.time() * 1000, "roomId": self.roomID}
        _COMMON = COMMON_GET_PARAM.format_map(_formatData)
        _formatData['COMMON'] = _COMMON
        _url = GIFT_DATA_API.format_map(_formatData)
        d = self.getJson(_url)
        if d is None or d["status_code"] != 0:
            return "异常"
        elif 'pages' in d["data"]:
            for _page in d["data"]['pages']:
                if 'gifts' in _page:
                    for _gift in _page['gifts']:
                        Gift.addGift(_gift)
        return len(Gift.giftList)

    def getDanmaku(self):
        """
        获取弹幕
        """
        self.updRoomInfo()
        _formatData = {"TIMESTAMP": time.time() * 1000, "roomId": self.roomID}
        _COMMON = COMMON_GET_PARAM.format_map(_formatData)
        _formatData['COMMON'] = _COMMON
        _url = DANMAKU_GET_API.format_map(_formatData)
        p = self.s.post(_url, data="cursor={cursor}&resp_content_type=protobuf&live_id=3&user_id=0&identity=audience"
                                   "last_rtt=85"
                                   "&internal_ext={ext}".format_map({"cursor": self._cursor, "ext": self._ext}),
                        headers={"Content-Type": "application/x-www-form-urlencoded"})
        if p.status_code != 200:
            return
        data = XiguaLive()
        data.ParseFromString(p.content)
        self._cursor = data.cursor
        self._ext = data.internal_ext
        for _each in data.data:
            if _each.method == "WebcastGiftMessage":
                _gift = Gift(_each.raw)
                if _gift.isAnimate() or _gift.isFinished:
                    self.onPresentEnd(_gift)
                else:
                    self.onPresent(_gift)
            elif _each.method == "WebcastChatMessage":
                _chat = Chat(_each.raw)
                self.onChat(_chat)
            elif _each.method == "WebcastControlMessage":
                # 下播的时候会有个这个
                self.onLeave(None)
            elif _each.method == "WebcastSocialMessage":
                _socialMessage = SocialMessage()
                _socialMessage.ParseFromString(_each.raw)
                _user = User(_socialMessage.user)
                self.onSubscribe(_user)
            elif _each.method == "WebcastFansclubMessage":
                _fansClubMessage = FansClubMessage()
                _fansClubMessage.ParseFromString(_each.raw)
                # 升级是1，加入是2
                if _fansClubMessage.type == 2:
                    _user = User(_fansClubMessage.user)
                    self.onJoin(_user)
                else:
                    self.onMessage(_fansClubMessage.content)
            else:
                pass

    @property
    def updateAt(self):
        return self._updRoomAt


if __name__ == "__main__":
    name = "永恒de草薙"
    if len(sys.argv) > 2:
        if sys.argv[-1] == "d":
            DEBUG = True
        name = sys.argv[1]
    print("西瓜直播弹幕助手 by JerryYan")
    print("接口版本9.2.6")
    print("搜索【", name, "】", end="\t", flush=True)
    api = XiGuaLiveApi(name)
    if not api.isValidUser:
        input("用户不存在")
        sys.exit()
    print("OK")
    print(api.broadcaster.__repr__())
    print("更新房间信息，请稍后", end="\t", flush=True)
    if api.updRoomInfo(True):
        print("OK")
    else:
        print("FAIL")
    print("更新房间礼物信息", end="\t", flush=True)
    __res = api.updGiftInfo()
    if __res < 0:
        print("FAIL")
    else:
        print('OK\n礼物种数：', __res)
    print("=" * 30)
    while True:
        if api.isLive:
            try:
                api.getDanmaku()
                time.sleep(1)
            except requests.exceptions.BaseHTTPError:
                print("网络错误，请确认网络")
                time.sleep(5)
            # except Exception as e:
            #     print(e)
        else:
            print("主播未开播，等待1分钟后重试")
            time.sleep(60)
            api.updRoomInfo(True)
