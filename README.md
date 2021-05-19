# XiguaLiveDanmakuHelper

## 现在西瓜视频搜索接口无法使用，建议开发者自己找到自己的用户ID，写死加载即可

### 因西瓜直播弹幕接口换成了ProtoBuf，已经尝试解析出了部分proto

### 从安卓9.4版本后 *（大概是）* 发现需要连接Websocket才能获取弹幕，且又是魔改protobuf（搞不懂），手动断开Websocket后才会轮询请求

### ~~西瓜直播弹幕助手--界面版~~

> 界面版：[q792602257/XiguaDanmakuHelperGUI](https://github.com/q792602257/XiguaDanmakuHelperGUI "C# ver")
> #### 该项目已经荒废，除非你知道如何开发，否则不建议使用

### 西瓜直播弹幕接口```api.py```

> - 基于安卓9.6.6(96615)

### 西瓜直播弹幕助手--礼物端```WinMain.py```

### 西瓜直播弹幕助手--录播端```WebMain.py```

> - 能够自动进行ffmpeg转码
> - 转码后自动上传至B站
> - 顺便还能自己清理录播的文件（移动到一个位置，执行shell命令，上传百度云）
> - 把录像文件分一定大小保存（B站有限制，但是不知道是多少）
> - 少部分错误包容机制
> - 有一个简单的WEB页面，及简单的控制接口

### ~~计划更新~~

### 随缘更新
