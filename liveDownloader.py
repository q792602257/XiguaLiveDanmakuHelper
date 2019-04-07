import shutil
import sys
import time
from datetime import datetime
import threading
from bilibili import *
from Common import *
import os
import requests

isEncode = False
isDownload = False


def download(url):
    global isDownload, forceStopDownload
    path = datetime.strftime(datetime.now(), "%Y%m%d_%H%M.flv")
    p = requests.get(url, stream=True)
    if p.status_code != 200:
        appendDownloadStatus("Download [{}] Response 404 ,will stop looping".format(url))
        return True
    isDownload = True
    appendDownloadStatus("Starting Download >{}<".format(path))
    f = open(path, "wb")
    try:
        for t in p.iter_content(chunk_size=64 * 1024):
            if t:
                f.write(t)
            _size = os.path.getsize(path)
            modifyLastDownloadStatus("Download >{}< @ {:.2f}%".format(path, 100.0 * _size/config["p_s"]))
            if _size > config["p_s"] or forceStopDownload:
                break
        modifyLastDownloadStatus("Finished Download >{}<".format(path))
    except Exception as e:
        appendError("Download >{}< With Exception {}".format(path, datetime.strftime(datetime.now(), "%y%m%d %H%M"),
                                                               e.__str__()))
    f.close()
    isDownload = False
    if os.path.getsize(path) == 0:
        os.remove(path)
        return False
    encodeQueue.put(path)
    if forceStopDownload:
        download(url)
        forceStopDownload = False


def encode():
    global isEncode
    while True:
        i = encodeQueue.get()
        if os.path.exists(i):
            isEncode = True
            appendEncodeStatus("Start Encoding >{}<".format(i))
            os.system("ffmpeg -i {} -c:v copy -c:a copy -f mp4 {} -y".format(i, i[:13] + ".mp4"))
            uploadQueue.put(i[:13] + ".mp4")
            modifyLastEncodeStatus("Finished Encoding >{}<".format(i))
            if config["mv"]:
                shutil.move(i, config["mtd"])
            elif config["del"]:
                os.remove(i)
        isEncode = False


def upload(date=datetime.strftime(datetime.now(), "%Y_%m_%d")):
    i = uploadQueue.get()
    while True:
        if isinstance(i, bool):
            if i is True:
                b.finishUpload(config["t_t"].format(date), 17, config["tag"], config["des"],
                               source=config["src"], no_reprint=0)
                b.clear()
            break
        if not os.path.exists(i):
            appendError("Upload File Not Exist {}".format(i))
            i = uploadQueue.get()
            continue
        try:
            b.preUpload(VideoPart(i, os.path.basename(i)))
        except Exception as e:
            appendError(e.__str__())
        os.remove(i)
        i = uploadQueue.get()

    appendUploadStatus("Upload Daemon Quiting")


b = Bilibili()
b.login(config["b_u"], config["b_p"])


def run(name):
    global isEncode, isDownload
    api = downloader(name)
    et = threading.Thread(target=encode, args=())
    et.setDaemon(True)
    et.start()
    if not api.isValidRoom:
        appendError("[{}]房间不存在".format(name))
        return
    d = None
    t = threading.Thread(target=download)
    ut = threading.Thread(target=upload, args=(d,))
    _count = 0
    _count_error = 0
    while True:
        if api.isLive:
            if d is None:
                d = datetime.strftime(datetime.now(), "%Y_%m_%d")
            if not t.is_alive():
                _count_error += 1
                _preT = api.playlist
                t = threading.Thread(target=download, args=(_preT,))
                t.setDaemon(True)
                t.start()
            if not ut.is_alive():
                ut = threading.Thread(target=upload, args=(d,))
                ut.setDaemon(True)
                ut.start()
            if not et.is_alive():
                et = threading.Thread(target=encode, args=())
                et.setDaemon(True)
                et.start()
            if _count % 15 == 0:
                try:
                    api.updRoomInfo()
                    _count = 0
                    _count_error = 0
                except Exception as e:
                    appendError(e.__str__())
                    time.sleep(20)
                    _count_error += 1
                    continue
            if _count_error > 15:
                api.isLive = False
            _count += 1
            time.sleep(20)
        else:
            if d is not None:
                d = None
            if not isEncode and not isDownload:
                uploadQueue.put(True)
                isEncode = True
                isDownload = True
                # print("主播未开播，等待1分钟后重试")
            time.sleep(60)
            try:
                api.updRoomInfo()
                _count_error = 0
            except Exception as e:
                appendError(e.__str__())
