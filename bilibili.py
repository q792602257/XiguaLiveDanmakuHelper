# coding=utf-8

import os
import re
import json as JSON
from datetime import datetime
from time import sleep
import Common
import rsa
import math
import base64
import hashlib
import requests
from urllib import parse


class VideoPart:
    def __init__(self, path, title='', desc=''):
        self.path = path
        self.title = title
        self.desc = desc


class Bilibili:
    def __init__(self, cookie=None):
        self.files = []
        self.videos = []
        self.session = requests.session()
        self.session.keep_alive = False
        if cookie:
            self.session.headers["cookie"] = cookie
            self.csrf = re.search('bili_jct=(.*?);', cookie).group(1)
            self.mid = re.search('DedeUserID=(.*?);', cookie).group(1)
            self.session.headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
            self.session.headers['Referer'] = 'https://space.bilibili.com/{mid}/#!/'.format(mid=self.mid)
            # session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
            # session.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'

    def login(self, user, pwd):
        """

        :param user: username
        :type user: str
        :param pwd: password
        :type pwd: str
        :return: if success return True
                 else return msg json
        """
        APPKEY = '4409e2ce8ffd12b8'
        ACTIONKEY = 'appkey'
        BUILD = 101800
        DEVICE = 'android_tv_yst'
        MOBI_APP = 'android_tv_yst'
        PLATFORM = 'android'
        APPSECRET = '59b43e04ad6965f34319062b478f83dd'

        def md5(s):
            h = hashlib.md5()
            h.update(s.encode('utf-8'))
            return h.hexdigest()

        def sign(s):
            """

            :return: return sign
            """
            return md5(s + APPSECRET)

        def signed_body(body):
            """

            :return: body which be added sign
            """
            if isinstance(body, str):
                return body + '&sign=' + sign(body)
            elif isinstance(body, dict):
                ls = []
                for k, v in body.items():
                    ls.append(k + '=' + v)
                body['sign'] = sign('&'.join(ls))
                return body

        def getkey():
            """

            :return: hash, key
            """
            r = self.session.post(
                'https://passport.bilibili.com/api/oauth2/getKey',
                signed_body({'appkey': APPKEY}),
            )
            # {"ts":1544152439,"code":0,"data":{"hash":"99c7573759582e0b","key":"-----BEGIN PUBLIC----- -----END PUBLIC KEY-----\n"}}
            json = r.json()
            data = json['data']
            return data['hash'], data['key']

        def access_token_2_cookie(access_token):
            r = self.session.get(
                'https://passport.bilibili.com/api/login/sso?' + \
                signed_body(
                    'access_key={access_token}&appkey={appkey}&gourl=https%3A%2F%2Faccount.bilibili.com%2Faccount%2Fhome'
                        .format(access_token=access_token, appkey=APPKEY),
                ),
                allow_redirects=False,
            )
            return r.cookies.get_dict(domain=".bilibili.com")

        self.session.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        h, k = getkey()
        pwd = base64.b64encode(
            rsa.encrypt(
                (h + pwd).encode('utf-8'),
                rsa.PublicKey.load_pkcs1_openssl_pem(k.encode())
            )
        )
        user = parse.quote_plus(user)
        pwd = parse.quote_plus(pwd)

        r = self.session.post(
            'https://passport.snm0516.aisee.tv/api/tv/login',
            signed_body(
                'appkey={appkey}&build={build}&captcha=&channel=master&'
                'guid=XYEBAA3E54D502E37BD606F0589A356902FCF&mobi_app={mobi_app}&'
                'password={password}&platform={platform}&token=5598158bcd8511e2&ts=0&username={username}'
                    .format(appkey=APPKEY, build=BUILD, platform=PLATFORM, mobi_app=MOBI_APP, username=user,
                            password=pwd)),
        )
        try:
            json = r.json()
        except:
            return r.text

        if json['code'] == -105:
            # need captcha
            raise Exception('TODO: login with captcha')

        if json['code'] != 0:
            return r.text

        access_token = json['data']['token_info']['access_token']
        cookie_dict = access_token_2_cookie(access_token)
        cookie = '; '.join(
            '%s=%s' % (k, v)
            for k, v in cookie_dict.items()
        )
        self.session.headers["cookie"] = cookie

        self.csrf = re.search('bili_jct=(.*?);', cookie).group(1)
        self.mid = re.search('DedeUserID=(.*?);', cookie).group(1)
        self.session.headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
        self.session.headers['Referer'] = 'https://space.bilibili.com/{mid}/#!/'.format(mid=self.mid)

        return True

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

    def preUpload(self, parts):
        """
        :param parts: e.g. VideoPart('part path', 'part title', 'part desc'), or [VideoPart(...), VideoPart(...)]
        :type parts: VideoPart or list<VideoPart>
        """
        self.session.headers['Content-Type'] = 'application/json; charset=utf-8'
        if not isinstance(parts, list):
            parts = [parts]

        for part in parts:
            filepath = part.path
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)
            Common.appendUploadStatus("Upload >{}< Started".format(filepath))
            self.files.append(part)
            r = self.session.get('https://member.bilibili.com/preupload?'
                                 'os=upos&upcdn=ws&name={name}&size={size}&r=upos&profile=ugcupos%2Fyb&ssl=0'
                                 .format(name=filename, size=filesize))
            """return example
            {
                "upos_uri": "upos://ugc/i181012ws18x52mti3gg0h33chn3tyhp.mp4",
                "biz_id": 58993125,
                "endpoint": "//upos-hz-upcdnws.acgvideo.com",
                "endpoints": [
                    "//upos-hz-upcdnws.acgvideo.com",
                    "//upos-hz-upcdntx.acgvideo.com"
                ],
                "chunk_retry_delay": 3,
                "chunk_retry": 200,
                "chunk_size": 4194304,
                "threads": 2,
                "timeout": 900,
                "auth": "os=upos&cdn=upcdnws&uid=&net_state=4&device=&build=&os_version=&ak=×tamp=&sign=",
                "OK": 1
            }
            """
            json = r.json()
            upos_uri = json['upos_uri']
            endpoint = json['endpoint']
            auth = json['auth']
            biz_id = json['biz_id']
            chunk_size = json['chunk_size']
            self.session.headers['X-Upos-Auth'] = auth  # add auth header
            r = self.session.post(
                'https:{}/{}?uploads&output=json'.format(endpoint, upos_uri.replace('upos://', '')))
            # {"upload_id":"72eb747b9650b8c7995fdb0efbdc2bb6","key":"\/i181012ws2wg1tb7tjzswk2voxrwlk1u.mp4","OK":1,"bucket":"ugc"}
            json = r.json()
            upload_id = json['upload_id']
            with open(filepath, 'rb') as f:
                chunks_num = math.ceil(filesize / chunk_size)
                chunks_index = 0
                chunks_data = f.read(chunk_size)
                Common.modifyLastUploadStatus(
                    "Uploading >{}< @ {:.2f}%".format(filepath, 100.0 * chunks_index / chunks_num))
                while True:
                    _d = datetime.now()
                    if not chunks_data:
                        break
                    r = self.session.put('https:{endpoint}/{upos_uri}?'
                                         'partNumber={part_number}&uploadId={upload_id}&chunk={chunk}&chunks={chunks}&size={size}&start={start}&end={end}&total={total}'
                                         .format(endpoint=endpoint,
                                                 upos_uri=upos_uri.replace('upos://', ''),
                                                 part_number=chunks_index + 1,  # starts with 1
                                                 upload_id=upload_id,
                                                 chunk=chunks_index,
                                                 chunks=chunks_num,
                                                 size=len(chunks_data),
                                                 start=chunks_index * chunk_size,
                                                 end=chunks_index * chunk_size + len(chunks_data),
                                                 total=filesize,
                                                 ),
                                         chunks_data,
                                         )
                    if r.status_code != 200:
                        continue
                    chunks_data = f.read(chunk_size)
                    chunks_index += 1  # start with 0
                    Common.modifyLastUploadStatus(
                        "Uploading >{}< @ {:.2f}%".format(filepath, 100.0 * chunks_index / chunks_num))
                    if (datetime.now() - _d).seconds < 2:
                        sleep(1)

                # NOT DELETE! Refer to https://github.com/comwrg/bilibiliupload/issues/15#issuecomment-424379769
                self.session.post('https:{endpoint}/{upos_uri}?'
                                  'output=json&name={name}&profile=ugcupos%2Fyb&uploadId={upload_id}&biz_id={biz_id}'
                                  .format(endpoint=endpoint,
                                          upos_uri=upos_uri.replace('upos://', ''),
                                          name=filename,
                                          upload_id=upload_id,
                                          biz_id=biz_id,
                                          ),
                                  {"parts": [{"partNumber": i, "eTag": "etag"} for i in range(1, chunks_num + 1)]},
                                  )
            self.videos.append({'filename': upos_uri.replace('upos://ugc/', '').split('.')[0],
                                'title': part.title,
                                'desc': part.desc})
            Common.modifyLastUploadStatus("Upload >{}< Finished".format(filepath))
            __f = open("uploaded.json", "w")
            JSON.dump(self.videos, __f)

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
        """
        if len(self.videos) == 0:
            return
        Common.appendUploadStatus("[{}]投稿中，请稍后".format(title))
        self.session.headers['Content-Type'] = 'application/json; charset=utf-8'
        copyright = 2 if source else 1
        r = self.session.post('https://member.bilibili.com/x/vu/web/add?csrf=' + self.csrf,
                              json={
                                  "copyright": copyright,
                                  "source": source,
                                  "title": title,
                                  "tid": tid,
                                  "tag": ','.join(tag),
                                  "no_reprint": no_reprint,
                                  "desc": desc,
                                  "cover": cover,
                                  "mission_id": 0,
                                  "order_id": 0,
                                  "videos": self.videos}
                              )
        Common.modifyLastUploadStatus("[{}] Published | Result : {}".format(title, r.text))

    def reloadFromPrevious(self):
        if os.path.exists("uploaded.json"):
            __f = open("uploaded.json", "r")
            try:
                self.videos = JSON.load(__f)
                Common.appendUploadStatus("RELOAD SUCCESS")
            except:
                Common.appendUploadStatus("RELOAD Failed")
                self.videos = []
            __f.close()
            os.remove("uploaded.json")
        else:
            Common.appendUploadStatus("RELOAD Failed")
            self.videos = []

    def clear(self):
        self.files.clear()
        self.videos.clear()
        if (os.path.exists("uploaded.json")):
            os.remove("uploaded.json")

    def appendUpload(self,
                     aid,
                     parts,
                     title="",
                     tid="",
                     tag="",
                     desc="",
                     source='',
                     cover='',
                     no_reprint=1,
                     ):
        """
        :param aid: just aid
        :type aid: int
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
        self.session.headers['Content-Type'] = 'application/json; charset=utf-8'
        p = self.session.get("https://member.bilibili.com/x/web/archive/view?aid={}&history=".format(aid))
        j = p.json()
        if len(self.videos) == 0:
            for i in j['data']['videos']:
                self.videos.append({'filename': i['filename'],
                                    'title': i["title"],
                                    'desc': i["desc"]})
        if (title == ""): title = j["data"]["archive"]['title']
        if (tag == ""): tag = j["data"]["archive"]['tag']
        if (no_reprint == ""): no_reprint = j["data"]["archive"]['no_reprint']
        if (desc == ""): desc = j["data"]["archive"]['desc']
        if (source == ""): source = j["data"]["archive"]['source']
        if (tid == ""): tid = j["data"]["archive"]['tid']
        self.preUpload(parts)
        self.editUpload(aid, title, tid, tag, desc, source, cover, no_reprint)

    def editUpload(self,
                   aid,
                   title,
                   tid,
                   tag,
                   desc,
                   source='',
                   cover='',
                   no_reprint=1,
                   ):
        """
        :param aid: just aid
        :type aid: int
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
        copyright = 2 if source else 1
        r = self.session.post('https://member.bilibili.com/x/vu/web/edit?csrf=' + self.csrf,
                              json={
                                  "aid": aid,
                                  "copyright": copyright,
                                  "source": source,
                                  "title": title,
                                  "tid": tid,
                                  "tag": ','.join(tag),
                                  "no_reprint": no_reprint,
                                  "desc": desc,
                                  "cover": cover,
                                  "mission_id": 0,
                                  "order_id": 0,
                                  "videos": self.videos}
                              )
        print(r.text)

    def addChannel(self, name, intro=''):
        """

        :param name: channel's name
        :type name: str
        :param intro: channel's introduction
        :type intro: str
        """
        r = self.session.post(
            url='https://space.bilibili.com/ajax/channel/addChannel',
            data={
                'name': name,
                'intro': intro,
                'aids': '',
                'csrf': self.csrf,
            },
            # name=123&intro=123&aids=&csrf=565d7ed17cef2cc8ad054210c4e64324&_=1497077610768

        )
        # return
        # {"status":true,"data":{"cid":"15812"}}
        print(r.json())

    def channel_addVideo(self, cid, aids):
        """

        :param cid: channel's id
        :type cid: int
        :param aids: videos' id
        :type aids: list<int>
        """

        r = self.session.post(
            url='https://space.bilibili.com/ajax/channel/addVideo',
            data={
                'aids': '%2C'.join(aids),
                'cid': cid,
                'csrf': self.csrf
            }
            # aids=9953555%2C9872953&cid=15814&csrf=565d7ed17cef2cc8ad054210c4e64324&_=1497079332679
        )
        print(r.json())

    def cover_up(self, img):
        """

        :param img: img path or stream
        :type img: str or BufferedReader
        :return: img URL
        """

        if isinstance(img, str):
            f = open(img, 'rb')
        else:
            f = img
        r = self.session.post(
            url='https://member.bilibili.com/x/vu/web/cover/up',
            data={
                'cover': b'data:image/jpeg;base64,' + (base64.b64encode(f.read())),
                'csrf': self.csrf,
            }
        )
        # print(r.text)
        # {"code":0,"data":{"url":"http://i0.hdslb.com/bfs/archive/67db4a6eae398c309244e74f6e85ae8d813bd7c9.jpg"},"message":"","ttl":1}
        return r.json()['data']['url']
