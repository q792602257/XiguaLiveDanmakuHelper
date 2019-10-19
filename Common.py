import os
import queue
from datetime import datetime
from glob import glob

import psutil
from api import XiGuaLiveApi
import json
import threading
from bilibili import *

# 默认设置
config = {
    # 录像的主播名
    "l_u": "永恒de草薙",
    "b_u": "自己的B站账号",
    "b_p": "自己的B站密码",
    # 标题及预留时间位置
    "t_t": "【永恒de草薙直播录播】直播于 {}",
    # 标签
    "tag": ["永恒de草薙", "三国", "三国战记", "直播录像", "录播", "怀旧", "街机"],
    # 描述
    "des": "西瓜直播 https://live.ixigua.com/userlive/97621754276 \n自动投递\n原主播：永恒de草薙\n直播时间：晚上6点多到凌晨4点左右",
    # 来源， 空则为自制
    "src": "",
    # Log条数
    "l_c": 5,
    # 错误Log条数
    "elc": 10,
    "p_s": 2141000000,
    "max": 75,
    "exp": 1,
    "dow": "echo 'clean'",
    # 仅下载
    "dlO": True,
    # 下播延迟投稿
    "dly": 30
}

_config_fp = open("config.json", "r", encoding="utf8")
_config = json.load(_config_fp)
_config_fp.close()
del _config_fp
doCleanTime = datetime.now()
_clean_flag = None
delay = 30
b = Bilibili()

network = [{
    "currentTime": datetime.now(),
    "out": {
        "currentByte": psutil.net_io_counters().bytes_sent,
    },
    "in": {
        "currentByte": psutil.net_io_counters().bytes_recv,
    }
}, {
    "currentTime": datetime.now(),
    "out": {
        "currentByte": psutil.net_io_counters().bytes_sent,
    },
    "in": {
        "currentByte": psutil.net_io_counters().bytes_recv,
    }
}]


def resetDelay():
    global delay
    delay = config['dly']


def doDelay():
    global delay
    if delay < 0:
        resetDelay()
    sleep(60)
    delay -= 1
    return delay < 0


def updateNetwork():
    global network
    network.append({
        "currentTime": datetime.now(),
        "out": {
            "currentByte": psutil.net_io_counters().bytes_sent,
        },
        "in": {
            "currentByte": psutil.net_io_counters().bytes_recv,
        }
    })
    network = network[-3:]


def getTimeDelta(a, b):
    sec = (a - b).seconds
    ms  = (a - b).microseconds
    return sec+(ms/100000.0)


def _doClean(_force=False):
    global doCleanTime, _clean_flag
    _disk = psutil.disk_usage(".")
    if _disk.percent > config["max"] or getTimeDelta(datetime.now(), doCleanTime) > config["exp"]*86400 or _force:
        _clean_flag = True
        doCleanTime = datetime.now()
        appendOperation("执行配置的清理命令")
        os.system(config["dow"])
        appendOperation("执行配置的清理命令完毕")
        doCleanTime = datetime.now()
    _clean_flag = False


def doClean(_force=False):
    if _clean_flag:
        return
    p = threading.Thread(target=_doClean, args=(_force,))
    p.setDaemon(True)
    p.start()


def getCurrentStatus():
    _disk = psutil.disk_usage(".")
    _mem  = psutil.virtual_memory()
    _net  = psutil.net_io_counters()
    _delta= getTimeDelta(network[-1]["currentTime"], network[-2]["currentTime"])
    if 60 > _delta > 1:
        _inSpeed = (network[-1]["in"]["currentByte"] - network[-2]["in"]["currentByte"]) / _delta
        _outSpeed = (network[-1]["out"]["currentByte"] - network[-2]["out"]["currentByte"]) / _delta
    else:
        _outSpeed = (network[-1]["in"]["currentByte"] - network[-2]["in"]["currentByte"])
        _inSpeed = (network[-1]["out"]["currentByte"] - network[-2]["out"]["currentByte"])
    updateNetwork()
    return {
        "memTotal": parseSize(_mem.total),
        "memUsed": parseSize(_mem.used),
        "memUsage": _mem.percent,
        "diskTotal": parseSize(_disk.total),
        "diskUsed": parseSize(_disk.used),
        "diskUsage": _disk.percent,
        "cpu": psutil.cpu_percent(),
        "outSpeed": parseSize(_outSpeed),
        "inSpeed": parseSize(_inSpeed),
        "doCleanTime": datetime.strftime(doCleanTime, dt_format),
        "fileExpire": config["exp"],
    }


