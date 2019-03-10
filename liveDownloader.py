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
eq = queue.Queue()

class downloader(XiGuaLiveApi):
    files = []
    playlist: str = None

    def updRoomInfo(self):
        super(downloader, self).updRoomInfo()
        if self.isLive:
            self.updPlayList()
        else:
            print("未开播，等待开播")
            self.files = []

    def updPlayList(self):
        if self.isLive:
            if "stream_url" in self._rawRoomInfo:
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
        else:
            print("PlayList {}".format(self.playlist))
        self.genNewName()


    def genNewName(self):
        if len(self.files) > 800:
            q.put(True)
            self.files.clear()
            self.updRoomInfo()


def download(path=datetime.strftime(datetime.now(), "%Y%m%d_%H%M.ts")):
    global isUpload
    print("{} : Download Daemon Starting".format(datetime.strftime(datetime.now(), "%y%m%d %H%M")))
    n = False
    isUpload = False
    i = q.get()
    f = open(path, "ab")
    while True:
        if isinstance(i, bool):
            print("{} : Download Daemon Receive Command {}".format(datetime.strftime(datetime.now(), "%y%m%d %H%M"), i))
            break
        print("{} : Download {}".format(datetime.strftime(datetime.now(), "%y%m%d %H%M"), i))
        try:
            _p = requests.get("{}{}".format(base_uri, i))
        except:
            continue
        f.write(_p.content)
        n = True
        i = q.get()
    f.close()
    if n:
        isUpload = True
        eq.put(path)
    print("{} : Download Daemon Quiting".format(datetime.strftime(datetime.now(), "%y%m%d %H%M")))


def encode():
    i = eq.get()
    while True:
        os.system("ffmpeg -i {} -c:a copy -c:v copy -f mp4 {}".format(i,i[:-3] + ".mp4"))
        if config["mv"]:
            shutil.move(i, config["mtd"])
        elif config["del"]:
            os.remove(i)
        uq.put(i[:-3] + ".mp4")
        i = eq.get()


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
                b.clear()
            break
        print("{} : Upload {}".format(datetime.strftime(datetime.now(), "%y%m%d %H%M"), i))
        try:
            b.preUpload(VideoPart(i, os.path.basename(i)))
        except:
            continue
        os.remove(i)
        i = uq.get()

    print("{} : Upload Daemon Quiting".format(datetime.strftime(datetime.now(), "%y%m%d %H%M")))


b = Bilibili()
b.login(config["b_u"], config["b_p"])

if __name__ == "__main__":
    name = config["l_u"]
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
            api.preDownload()
            time.sleep(4)
        else:
            if d is not None:
                q.put(False)
                d = None
            if isUpload:
                uq.put(True)
                isUpload = False
                del config
                from config import config
                # print("主播未开播，等待1分钟后重试")
            time.sleep(60)
            api.updRoomInfo()
