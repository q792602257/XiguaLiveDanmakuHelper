import os
from glob import glob
from time import sleep
from flask_cors import CORS
from flask import Flask, jsonify, request, redirect, render_template, Response
import Common
import threading
from liveDownloader import run as RUN
import psutil

app = Flask("liveStatus")
app.config['JSON_AS_ASCII'] = False
CORS(app, supports_credentials=True)
# url_for('static', filename='index.html')
# url_for('static', filename='index.js')


@app.route("/")
def index():
    return redirect("/static/index.html")

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
    Common.reloadConfig()
    return jsonify({"message":"ok","code":200,"status":0,"data":request.form})


@app.route("/encode/insert", methods=["POST"])
def insertEncode():
    if "filename" in request.form:
        Common.encodeQueue.put(request.form["filename"])
        return jsonify({"message":"ok","code":200,"status":0})


@app.route("/upload/insert", methods=["POST"])
def insertUpload():
    if "filename" in request.form:
        Common.uploadQueue.put(request.form["filename"])
        return jsonify({"message":"ok","code":200,"status":0})


@app.route("/upload/finish", methods=["POST"])
def finishUpload():
    Common.uploadQueue.put(True)
    return jsonify({"message":"ok","code":200,"status":0})


@app.route("/stats", methods=["GET"])
def getAllStats():
    _disk = psutil.disk_usage("/")
    return jsonify({"message":"ok","code":200,"status":0,"data":{
        "download":Common.downloadStatus,
        "encode": Common.encodeStatus,
        "encodeQueueSize": Common.encodeQueue.qsize(),
        "upload": Common.uploadStatus,
        "uploadQueueSize": Common.uploadQueue.qsize(),
        "error": Common.errors,
        "broadcast": {
            "broadcaster": Common.broadcaster.__str__(),
            "isBroadcasting": Common.isBroadcasting,
            "streamUrl": Common.streamUrl,
            "updateTime": Common.updateTime
        },
        "config": {
            "forceNotBroadcasting": Common.forceNotBroadcasting,
            "forceStopDownload": Common.forceStopDownload,
            "forceNotUpload": Common.forceNotUpload,
            "forceNotEncode": Common.forceNotEncode,
        },
    }})


@app.route("/stats/device", methods=["GET"])
def getDeviceStatus():
    _disk = psutil.disk_usage("/")
    _mem  = psutil.virtual_memory()
    return jsonify({"message":"ok","code":200,"status":0,"data":{
        "status": {
            "memTotal": Common.parseSize(_mem.total),
            "memUsed": Common.parseSize(_mem.used),
            "memUsage": _mem.percent,
            "diskTotal": Common.parseSize(_disk.total),
            "diskUsed": Common.parseSize(_disk.used),
            "diskUsage": _disk.percent,
            "cpu": psutil.cpu_percent(),
        },
    }})


@app.route("/stats/broadcast", methods=["GET"])
def getBroadcastStats():
    return jsonify({"message":"ok","code":200,"status":0,"data":{
        "broadcast": {
            "broadcaster": Common.broadcaster.__str__(),
            "isBroadcasting": Common.isBroadcasting,
            "streamUrl": Common.streamUrl,
            "updateTime": Common.updateTime
        }
    }})


@app.route("/stats/config", methods=["GET"])
def getConfigStats():
    return jsonify({"message":"ok","code":200,"status":0,"data":{
        "config": {
            "forceNotBroadcasting": Common.forceNotBroadcasting,
            "forceStopDownload": Common.forceStopDownload,
            "forceNotUpload": Common.forceNotUpload,
        }
    }})


@app.route("/stats/download", methods=["GET"])
def getDownloadStats():
    return jsonify({"message":"ok","code":200,"status":0,"data":{
        "download":Common.downloadStatus,
    }})


@app.route("/stats/encode", methods=["GET"])
def getEncodeStats():
    return jsonify({"message":"ok","code":200,"status":0,"data":{
        "encode": Common.encodeStatus,
        "encodeQueueSize": Common.encodeQueue.qsize(),
    }})


@app.route("/stats/upload", methods=["GET"])
def getUploadStats():
    return jsonify({"message":"ok","code":200,"status":0,"data":{
        "upload": Common.uploadStatus,
        "uploadQueueSize": Common.uploadQueue.qsize(),
    }})


@app.route("/files/", methods=["GET"])
def fileIndex():
    a = []
    for i in (glob("*.mp4") + glob("*.flv")):
        a.append({
            "name": i,
            "size": Common.parseSize(os.path.getsize(i))
        })
    return render_template("files.html",files=a)


@app.route("/files/download/<path>", methods=["GET"])
def fileDownload(path):
    def generate(file):
        with open(file, "rb") as f:
            for row in f:
                yield row
    return Response(generate(path), mimetype='application/octet-stream')


def SubThread():
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


p = threading.Thread(target = SubThread)
p.setDaemon(True)
p.start()
