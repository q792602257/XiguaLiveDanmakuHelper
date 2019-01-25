import sys
import time
from datetime import datetime
import dotenv
import m3u8
import queue
import threading

from api import XiGuaLiveApi
from bilibili import *

q = queue.Queue()
base_uri = ""
isUpload = False
OutFileName = []
env = dotenv.main.DotEnv(".env")


class downloader(XiGuaLiveApi):
    files = []
    playlist: str = None

    def updRoomInfo(self):
        super(downloader, self).updRoomInfo()
        self.updPlayList()

    def updPlayList(self):
        if "playInfo" not in self._rawRoomInfo or "Main" not in self._rawRoomInfo["playInfo"]:
            if self.playlist is None:
                self.apiChangedError("无法获取直播链接")
                self.playlist = False
        else:
            self.playlist = self._rawRoomInfo["playInfo"]["Main"]["1"]["Url"]["HlsUrl"]


    def onLike(self, user):
        pass
    def onAd(self, i):
        pass
    def onChat(self, chat):
        pass
    def onEnter(self, msg):
        pass
    def onJoin(self, user):
        pass
    def onLeave(self, json):
        self.updRoomInfo()
    def onMessage(self, msg):
        pass
    def onPresent(self, gift):
        pass
    def onPresentEnd(self, gift):
        pass
    def onSubscribe(self, user):
        pass
    def preDownload(self):
        global base_uri
        if self.playlist:
            try:
                p = m3u8.load(self.playlist)
            except:
                self.updRoomInfo()
                return
            base_uri = p.base_uri
            for i in p.files:
                if i not in self.files:
                    self.files.append(i)
                    q.put(i)
        self.genNewName()
    def genNewName(self):
        if len(self.files) > 1500:
            q.put(False)
            self.files.clear()
            return True
        else:
            return False

def download(path=datetime.strftime(datetime.now(),"%Y%m%d_%H%M.ts")):
    print("Download Daemon Starting")
    OutFileName.append(path)
    while True:
        i = q.get()
        if isinstance(i, bool):
            print("Recive Command {}".format(i))
            break
        _p = requests.get("{}{}".format(base_uri,i))
        print("Download : {}".format(i))
        f = open(path, "ab")
        f.write(_p.content)
        f.close()


if __name__ == "__main__":
    room = 97621754276  # 永恒
    # room = 75366565294
    # room = 83940182312 #Dae
    # room = 5947850784 #⑦
    # room = 58649240617 #戏
    if len(sys.argv) > 1:
        try:
            room = int(sys.argv[1])
        except ValueError:
            pass
    print("西瓜直播录播助手 by JerryYan")
    api = downloader(room)
    print("进入", api.roomLiver, "的直播间")
    if not api.isValidRoom:
        input("房间不存在")
        sys.exit()
    print("=" * 30)
    _preT = datetime.strftime(datetime.now(), "%Y%m%d_%H.ts")
    t = threading.Thread(target=download, args=(_preT,))
    t.setDaemon(True)
    t.start()
    while True:
        if api.isLive:
            if not t.is_alive():
                _preT = datetime.strftime(datetime.now(), "%Y%m%d_%H.ts")
                t = threading.Thread(target=download, args=(_preT,))
                t.setDaemon(True)
                t.start()
            api.preDownload()
            isUpload = True
            time.sleep(3)
        else:
            q.put(False)
            if isUpload:
                print("自动投稿中，请稍后")
                b = Bilibili()
                b.login(env.get("b_u"), env.get("b_p"))
                u = threading.Thread(target=b.upload,args=([VideoPart(n) for n in OutFileName],
                                     "【永恒de草薙直播的录播】（三国战记） live at {} 自动投递实际测试".format(OutFileName[0]),
                                     17, ["永恒de草薙", "三国", "三国战记", "自动投递", "直播", "录播"],
                                     "自动投递实际测试\n原主播：永恒de草薙\n直播时间：晚上6点多到白天6点左右",),
                                     kwargs={"source": "https://live.ixigua.com/userlive/97621754276", "no_reprint": 0})
                u.setDaemon(True)
                u.start()
                u.join()
                # reset all for long time running
                OutFileName = []
                api.files = []
                isUpload = False
            else:
                pass
                # print("主播未开播，等待1分钟后重试")
            time.sleep(60)
            api.updRoomInfo()
