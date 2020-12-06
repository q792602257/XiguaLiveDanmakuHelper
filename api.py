# coding=utf-8

from Struct.User import User
import requests
import time
from datetime import datetime, timedelta

DEBUG = False
# 自己抓的自己设备的参数，建议开发者自己抓一个长期使用
# 如果有大佬破解初次激活设备时的数据也行，可以自己生成一堆用
CUSTOM_INFO = {
    'iid': "96159232732",
    'device_id': "55714661189",
    'cdid': "ed4295e8-5d9a-4cb9-b2a2-04009a3baa2d",
    'openudid': "70d6668d41512c39",
    'aid': "32",
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
    # 一个定值，几个版本换设备都没变过
    'oaid': "a625f466e0975d42",
}
COMMON_GET_PARAM = (
    "&iid={iid}&device_id={device_id}&channel={channel}&aid={aid}&app_name={app_name}&version_code={version_code}&"
    "version_name={version_name}&device_platform=android&ab_version={ab_version}&device_type={device_type}&"
    "device_brand={device_brand}&language=zh&os_api={os_api}&os_version={os_version}&openudid={openudid}&fp=a_fake_fp&"
    "manifest_version_code={manifest_version_code}&update_version_code={version_code_full}&_rticket={{TIMESTAMP:.0f}}&"
    "_rticket={{TIMESTAMP:.0f}}&cdid_ts={{TIMESTAMP:.0f}}&tma_jssdk_version={tma_jssdk_version}&"
    "rom_version={rom_version}&oaid={oaid}&cdid={cdid}").format_map({**CUSTOM_INFO, **VERSION_INFO})
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
COMMON_HEADERS = {
    "sdk-version": '2',
    "passport-sdk-version": "19",
    "X-SS-DP": "32",
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10) VideoArticle/9.2.6 cronet/TTNetVersion:828f6f3c 2020-09-06 "
                  "QuicVersion:7aee791b 2020-06-05",
    # 最好别加br，requests库好像自带没法解析
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
        self.s = requests.session()
        self.s.headers.update(COMMON_HEADERS)
        self._updRoomAt = datetime.fromtimestamp(0)
        self.updRoomInfo()
        self._ext = ""
        self._cursor = "0"

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
            self.roomID = self._rawRoomInfo['room_id']
            return self._getRoomInfo(True)
        return self.isLive

    def _getRoomInfo(self, force=False):
        if self.roomID == 0 or not self.roomID:
            self.isLive = False
            return False
        if (self._updRoomAt + timedelta(minutes=3) > datetime.now()) and not force:
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
