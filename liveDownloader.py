import shutil
import sys
import time
from datetime import datetime
import threading
import Common
import os
import requests


def download():
    session = requests.session()
    while Common.api.isLive and not Common.forceNotDownload:
        if not Common.streamUrl:
            Common.appendError("Download with No StreamUrl Specific")
            break
        path = datetime.strftime(datetime.now(), "%Y%m%d_%H%M.flv")
        p = session.get(Common.streamUrl, stream=True, timeout=10)
        if p.status_code != 200:
            Common.appendDownloadStatus("Download with Response {}".format(p.status_code))
            Common.api.updRoomInfo(True)
            break
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
        if os.path.getsize(path) < 1024 * 1024:
            Common.modifyLastDownloadStatus("Downloaded File >{}< is too small, will ignore it".format(path))
            os.remove(path)
            return False
        Common.encodeQueue.put(path)
        Common.api.updRoomInfo()


def encode():
    Common.appendEncodeStatus("Encode Daemon Starting")
    while True:
        i = Common.encodeQueue.get()
        Common.encodeVideo(i)


def upload():
    date = datetime.strftime(datetime.now(), "%Y_%m_%d")
    Common.appendUploadStatus("Upload Daemon Starting")
    i = Common.uploadQueue.get()
    while True:
        if i is True:
            Common.publishVideo(date)
            break
        try:
            Common.uploadVideo(i)
        except Exception as e:
            Common.appendError(e.__str__())
            time.sleep(120)
            continue
        i = Common.uploadQueue.get()
    Common.appendUploadStatus("Upload Daemon Quiting")


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
    Common.refreshDownloader()
    if not Common.api.isValidUser:
        Common.appendError("[{}]房间未找到".format(Common.config["l_u"]))
        return
    while True:
        if Common.api.isLive and not Common.forceNotBroadcasting:
            if not Common.forceNotDownload:
                awakeDownload()
            if not Common.forceNotUpload:
                awakeUpload()
            if not Common.forceNotEncode:
                awakeEncode()
            try:
                Common.api.updRoomInfo()
            except Exception as e:
                Common.appendError(e.__str__())
                time.sleep(2)
                continue
            time.sleep(0.5)
        else:
            try:
                Common.api.updRoomInfo()
            except Exception as e:
                Common.appendError(e.__str__())
                Common.refreshDownloader()
            if not Common.api.broadcaster:
                Common.refreshDownloader()
            if Common.forceStartEncodeThread:
                awakeEncode()
                Common.forceStartEncodeThread = False
            if Common.forceStartUploadThread:
                awakeUpload()
                Common.forceStartUploadThread = False
            if Common.doDelay():
                Common.uploadQueue.put(True)
                Common.isEncode = True
                Common.isUpload = True
            time.sleep(5)
