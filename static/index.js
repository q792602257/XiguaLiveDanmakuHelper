function taskUpdate(){
    $.ajax(
        "/stats",
        {
            success: function (res){
                $("#broadcaster").text(res.data.broadcast.broadcaster)
                $("#isBroadcasting").text(res.data.broadcast.isBroadcasting)
                $("#streamUrl").text(res.data.broadcast.streamUrl)
                $("#forceNotBroadcasting").text(res.data.config.forceNotBroadcasting)
                $("#forceStopDownload").text(res.data.config.forceStopDownload)
                $("#forceNotUpload").text(res.data.config.forceNotUpload)
                $("#forceNotEncode").text(res.data.config.forceNotEncode)
                $("#updateTime").text(res.data.broadcast.updateTime)
                $("#download").html(function(){
                    var ret = ""
                    res.data.download.reverse().forEach(function(obj){
                        ret += "<tr><td>" + obj.datetime + "</td><td>" + obj.message + "</td></tr>"
                    })
                    return "<table>" + ret + "</table>"
                })
                $("#encode").html(function(){
                    var ret = ""
                    res.data.encode.reverse().forEach(function(obj){
                        ret += "<tr><td>" + obj.datetime + "</td><td>" + obj.message + "</td></tr>"
                    })
                    return "<table>" + ret + "</table>"
                })
                $("#upload").html(function(){
                    var ret = ""
                    res.data.upload.reverse().forEach(function(obj){
                        ret += "<tr><td>" + obj.datetime + "</td><td>" + obj.message + "</td></tr>"
                    })
                    return "<table>" + ret + "</table>"
                })
                $("#error").html(function(){
                    var ret = ""
                    res.data.error.reverse().forEach(function(obj){
                        ret += "<tr><td>" + obj.datetime + "</td><td>" + obj.message + "</td></tr>"
                    })
                    return "<table>" + ret + "</table>"
                })
            }
        }
    )
}
function deviceUpdate(){
        $.ajax(
        "/stats/device",
        {
            success: function (res){
                $("#memTotal").text(res.data.status.memTotal)
                $("#memUsed").text(res.data.status.memUsed)
                $("#memUsage").text(res.data.status.memUsage)
                $("#diskTotal").text(res.data.status.diskTotal)
                $("#diskUsed").text(res.data.status.diskUsed)
                $("#diskUsage").text(res.data.status.diskUsage)
                $("#cpu").text(res.data.status.cpu)
                $("#memUsageP").val(res.data.status.memUsage)
                $("#diskUsageP").val(res.data.status.diskUsage)
                $("#cpuP").val(res.data.status.cpu)
            }
        }
    )
}
taskUpdate()
deviceUpdate()
setInterval(taskUpdate,10000)
setInterval(deviceUpdate,5000)