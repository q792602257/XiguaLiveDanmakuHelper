# coding=utf-8
import json
import sys
import random

from Struct.User import User
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
                if i["block_type"] != 0:
                    continue
                if "cells" not in i or len(i["cells"]) == 0:
                    break
                for _j in i["cells"]:
                    _user = User(_j)
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
        self._rawRoomInfo = d["user_info"]['live_info']
        if self.isLive:
            self.roomID = d["user_info"]['live_info']['room_id']
        return self.isLive

    def _getRoomInfo(self, force=False):
        if self.roomID == 0:
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
