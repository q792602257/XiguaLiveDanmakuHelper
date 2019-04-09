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
                $("#inSpeed").text(res.data.status.inSpeed)
                $("#outSpeed").text(res.data.status.outSpeed)
            }
        }
    )
}

deviceUpdate()
setInterval(deviceUpdate,2000)
