from XiguaUser_pb2 import User as UserPb


class User:
    def __init__(self, json=None):
        self.ID = 0
        self.name = ""
        self.brand = ""
        self.level = 0
        self.type = 0
        self.block = False
        self.mute = False
        if json:
            if type(json) == bytes:
                self.parsePb(json)
            elif type(json) == UserPb:
                self.parseUserPb(json)
            else:
                self.parse(json)

    def parseUserPb(self, _user):
        self.ID = _user.id
        self.name = _user.nickname
        self.brand = _user.fansClub.fansClub.title
        self.level = _user.fansClub.fansClub.level

    def parsePb(self, raw):
        _user = UserPb()
        _user.ParseFromString(raw)
        self.parseUserPb(_user)

    def parse(self, json):
        if "extra" in json:
            if "user" in json["extra"] and json["extra"]["user"] is not None:
                self.ID = json["extra"]['user']['user_id']
                self.name = json["extra"]['user']['name']
            if "im_discipulus_info" in json["extra"] and json["extra"]["im_discipulus_info"] is not None:
                self.level = json["extra"]["im_discipulus_info"]["level"]
                self.brand = json["extra"]["im_discipulus_info"]["discipulus_group_title"]
            if "user_room_auth_status" in json["extra"] and json["extra"]["user_room_auth_status"] is not None:
                self.type = json["extra"]["user_room_auth_status"]["user_type"]
                self.block = json["extra"]["user_room_auth_status"]["is_block"]
                self.mute = json["extra"]["user_room_auth_status"]["is_silence"]
        if "user_info" in json and json["user_info"] is not None:
                self.ID = json['user_info']['user_id']
                self.name = json['user_info']['name']
        if "anchor" in json and json["anchor"] is not None:
            if "user_info" in json["anchor"] and json["anchor"]['user_info'] is not None:
                self.ID = json["anchor"]['user_info']['user_id']
                self.name = json["anchor"]['user_info']['name']
        if "user_id" in json:
            self.ID = json["user_id"]
        if "user_name" in json:
            self.name = json["user_name"]
        if self.type is None:
            self.type = 0
        if isinstance(self.level, str):
            self.level = int(self.level)

    def __str__(self):
        if self.level == 0:
            if self.type == 1:
                return "[房管]{}".format(self.name)
            elif self.type == 3:
                return "[主播]{}".format(self.name)
            else:
                return "{}".format(self.name)
        else:
            if self.type != 0:
                return "[{}{}]{}".format(self.brand, self.level, self.name)
            return "<{}{}>{}".format(self.brand, self.level, self.name)

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return "西瓜用户【{}(ID:{})】".format(self.name, self.ID)
