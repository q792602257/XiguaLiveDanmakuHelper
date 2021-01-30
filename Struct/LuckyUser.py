from .User import User

class LuckyUser:

    user = None
    count = 0

    def __init__(self, json=None):
        if json:
            self.parse(json)

    def parse(self, json):
        self.user = User()
        self.user.ID = json['user_id']
        self.user.name = json['user_name']
        self.count = int(json["grant_count"])

    def __str__(self):
        return "用户 {} 获得了 {} 个".format(self.user,self.count)
