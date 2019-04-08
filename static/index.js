function update(){
    $.ajax(
        "/stats",
        {
            success: function (res){
                $("#broadcaster").text(res.data.broadcast.broadcaster)
                $("#isBroadcasting").text(res.data.broadcast.isBroadcasting)
                $("#streamUrl").text(res.data.broadcast.streamUrl)
                $("#forceNotBroadcasting").text(res.data.config.forceNotBroadcasting)
                $("#forceStopDownload").text(res.data.config.forceStopDownload)
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
update()
setInterval(update,10000)