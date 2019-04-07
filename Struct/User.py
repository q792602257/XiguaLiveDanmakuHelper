class User:
    ID = 0
    name = ""
    brand = ""
    level = 0
    type = 0
    block = False
    mute = False

    def __init__(self, json=None):
        if json:
            self.parse(json)

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
        elif "room" in json and json["room"] is not None:
            if "user_info" in json["room"] and json["room"]["user_info"] is not None:
                self.ID = json["room"]['user_info']['user_id']
                self.name = json["room"]['user_info']['name']
        elif "anchor" in json and json["anchor"] is not None:
            if "user_info" in json["anchor"] and json["anchor"]['user_info'] is not None:
                self.ID = json["anchor"]['user_info']['user_id']
                self.name = json["anchor"]['user_info']['name']
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
