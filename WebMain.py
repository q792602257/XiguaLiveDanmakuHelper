import os
from glob import glob
from time import sleep
from flask_cors import CORS
from flask import Flask, jsonify, request, render_template, Response, send_file
import Common
import threading
from liveDownloader import run as RUN

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app, supports_credentials=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/config", methods=["GET"])
def readConfig():
    config = Common.config.copy()
    return jsonify(config)


@app.route("/config", methods=["POST"])
def writeConfig():
    # TODO : 完善
    Common.appendOperation("更新配置")
    Common.reloadConfig()
    return jsonify({"message": "ok", "code": 200, "status": 0, "data": request.form})


@app.route("/force/not/upload", methods=["POST"])
def toggleForceNotUpload():
    Common.forceNotUpload = not Common.forceNotUpload
    Common.appendOperation("将强制不上传的值改为：{}".format(Common.forceNotUpload))
    return jsonify({"message": "ok", "code": 200, "status": 0, "data": {
        "forceNotUpload": Common.forceNotUpload,
    }})


@app.route("/force/not/encode", methods=["POST"])
def toggleForceNotEncode():
    Common.forceNotEncode = not Common.forceNotEncode
    Common.appendOperation("将强制不编码的值改为：{}".format(Common.forceNotEncode))
    return jsonify({"message": "ok", "code": 200, "status": 0, "data": {
        "forceNotEncode": Common.forceNotEncode,
    }})


@app.route("/force/not/download", methods=["POST"])
def toggleForceNotDownload():
    Common.forceNotDownload = not Common.forceNotDownload
    Common.appendOperation("将强制不下载的值改为：{}".format(Common.forceNotDownload))
    return jsonify({"message": "ok", "code": 200, "status": 0, "data": {
        "forceNotDownload": Common.forceNotDownload,
    }})


@app.route("/force/not/broadcast", methods=["POST"])
def toggleForceNotBroadcast():
    Common.forceNotBroadcasting = not Common.forceNotBroadcasting
    return jsonify({"message": "ok", "code": 200, "status": 0, "data": {
        "forceNotBroadcasting": Common.forceNotBroadcasting,
    }})


@app.route("/force/start/encode", methods=["POST"])
def toggleForceStartEncodeThread():
    Common.forceStartEncodeThread = True
    Common.appendOperation("强制运行编码线程")
    return jsonify({"message": "ok", "code": 200, "status": 0, "data": {
    }})


@app.route("/force/start/upload", methods=["POST"])
def toggleForceStartUploadThread():
    Common.forceStartUploadThread = True
    Common.appendOperation("强制运行上传线程")
    return jsonify({"message": "ok", "code": 200, "status": 0, "data": {
    }})


@app.route("/force/start/clean", methods=["POST"])
def startForceCleanDisk():
    Common.doClean(True)
    Common.appendOperation("强制执行清理程序")
    return jsonify({"message": "ok", "code": 200, "status": 0, "data": {
    }})


@app.route("/encode/insert", methods=["POST"])
def insertEncode():
    if "filename" in request.form and os.path.exists(request.form["filename"]):
        Common.appendOperation("添加编码文件：{}".format(request.form["filename"]))
        Common.encodeQueue.put(request.form["filename"])
        return jsonify({"message": "ok", "code": 200, "status": 0})
    else:
        return jsonify({"message": "no filename specific", "code": 400, "status": 1})


@app.route("/upload/insert", methods=["POST"])
def insertUpload():
    if "filename" in request.form and os.path.exists(request.form["filename"]):
        Common.appendOperation("添加上传文件：{}".format(request.form["filename"]))
        Common.uploadQueue.put(request.form["filename"])
        return jsonify({"message": "ok", "code": 200, "status": 0})
    else:
        return jsonify({"message": "no filename specific", "code": 400, "status": 1})


@app.route("/upload/finish", methods=["POST"])
def finishUpload():
    Common.appendOperation("设置当前已完成上传")
    Common.uploadQueue.put(True)
    return jsonify({"message": "ok", "code": 200, "status": 0})


@app.route("/stats", methods=["GET"])
def getAllStats():
    return jsonify({"message": "ok", "code": 200, "status": 0, "data": Common.collectInfomation()})


@app.route("/stats/device", methods=["GET"])
def getDeviceStatus():
    return jsonify({"message": "ok", "code": 200, "status": 0, "data": {
        "status": Common.getCurrentStatus(),
    }})


@app.route("/stats/config", methods=["GET"])
def getConfigStats():
    return jsonify({"message": "ok", "code": 200, "status": 0, "data": {
        "config": {
            "forceNotBroadcasting": Common.forceNotBroadcasting,
            "forceNotDownload": Common.forceNotDownload,
            "forceNotUpload": Common.forceNotUpload,
            "forceNotEncode": Common.forceNotEncode,
            "downloadOnly": Common.config['dlO'],
        }
    }})


@app.route("/account/reLogin", methods=["POST"])
def accountRelogin():
    res = Common.loginBilibili(True)
    return jsonify({"message": "ok", "code": 200, "status": 0, "data": {"result": res}})


@app.route("/files/", methods=["GET"])
def fileIndex():
    a = []
    for i in (glob("*.mp4") + glob("*.flv")):
        a.append({
            "name": i,
            "size": Common.parseSize(os.path.getsize(i))
        })
    return render_template("files.html", files=a)


@app.route("/files/download/<path>", methods=["GET"])
def fileDownload(path):
    if not (".mp4" in path or ".flv" in path):
        return Response(status=404)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        return Response(status=404)


def SubThread():
    t = threading.Thread(target=RUN, args=())
    t.setDaemon(True)
    t.start()
    while True:
        if t.is_alive():
            sleep(240)
        else:
            t = threading.Thread(target=RUN, args=())
            t.setDaemon(True)
            t.start()


if not app.debug:
    p = threading.Thread(target=SubThread)
    p.setDaemon(True)
    p.start()

if __name__ == "__main__":
    app.run()
