from time import sleep

from flask import Flask, jsonify, request
import Common
import threading
from liveDownloader import run as RUN

app = Flask("liveStatus")
app.config['JSON_AS_ASCII'] = False


@app.route("/config", methods=["GET"])
def readConfig():
    config = Common.config.copy()
    config.pop("b_p")
    config.pop("mtd")
    config.pop("del")
    config.pop("mv")
    return jsonify(config)


@app.route("/config", methods=["POST"])
def writeConfig():
    # TODO : 完善
    return jsonify({"message":"ok","code":200,"status":0,"data":request.form})


@app.route("/stats", methods=["GET"])
def getAllStats():
    return jsonify({"message":"ok","code":200,"status":0,"data":{
        "download":Common.downloadStatus,
        "encode": Common.encodeStatus,
        "upload": Common.uploadStatus,
        "error": Common.errors,
        "broadcast": {
            "broadcaster": Common.broadcaster.__str__(),
            "isBroadcasting": Common.isBroadcasting,
            "streamUrl": Common.streamUrl,
            "updateTime": Common.updateTime
        }
    }})


@app.route("/stats/broadcast", methods=["GET"])
def geBroadcastStats():
    return jsonify({"message":"ok","code":200,"status":0,"data":{
        "broadcast": {
            "broadcaster": Common.broadcaster.__str__(),
            "isBroadcasting": Common.isBroadcasting,
            "streamUrl": Common.streamUrl,
            "updateTime": Common.updateTime
        }
    }})


@app.route("/stats/download", methods=["GET"])
def geDownloadStats():
    return jsonify({"message":"ok","code":200,"status":0,"data":{
        "download":Common.downloadStatus,
    }})


@app.route("/stats/encode", methods=["GET"])
def getEncodeStats():
    return jsonify({"message":"ok","code":200,"status":0,"data":{
        "encode": Common.encodeStatus,
    }})


@app.route("/stats/upload", methods=["GET"])
def getUploadStats():
    return jsonify({"message":"ok","code":200,"status":0,"data":{
        "upload": Common.uploadStatus,
    }})


t = threading.Thread(target=RUN, args=(Common.config['l_u'],))
t.setDaemon(True)
t.start()
while True:
    if t.is_alive():
        sleep(240)
    else:
        t = threading.Thread(target=RUN, args=(Common.config['l_u'],))
        t.setDaemon(True)
        t.start()
