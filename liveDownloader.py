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


def download(url):
    global isDownload
    path = datetime.strftime(datetime.now(), "%Y%m%d_%H%M.flv")
    p = requests.get(url, stream=True)
    if p.status_code != 200:
        Common.appendDownloadStatus("Download with Response 404, maybe broadcaster is not broadcasting")
        return True
    isDownload = True
    Common.appendDownloadStatus("Download >{}< Start".format(path))
    f = open(path, "wb")
    try:
        for t in p.iter_content(chunk_size=64 * 1024):
            if t:
                f.write(t)
            else:
                raise Exception("`t` is not valid")
            _size = os.path.getsize(path)
            Common.modifyLastDownloadStatus("Downloading >{}< @ {:.2f}%".format(path, 100.0 * _size/Common.config["p_s"]))
            if _size > Common.config["p_s"] or Common.forceNotDownload:
                Common.modifyLastDownloadStatus("Download >{}< Exceed MaxSize".format(path))
                break
    except Exception as e:
        Common.appendError("Download >{}< With Exception {}".format(path, e.__str__()))
    f.close()
    isDownload = False
    Common.modifyLastDownloadStatus("Download >{}< Finished".format(path))
    if os.path.getsize(path) < 1024 * 1024:
        Common.modifyLastDownloadStatus("Downloaded File >{}< is too small, will ignore it".format(path))
        os.remove(path)
        return False
    if Common.forceNotDownload:
        Common.modifyLastDownloadStatus("设置了不下载，所以[{}]不会下载".format(path))
        return
    else:
        Common.encodeQueue.put(path)
        download(url)


def encode():
    global isEncode
    Common.appendEncodeStatus("Encode Daemon Starting")
    while True:
        isEncode = False
        i = Common.encodeQueue.get()
        if Common.forceNotEncode:
            Common.appendEncodeStatus("设置了不编码，所以[{}]不会编码".format(i))
            Common.uploadQueue.put(i)
            continue
        if os.path.exists(i):
            isEncode = True
            if os.path.getsize(i) < 8 * 1024 * 1024:
                Common.appendEncodeStatus("Encoded File >{}< is too small, will ignore it".format(i))
                continue
            Common.appendEncodeStatus("Encoding >{}< Start".format(i))
            os.system("ffmpeg -i {} -c:v copy -c:a copy -f mp4 {} -y".format(i, i[:13] + ".mp4"))
            Common.uploadQueue.put(i[:13] + ".mp4")
            Common.modifyLastEncodeStatus("Encode >{}< Finished".format(i))


def upload(date=datetime.strftime(datetime.now(), "%Y_%m_%d")):
    Common.appendUploadStatus("Upload Daemon Starting")
    i = Common.uploadQueue.get()
    while True:
        Common.doClean()
        if Common.forceNotUpload:
            Common.appendUploadStatus("设置了不上传，所以[{}]不会上传了".format(i))
            i = Common.uploadQueue.get()
            continue
        if isinstance(i, bool):
            if i is True:
                b.finishUpload(Common.config["t_t"].format(date), 17, Common.config["tag"], Common.config["des"],
                               source=Common.config["src"], no_reprint=0)
                b.clear()
            break
        if not os.path.exists(i):
            Common.appendError("Upload File Not Exist {}".format(i))
            i = Common.uploadQueue.get()
            continue
        try:
            b.preUpload(VideoPart(i, os.path.basename(i)))
        except Exception as e:
            Common.appendError(e.__str__())
            continue
        if not Common.forceNotEncode:
            os.remove(i)
        i = Common.uploadQueue.get()
    Common.appendUploadStatus("Upload Daemon Quiting")


b = Bilibili()
b.login(Common.config["b_u"], Common.config["b_p"])


def run():
    global isEncode, isDownload
    et = threading.Thread(target=encode, args=())
    et.setDaemon(True)
    et.start()
    if not Common.api.isValidRoom:
        Common.appendError("[{}]房间不存在".format(Common.config["l_u"]))
        return
    d = None
    t = threading.Thread(target=download)
    ut = threading.Thread(target=upload, args=(d,))
    _count = 0
    _count_error = 0
    while True:
        if Common.api.isLive and not Common.forceNotBroadcasting:
            if d is None:
                d = datetime.strftime(datetime.now(), "%Y_%m_%d")
            if not t.is_alive() and not Common.forceNotDownload:
                try:
                    Common.api.updRoomInfo()
                    _count = 0
                    _count_error = 0
                except Exception as e:
                    Common.appendError(e.__str__())
                    continue
                _count_error += 1
                _preT = Common.api.playlist
                if not _preT:
                    Common.api.updRoomInfo()
                    continue
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
                    Common.api.updRoomInfo()
                    _count = 0
                    _count_error = 0
                except Exception as e:
                    Common.appendError(e.__str__())
                    time.sleep(20)
                    _count_error += 1
                    continue
            if _count_error > 15:
                Common.api.isLive = False
            _count += 1
            time.sleep(20)
        else:
            if d is not None:
                d = None
            if not isEncode and not isDownload:
                Common.uploadQueue.put(True)
                isEncode = True
                isDownload = True
                # print("主播未开播，等待1分钟后重试")
            time.sleep(60)
            try:
                Common.api.updRoomInfo()
                _count_error = 0
            except Exception as e:
                Common.appendError(e.__str__())
            if Common.forceStartEncodeThread:
                if not et.is_alive():
                    et = threading.Thread(target=encode, args=())
                    et.setDaemon(True)
                    et.start()
                Common.forceStartEncodeThread = False
            if Common.forceStartUploadThread:
                if not ut.is_alive():
                    d = datetime.strftime(datetime.now(), "%Y_%m_%d")
                    ut = threading.Thread(target=upload, args=(d,))
                    ut.setDaemon(True)
                    ut.start()
                Common.forceStartUploadThread = False
