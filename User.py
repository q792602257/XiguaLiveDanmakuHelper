class User:
    ID:     int = 0
    name:   str = ""
    brand:  str = ""
    level:  int = 0
    type:   int = 0

    def __init__(self, json=None):
        if json:
            self.parse(json)

    def parse(self, json):
        if "Msg" in json:
            if "user" in json["Msg"]:
                self.ID = json["Msg"]['user']['user_id']
                self.name = json["Msg"]['user']['name']
            if "discipulus_info" in json["Msg"]:
                self.level = json["Msg"]["discipulus_info"]["level"]
                self.brand = json["Msg"]["discipulus_info"]["discipulus_group_title"]
        elif "data" in json:
            if "anchorInfo" in json["data"]:
                self.ID = json["data"]['anchorInfo']['id']
                self.name = json["data"]['anchorInfo']['name']
        if self.type is None:
            self.type = 0

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
            return "<{}{}>{}".format(self.brand,self.level,self.name)

    def __unicode__(self):
        return self.__str__()

