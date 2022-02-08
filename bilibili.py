from bilibiliuploader import core, VideoPart


class Bilibili:
    def __init__(self):
        self.access_token = ""
        self.session_id = ""
        self.user_id = ""
        self.parts = []

    def login(self):
        from Common import appendOperation
        with open("access_token", "r") as f:
            self.access_token = f.read(64).strip()
        self.session_id, self.user_id, expires = core.login_by_access_token(self.access_token)
        appendOperation("B站登录，UID【{}】，过期时间【{}】".format(self.user_id, expires))

    def upload(self,
               parts,
               title,
               tid,
               tag,
               desc,
               source='',
               cover='',
               no_reprint=1,
               ):
        """

        :param parts: e.g. VideoPart('part path', 'part title', 'part desc'), or [VideoPart(...), VideoPart(...)]
        :type parts: VideoPart or list<VideoPart>
        :param title: video's title
        :type title: str
        :param tid: video type, see: https://member.bilibili.com/x/web/archive/pre
                                  or https://github.com/uupers/BiliSpider/wiki/%E8%A7%86%E9%A2%91%E5%88%86%E5%8C%BA%E5%AF%B9%E5%BA%94%E8%A1%A8
        :type tid: int
        :param tag: video's tag
        :type tag: list<str>
        :param desc: video's description
        :type desc: str
        :param source: (optional) 转载地址
        :type source: str
        :param cover: (optional) cover's URL, use method *cover_up* to get
        :type cover: str
        :param no_reprint: (optional) 0=可以转载, 1=禁止转载(default)
        :type no_reprint: int
        """
        self.preUpload(parts)
        self.finishUpload(title, tid, tag, desc, source, cover, no_reprint)
        self.clear()

    def preUpload(self, parts, max_retry=5):
        """
        :param max_retry:
        :param parts: e.g. VideoPart('part path', 'part title', 'part desc'), or [VideoPart(...), VideoPart(...)]
        :type parts: VideoPart or list<VideoPart>
        """
        from Common import appendUploadStatus, modifyLastUploadStatus, appendError
        if not isinstance(parts, list):
            parts = [parts]

        def log_status(video_part: VideoPart, chunks_index: int, chunks_num: int):
            modifyLastUploadStatus("Uploading >{}< @ {:.2f}%".format(video_part.path, 100.0 * chunks_index / chunks_num))
        for part in parts:
            appendUploadStatus("Start Uploading >{}<".format(part.path))
            status = core.upload_video_part(self.access_token, self.session_id, self.user_id, part, max_retry, cb=log_status)
            if status:
                modifyLastUploadStatus("Upload >{}< Failed".format(part.path))
                continue
            # 上传完毕
            modifyLastUploadStatus("Upload >{}< Finished；【{}】".format(part.path, part.server_file_name))
            self.parts.append(part)

    def finishUpload(self,
                     title,
                     tid,
                     tag,
                     desc,
                     source='',
                     cover='',
                     no_reprint=1,
                     ):
        """
        :param title: video's title
        :type title: str
        :param tid: video type, see: https://member.bilibili.com/x/web/archive/pre
                                  or https://github.com/uupers/BiliSpider/wiki/%E8%A7%86%E9%A2%91%E5%88%86%E5%8C%BA%E5%AF%B9%E5%BA%94%E8%A1%A8
        :type tid: int
        :param tag: video's tag
        :type tag: list<str>
        :param desc: video's description
        :type desc: str
        :param source: (optional) 转载地址
        :type source: str
        :param cover: (optional) cover's URL, use method *cover_up* to get
        :type cover: str
        :param no_reprint: (optional) 0=可以转载, 1=禁止转载(default)
        :type no_reprint: int
        :param copyright: (optional) 0=转载的, 1=自制的(default)
        :type copyright: int
        """
        from Common import appendUploadStatus, modifyLastUploadStatus, appendError
        if len(self.parts) == 0:
            return
        appendUploadStatus("[{}]投稿中，请稍后".format(title))
        copyright = 2 if source else 1
        try:
            avid, bvid = core.upload(self.access_token, self.session_id, self.user_id, self.parts, copyright,
                        title=title, tid=tid, tag=','.join(tag), desc=desc, source=source, cover=cover, no_reprint=no_reprint)
            modifyLastUploadStatus("[{}]投稿成功；AVID【{}】，BVID【{}】".format(title, avid, bvid))
            self.clear()
        except Exception as e:
            modifyLastUploadStatus("[{}]投稿失败".format(title))
            appendError(e)


    def reloadFromPrevious(self):
        ...

    def clear(self):
        self.parts = []