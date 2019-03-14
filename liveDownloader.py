import sys
import time
from datetime import datetime
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
                    self.playlist = self._rawRoomInfo["stream_url"]["flv_pull_url"]
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


def download(url):
    global isUpload
    isUpload = False
    path = datetime.strftime(datetime.now(), "%Y%m%d_%H%M.flv")
    p = requests.get(url, stream=True)
    if p.status_code != 200:
        isUpload = True
        print("{} : Download Response 404 ,will stop looping".format(datetime.strftime(datetime.now(), "%y%m%d %H%M")))
        return True
    print("{} : Download {}".format(datetime.strftime(datetime.now(), "%y%m%d %H%M"), path))
    f = open(path, "ab")
    try:
        for t in p.iter_content(chunk_size=64*1024):
            if t:
                f.write(t)
            if os.path.getsize(path) > 1024*1024*1024*1.5:
                break
        print("{} : Download Quiting".format(datetime.strftime(datetime.now(), "%y%m%d %H%M")))
    except Exception as e:
        print("{} : Download Quiting With Exception {}".format(datetime.strftime(datetime.now(), "%y%m%d %H%M"),e.__str__()))
    f.close()
    isUpload = True
    uq.put(path)
    download(url)


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
        if not os.path.exists(i):
            print("{} : Upload File Not Exist {}".format(datetime.strftime(datetime.now(), "%y%m%d %H%M"), i))
            i = uq.get()
            continue
        try:
            b.preUpload(VideoPart(i, os.path.basename(i)))
        except:
            continue
        if config["mv"]:
            shutil.move(i, config["mtd"])
        elif config["del"]:
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
    t = threading.Thread(target=download)
    ut = threading.Thread(target=upload, args=(d,))

    while True:
        if api.isLive:
            if d is None:
                d = datetime.strftime(datetime.now(), "%Y_%m_%d")
            if not t.is_alive():
                _preT = api.playlist
                t = threading.Thread(target=download, args=(_preT,))
                t.setDaemon(True)
                t.start()
            if not ut.is_alive():
                ut = threading.Thread(target=upload, args=(d,))
                ut.setDaemon(True)
                ut.start()
            try:
                api.updRoomInfo()
            except:
                time.sleep(30)
                continue
            time.sleep(120)
        else:
            if d is not None:
                d = None
            if isUpload:
                uq.put(True)
                isUpload = False
                del config
                from config import config
                # print("主播未开播，等待1分钟后重试")
            time.sleep(60)
            api.updRoomInfo()
