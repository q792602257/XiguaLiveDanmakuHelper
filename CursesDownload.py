import curses
import Common


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
        handle.addch(y, x, ord(_i), style)
        x += _w


def render(screen):
    _style = curses.A_DIM
    if Common.api.isLive:
        _style = curses.A_BOLD | curses.A_BLINK | curses.A_ITALIC | curses.A_UNDERLINE
    c_print(screen, 1, 3, Common.api.roomLiver, _style)
    screen.refresh()

def main(stdscr):
    global screen
    screen = stdscr.subwin(23, 79, 0, 0)
    screen.timeout(2000)
    screen.box()
    screen.hline(2, 1, curses.ACS_HLINE, 77)
    c_print(screen, 1, 2, " "*45 + " 西瓜录播助手 -- by JerryYan  ", curses.A_STANDOUT)
    render(screen)
    while True:
        c = stdscr.getch()
        if c == ord("q"):
            break
        elif c == ord("f"):
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

