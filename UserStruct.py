class UserStruct:
    ID = 0
    name = ""
    brand= ""
    level= 0
    type = 0

    def __init__(self, json=None):
        if json:
            self.parse(json)

    def parse(self, json):
        if "Msg" in json:
            if "user" in json["Msg"]:
                self.ID = json["Msg"]['user']['user_id']
                self.name = json["Msg"]['user']['name']
                self.type = json["Msg"]['user']['user_type']
            if "discipulus_info" in json["Msg"]:
                self.level = json["Msg"]["discipulus_info"]["level"]
                self.brand = json["Msg"]["discipulus_info"]["discipulus_group_title"]
        if self.type is None:
            self.type = 0

    def __str__(self):
        if self.level == 0:
            if self.type != 0:
                return "[]{}".format(self.name)
            return "{}".format(self.name)
        else:
            if self.type != 0:
                return "[{}{}]{}".format(self.brand, self.level, self.name)
            return "<{}{}>{}".format(self.brand,self.level,self.name)

    def __unicode__(self):
        return self.__str__()