def reloadConfig():
    global config
    _config_fp = open("config.json", "r", encoding="utf8")
    _config = json.load(_config_fp)
    config.update(_config)
    _config_fp.close()


dt_format = "%Y/%m/%d %H:%M:%S"

broadcaster = ""
streamUrl = ""
isBroadcasting = False
updateTime = ""

forceNotDownload = False
forceNotBroadcasting = False
forceNotUpload = False
forceNotEncode = False
if config["dlO"] is True:
    forceNotUpload = True
    forceNotEncode = True
forceStartEncodeThread = False
forceStartUploadThread = False

uploadQueue = queue.Queue()
encodeQueue = queue.Queue()

uploadStatus = []
downloadStatus = []
encodeStatus = []
errors = []
operations = []


def appendOperation(obj):
    global operations
    if isinstance(obj, dict):
        if "datetime" not in obj:
            obj["datetime"] = datetime.strftime(datetime.now(), dt_format)
        operations.append(obj)
    else:
        operations.append({
            "datetime": datetime.strftime(datetime.now(), dt_format),
            "message": str(obj)
        })
    operations = operations[-config["elc"]:]


def parseSize(size):
    K = size / 1024.0
    if K > 1000:
        M = K / 1024.0
        if M > 1000:
            return "{:.2f}GB".format(M / 1024.0)
        else:
            return "{:.2f}MB".format(M)
    else:
        return "{:.2f}KB".format(K)


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


def loginBilibili():
    if "dlO" not in config or config["dlO"] is False or forceNotUpload is False:
        res = b.login(config["b_u"], config["b_p"])
        appendOperation("登陆账号，结果为：[{}]".format(res))


class downloader(XiGuaLiveApi):
    playlist = None


    def updRoomInfo(self):
        doClean()
        super(downloader, self).updRoomInfo()

    def _updateRoomOnly(self):
        global broadcaster, isBroadcasting, updateTime
        super(downloader, self)._updateRoomOnly()
        updateTime = datetime.strftime(datetime.now(), dt_format)
        broadcaster = self.roomLiver
        isBroadcasting = self.isLive
        if self.isLive:
            self.updPlayList()
        else:
            self.playlist = False

    def updPlayList(self):
        global streamUrl
        if self.isLive and "stream_url" in self._rawRoomInfo:
            self.playlist = self._rawRoomInfo["stream_url"]["flv_pull_url"]
            self.playlist = self.playlist.replace("_uhd", "").replace("_sd", "").replace("_ld", "")
            streamUrl = self.playlist
        else:
            streamUrl = None
            self.playlist = None

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


api = downloader(config["l_u"])


def refreshDownloader():
    global api
    api = downloader(config["l_u"])


def uploadVideo(name):
    if not os.path.exists(name):
        Common.appendError("Upload File Not Exist {}".format(name))
    if forceNotUpload is False:
        b.preUpload(VideoPart(name, os.path.basename(name)))
    else:
        appendUploadStatus("设置了不上传，所以[{}]不会上传了".format(name))
    if not Common.forceNotEncode:
        os.remove(name)

def publishVideo(date):
    if forceNotUpload is False:
        b.finishUpload(config["t_t"].format(date), 17, config["tag"], config["des"],
                              source=config["src"], no_reprint=0)
        b.clear()
    else:
        appendUploadStatus("设置了不上传，所以[{}]的录播不会上传了".format(date))
