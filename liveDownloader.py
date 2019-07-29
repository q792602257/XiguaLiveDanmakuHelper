import shutil
import sys
import time
from datetime import datetime
import threading
from bilibili import *
import Common
import os
import requests

isEncode = False
isDownload = False


def download():
    global isDownload
    while Common.api.isLive and not Common.forceNotDownload:
        session = requests.session()
        if not Common.streamUrl:
            Common.appendError("Download with No StreamUrl Specific")
            break
        path = datetime.strftime(datetime.now(), "%Y%m%d_%H%M.flv")
        p = session.get(Common.streamUrl, stream=True, timeout=10)
        if p.status_code != 200:
            Common.appendDownloadStatus("Download with Response {}".format(p.status_code))
            break
        isDownload = True
        Common.appendDownloadStatus("Download >{}< Start".format(path))
        f = open(path, "wb")
        _size = 0
        try:
            for t in p.iter_content(chunk_size=64 * 1024):
                if Common.forceNotDownload:
                    Common.modifyLastDownloadStatus("Force Stop Download".format(path))
                    return
                f.write(t)
                _size += len(t)
                Common.modifyLastDownloadStatus(
                    "Downloading >{}< @ {:.2f}%".format(path, 100.0 * _size / Common.config["p_s"]))
                if _size > Common.config["p_s"]:
                    Common.modifyLastDownloadStatus("Download >{}< Exceed MaxSize".format(path))
                    break
            Common.modifyLastDownloadStatus("Download >{}< Finished".format(path))
        except Exception as e:
            Common.appendError("Download >{}< With Exception {}".format(path, e.__str__()))
        f.close()
        isDownload = False
        if os.path.getsize(path) < 1024 * 1024:
            Common.modifyLastDownloadStatus("Downloaded File >{}< is too small, will ignore it".format(path))
            os.remove(path)
            return False
        Common.encodeQueue.put(path)
        Common.api.updRoomInfo()


def encode():
    global isEncode
    Common.appendEncodeStatus("Encode Daemon Starting")
    while True:
        isEncode = False
        i = Common.encodeQueue.get()
        if Common.forceNotEncode:
            Common.appendEncodeStatus("设置了不编码，所以[{}]不会编码".format(i))
        elif os.path.exists(i):
            isEncode = True
            if os.path.getsize(i) < 8 * 1024 * 1024:
                Common.appendEncodeStatus("Encoded File >{}< is too small, will ignore it".format(i))
                continue
            else:
                Common.appendEncodeStatus("Encoding >{}< Start".format(i))
                _code = os.system("ffmpeg -i {} -c:v copy -c:a copy -f mp4 {} -y".format(i, i[:13] + ".mp4"))
                if _code != 0:
                    Common.appendError("Encode {} with Non-Zero Return.".format(i))
                    continue
                else:
                    Common.modifyLastEncodeStatus("Encode >{}< Finished".format(i))
                    i = i[:13] + ".mp4"
        Common.uploadQueue.put(i)


def upload():
    date=datetime.strftime(datetime.now(), "%Y_%m_%d")
    Common.appendUploadStatus("Upload Daemon Starting")
    i = Common.uploadQueue.get()
    while True:
        Common.doClean()
        if Common.forceNotUpload:
            if isinstance(i, bool):
                Common.appendUploadStatus("设置了不上传，不会发布了")
                break
            else:
                Common.appendUploadStatus("设置了不上传，所以[{}]不会上传了".format(i))
        else:
            if isinstance(i, bool):
                if i is True:
                    b.finishUpload(Common.config["t_t"].format(date), 17, Common.config["tag"], Common.config["des"],
                                   source=Common.config["src"], no_reprint=0)
                    b.clear()
                break
            if not os.path.exists(i):
                Common.appendError("Upload File Not Exist {}".format(i))
            else:
                try:
                    b.preUpload(VideoPart(i, os.path.basename(i)))
                except Exception as e:
                    Common.appendError(e.__str__())
                    continue
            if not Common.forceNotEncode:
                os.remove(i)
        sleep(1800)  # 防抖，避免主播因特殊情况下播导致直接投递了
        i = Common.uploadQueue.get()
    Common.appendUploadStatus("Upload Daemon Quiting")


b = Bilibili()
b.login(Common.config["b_u"], Common.config["b_p"])
t = threading.Thread(target=download, args=())
ut = threading.Thread(target=upload, args=())
et = threading.Thread(target=encode, args=())


def awakeEncode():
    global et
    if et.is_alive():
        return True
    et = threading.Thread(target=encode, args=())
    et.setDaemon(True)
    et.start()
    return False


def awakeDownload():
    global t
    if t.is_alive():
        return True
    t = threading.Thread(target=download, args=())
    t.setDaemon(True)
    t.start()
    Common.api.updRoomInfo()
    return False


def awakeUpload():
    global ut
    if ut.is_alive():
        return True
    ut = threading.Thread(target=upload, args=())
    ut.setDaemon(True)
    ut.start()
    return False


def run():
    global isEncode, isDownload
    Common.refreshDownloader()
    if not Common.api.isValidRoom:
        Common.appendError("[{}]房间未找到".format(Common.config["l_u"]))
        return
    awakeEncode()
    _count = 0
    while True:
        if Common.api.isLive and not Common.forceNotBroadcasting:
            if not Common.forceNotDownload:
                awakeDownload()
            awakeUpload()
            awakeEncode()
            if _count % 15 == 14:
                try:
                    Common.api.updRoomInfo()
                    _count = 0
                    _count_error = 0
                except Exception as e:
                    Common.appendError(e.__str__())
                    time.sleep(5)
                    continue
            time.sleep(5)
        else:
            if not isEncode and not isDownload:
                Common.uploadQueue.put(True)
                isEncode = True
                isDownload = True
            time.sleep(60)
            try:
                Common.api.updRoomInfo()
            except Exception as e:
                Common.appendError(e.__str__())
                Common.refreshDownloader()
            if not Common.api.roomLiver:
                Common.refreshDownloader()
            if Common.forceStartEncodeThread:
                awakeEncode()
                Common.forceStartEncodeThread = False
            if Common.forceStartUploadThread:
                awakeUpload()
                Common.forceStartUploadThread = False
