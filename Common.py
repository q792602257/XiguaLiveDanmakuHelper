import queue
from datetime import datetime

from api import XiGuaLiveApi
import json

_config_fp = open("config.json","r",encoding="utf8")
config = json.load(_config_fp)
_config_fp.close()


def reloadConfig():
    global config, _config_fp
    _config_fp = open("config.json", "r", encoding="utf8")
    config = json.load(_config_fp)
    _config_fp.close()


dt_format="%Y/%m/%d %H:%M:%S"

broadcaster = ""
streamUrl = ""
isBroadcasting = False
updateTime = ""

forceStopDownload = False
forceNotBroadcasting = False
forceNotUpload = False

uploadQueue = queue.Queue()
encodeQueue = queue.Queue()

uploadStatus = []
downloadStatus = []
encodeStatus = []
errors = []


def parseSize(size):
    K = size/1024.0
    if K > 1000:
        M = K/1024.0
        if M > 1000:
            return "{:.2f}GB".format(M / 1024.0)
        else:
            return "{:.2f}MB".format(M)
    else:
        return "{:.2f}MB".format(K)


def appendUploadStatus(obj):
    global uploadStatus
    if isinstance(obj, dict):
        if "datetime" not in obj:
            obj["datetime"] = datetime.strftime(datetime.now(), dt_format)
        uploadStatus.append(obj)
    else:
        uploadStatus.append({
            "datetime": datetime.strftime(datetime.now(), dt_format),
            "message": str(obj)
        })
    uploadStatus = uploadStatus[-config["l_c"]:]


def modifyLastUploadStatus(obj):
    global uploadStatus
    if isinstance(obj, dict):
        if "datetime" not in obj:
            obj["datetime"] = datetime.strftime(datetime.now(), dt_format)
        uploadStatus[-1] = obj
    else:
        uploadStatus[-1]["message"] = str(obj)
        uploadStatus[-1]["datetime"] = datetime.strftime(datetime.now(), dt_format)


def appendEncodeStatus(obj):
    global encodeStatus
    if isinstance(obj, dict):
        if "datetime" not in obj:
            obj["datetime"] = datetime.strftime(datetime.now(), dt_format)
        encodeStatus.append(obj)
    else:
        encodeStatus.append({
            "datetime": datetime.strftime(datetime.now(), dt_format),
            "message": str(obj)
        })
    encodeStatus = encodeStatus[-config["l_c"]:]


def modifyLastEncodeStatus(obj):
    global encodeStatus
    if isinstance(obj, dict):
        if "datetime" not in obj:
            obj["datetime"] = datetime.strftime(datetime.now(), dt_format)
        encodeStatus[-1] = obj
    else:
        encodeStatus[-1]["message"] = str(obj)
        encodeStatus[-1]["datetime"] = datetime.strftime(datetime.now(), dt_format)


def appendDownloadStatus(obj):
    global downloadStatus
    if isinstance(obj, dict):
        if "datetime" not in obj:
            obj["datetime"] = datetime.strftime(datetime.now(), dt_format)
        downloadStatus.append(obj)
    else:
        downloadStatus.append({
            "datetime": datetime.strftime(datetime.now(), dt_format),
            "message": str(obj)
        })
    downloadStatus = downloadStatus[-config["l_c"]:]


def modifyLastDownloadStatus(obj):
    global downloadStatus
    if isinstance(obj, dict):
        if "datetime" not in obj:
            obj["datetime"] = datetime.strftime(datetime.now(), dt_format)
        downloadStatus[-1] = obj
    else:
        downloadStatus[-1]["message"] = str(obj)
        downloadStatus[-1]["datetime"] = datetime.strftime(datetime.now(), dt_format)


def appendError(obj):
    global errors
    if isinstance(obj, dict):
        if "datetime" not in obj:
            obj["datetime"] = datetime.strftime(datetime.now(), dt_format)
        errors.append(obj)
    else:
        errors.append({
            "datetime": datetime.strftime(datetime.now(), dt_format),
            "message": str(obj)
        })
    errors = errors[-config["elc"]:]


class downloader(XiGuaLiveApi):
    files = []
    playlist = None

    def updRoomInfo(self):
        global broadcaster, isBroadcasting, updateTime, forceNotBroadcasting, forceStopDownload
        super(downloader, self).updRoomInfo()
        updateTime = datetime.strftime(datetime.now(), dt_format)
        broadcaster = self.roomLiver
        isBroadcasting = self.isLive
        if self.isLive:
            self.updPlayList()
        else:
            forceStopDownload = False
            forceNotBroadcasting = False
            self.playlist = False
            self.files = []

    def updPlayList(self):
        global streamUrl
        if self.isLive:
            if "stream_url" in self._rawRoomInfo:
                if self.playlist is None:
                    self.playlist = False
                else:
                    self.playlist = self._rawRoomInfo["stream_url"]["flv_pull_url"]
                    self.playlist = self.playlist.replace("_uhd", "").replace("_sd", "").replace("_ld", "")
                    streamUrl = self.playlist

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

