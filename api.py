# coding=utf-8

from Struct.User import User
import requests
import time
from datetime import datetime, timedelta

DEBUG = False
COMMON_GET_PARAM = (
    "&iid=96159232732&device_id=55714661189&channel=xiaomi&aid=32&app_name=video_article&version_code=844"
    "&version_name=8.4.4&device_platform=android&ab_version=668855,1640207,1652557,1143698,1043330,1143713,"
    "1477978,1189797,1635895,1631832,994822,900042,956074,1143356,1046292,1481027,929436,994679,1419059,"
    "1073579,668854,1143441,668852,668853,941090,668858,668851,668859,668856,"
    "1639440,1630487&device_type=MI+8+SE&device_brand=Xiaomi&language=zh"
    "&os_api=28&os_version=9&openudid=70d6668d41512c39&manifest_version_code=444&update_version_code=84407"
    "&_rticket={TIMESTAMP:.0f}&cdid_ts={TIMESTAMP:.0f}&fp=a_fake_fp&tma_jssdk_version=1.53.0.5"
    "&cdid=ed4295e8-5d9a-4cb9-b2a2-04009a3baa2d&oaid=a625f466e0975d42")
SEARCH_USER_API = (
    "https://search-hl.ixigua.com/video/app/search/search_content/?format=json"
    "&fss=&keyword_type=input&offset=0&count=10&search_sug=0&forum=0&is_native_req=0"
    "&search_start_time={TIMESTAMP:.0f}&from=live&en_qc=1&pd=xigua_live&ssmix=a{COMMON}&keyword={keyword}")
USER_INFO_API = "https://api3-normal-c-hl.ixigua.com/video/app/user/home/v7/?to_user_id={userId}{COMMON}"
ROOM_INFO_API = "https://webcast3.ixigua.com/webcast/room/enter/?room_id={roomId}&pack_level=4{COMMON}"
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
        self.broadcaster = None
        self.isValidUser = False
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
        self._cursor = "0"
        self.lottery = None
        self.s = requests.session()
        self.s.headers.update(COMMON_HEADERS)
        self._updRoomAt = datetime.fromtimestamp(0)
        self.updRoomInfo()

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
            p = self.s.post(url, data, **kwargs)
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

    def _checkUsernameIsMatched(self, compare=None):
        """
        验证主播名字是自己想要的那个
        Check name matched
        :return: bool: 是否匹配
        """
        return True
        if compare is None:
            compare = self.broadcaster
        if self.name is None or compare is None:
            return False
        return self.name == compare.__str__() or compare.__str__() in self.name or self.name in compare.__str__()

    def _forceSearchUser(self):
        """
        搜索主播名
        :return:
        """
        _formatData = {"COMMON": COMMON_GET_PARAM, "TIMESTAMP": time.time() * 1000, "keyword": self.name}
        _url = SEARCH_USER_API.format_map(_formatData).format_map(_formatData)
        d = self.getJson(_url)
        if d is None:
            print("搜索接口请求失败")
            return False
        self.broadcaster = None
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
        self.isValidUser = False
        if self.broadcaster is None:
            return False
        _formatData = {"COMMON": COMMON_GET_PARAM, "TIMESTAMP": time.time() * 1000, "userId": self.broadcaster.ID}
        _url = USER_INFO_API.format_map(_formatData).format_map(_formatData)
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
            self.roomID = self._rawRoomInfo['room_id']
        return self.isLive

    def _getRoomInfo(self, force=False):
        if self.roomID == 0 or not self.roomID:
            self.isLive = False
            return False
        if (self._updRoomAt + timedelta(minutes=3) > datetime.now()) and not force:
            return self.isLive
        _formatData = {"COMMON": COMMON_GET_PARAM, "TIMESTAMP": time.time() * 1000, "roomId": self.roomID}
        _url = ROOM_INFO_API.format_map(_formatData).format_map(_formatData)
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

    @property
    def updateAt(self):
        return self._updRoomAt
