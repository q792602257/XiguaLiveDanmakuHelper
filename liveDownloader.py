import sys
import time
from datetime import datetime
import m3u8
import queue
import threading
from config import config
from api import XiGuaLiveApi
from bilibili import *

q = queue.Queue()
base_uri = ""
isUpload = False
uq = queue.Queue()


class downloader(XiGuaLiveApi):
    files = []
    playlist: str = None

    def updRoomInfo(self):
        super(downloader, self).updRoomInfo()
        self.updPlayList()

    def updPlayList(self):
        if api.isLive:
            if "stream_url" not in self._rawRoomInfo:
                if self.playlist is None:
                    self.apiChangedError("无法获取直播链接")
                    self.playlist = False
                else:
                    self.playlist = self._rawRoomInfo["stream_url"]["alternate_pull_url"]
                    self.playlist = self.playlist.replace("_uhd","").replace("_sd","").replace("_ld","")

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
                    print("{} : Add Sequence {}".format(datetime.strftime(datetime.now(), "%y%m%d %H%M"),
                                                        len(self.files)))
                    q.put(i)
        self.genNewName()

    def genNewName(self):
        if len(self.files) > 800:
            q.put(True)
            self.files.clear()


def download(path=datetime.strftime(datetime.now(), "%Y%m%d_%H%M.ts")):
    global isUpload
    print("{} : Download Daemon Starting".format(datetime.strftime(datetime.now(), "%y%m%d %H%M")))
    n = False
    isUpload = False
    i = q.get()
    while True:
        if isinstance(i, bool):
            print("{} : Download Daemon Receive Command {}".format(datetime.strftime(datetime.now(), "%y%m%d %H%M"), i))
            break
        print("{} : Download {}".format(datetime.strftime(datetime.now(), "%y%m%d %H%M"), i))
        try:
            _p = requests.get("{}{}".format(base_uri, i))
        except:
            continue
        f = open(path, "ab")
        f.write(_p.content)
        f.close()
        n = True
        i = q.get()
    if n:
        isUpload = True
        uq.put(path)
    print("{} : Download Daemon Quiting".format(datetime.strftime(datetime.now(), "%y%m%d %H%M")))


def upload(date=datetime.strftime(datetime.now(), "%Y_%m_%d")):
    print("{} : Upload Daemon Starting".format(datetime.strftime(datetime.now(), "%y%m%d %H%M")))
    i = uq.get()
    while True:
        if isinstance(i, bool):
            print("{} : Upload Daemon Receive Command {}"
                  .format(datetime.strftime(datetime.now(), "%y%m%d %H%M"), i))
            if i is True:
                print("自动投稿中，请稍后")
                b.finishUpload(config["t_t"].format(date), 17, config["tag"], config["des"],
                               source=config["src"], no_reprint=0)
            break
        print("{} : Upload {}".format(datetime.strftime(datetime.now(), "%y%m%d %H%M"), i))
        try:
            b.preUpload(VideoPart(i, i))
        except:
            continue
        i = uq.get()
    print("{} : Upload Daemon Quiting".format(datetime.strftime(datetime.now(), "%y%m%d %H%M")))


b = Bilibili()
b.login(config["b_u"], config["b_p"])

if __name__ == "__main__":
    name = "永恒de草薙"
    # room = 75366565294
    # room = 83940182312 #Dae
    # room = 5947850784 #⑦
    # room = 58649240617 #戏
    if len(sys.argv) > 1:
        name = sys.argv[1]
    print("西瓜直播录播助手 by JerryYan")
    api = downloader(name)
    print("进入", api.roomLiver, "的直播间")
    if not api.isValidRoom:
        input("房间不存在")
        sys.exit()
    print("=" * 30)
    d = datetime.strftime(datetime.now(), "%Y_%m_%d")
    _preT = datetime.strftime(datetime.now(), "%Y%m%d_%H%M.ts")
    t = threading.Thread(target=download, args=(_preT,))
    ut = threading.Thread(target=upload, args=(d,))
    while True:
        if api.isLive:
            if d is None:
                d = datetime.strftime(datetime.now(), "%Y_%m_%d")
            if not t.is_alive():
                _preT = datetime.strftime(datetime.now(), "%Y%m%d_%H%M.ts")
                t = threading.Thread(target=download, args=(_preT,))
                t.setDaemon(True)
                t.start()
            if not ut.is_alive():
                ut = threading.Thread(target=upload, args=(d,))
                ut.setDaemon(True)
                ut.start()
            try:
                api.preDownload()
            except:
                pass
            time.sleep(3)
        else:
            if d is not None:
                q.put(False)
                d = None
            if isUpload:
                uq.put(True)
                isUpload = False
            else:
                del config
                from config import config
                # print("主播未开播，等待1分钟后重试")
            time.sleep(60)
            api.updRoomInfo()
