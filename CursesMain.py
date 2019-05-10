import curses

from Struct.Chat import Chat
from Struct.Gift import Gift
from Struct.MemberMsg import MemberMsg
from Struct.User import User
from api import XiGuaLiveApi


class Api(XiGuaLiveApi):
    danmakuList = []
    def onAd(self, i):
        pass
    def onChat(self, chat: Chat):
        self.danmakuList.append(str(chat))
    def onLike(self, user: User):
        pass
    def onEnter(self, msg: MemberMsg):
        pass
    def onJoin(self, user: User):
        self.danmakuList.append(str(user))
    def onSubscribe(self, user: User):
        self.danmakuList.append(str(user))
    def onPresent(self, gift: Gift):
        pass
    def onPresentEnd(self, gift: Gift):
        self.danmakuList.append(str(gift))


api = Api()
widths = [
    (126, 1), (159, 0), (687, 1), (710, 0), (711, 1),
    (727, 0), (733, 1), (879, 0), (1154, 1), (1161, 0),
    (4347, 1), (4447, 2), (7467, 1), (7521, 0), (8369, 1),
    (8426, 0), (9000, 1), (9002, 2), (11021, 1), (12350, 2),
    (12351, 1), (12438, 2), (12442, 0), (19893, 2), (19967, 1),
    (55203, 2), (63743, 1), (64106, 2), (65039, 1), (65059, 0),
    (65131, 2), (65279, 1), (65376, 2), (65500, 1), (65510, 2),
    (120831, 1), (262141, 2), (1114109, 1),
]


def get_width(o):
    global widths
    if o == 0xe or o == 0xf:
        return 0
    for num, wid in widths:
        if o <= num:
            return wid
    return 1


def c_print(handle, y, x, string, style=curses.A_NORMAL):
    if type(string) != str:
        string = str(string)
    for _i in string:
        _w = get_width(ord(_i))
        if(_w>1):
            handle.addch(y, x+1, " ", style)
        if _i != " " or style!=curses.A_NORMAL:
            handle.addch(y, x, ord(_i), style)
        else:
            handle.addch(y, x, 0, style)
        x += _w




def render(screen):
    screen.erase()
    screen.box()
    screen.hline(2, 1, curses.ACS_HLINE, 77)
    c_print(screen, 1, 2, " "*45 + " 西瓜弹幕助手 -- by JerryYan  ", curses.A_STANDOUT)
    _style = curses.A_DIM
    if api.isLive:
        _style = curses.A_BOLD | curses.A_BLINK | curses.A_ITALIC
    c_print(screen, 1, 3, api.roomLiver, _style)
    _y = 3
    api.getDanmaku()
    for i in api.danmakuList[-10:]:
        c_print(screen, _y, 2, i)
        _y += 1
    screen.move(0,0)
    screen.refresh()

def main(stdscr):
    global screen
    screen = stdscr.subwin(23, 79, 0, 0)
    screen.timeout(2000)
    render(screen)
    while True:
        c = screen.getch()
        if c == ord("q"):
            break
        render(screen)


stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(1)
curses.wrapper(main)
stdscr.keypad(0)
curses.echo()
curses.nocbreak()
curses.endwin()

