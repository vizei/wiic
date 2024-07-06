import pygame
import sys
import wiiuse
import mouse as pyautogui

pygame.init()

scrsize = (800, 600)
white = (255, 255, 255)
black = (0, 0, 0)
nmotes = 1
wiimotes = []
screen = pygame.display.set_mode(scrsize)
pygame.display.set_caption("wiimote ir")

following_length = 1000
following = []
smoothpos = (scrsize[0] // 2, scrsize[1] // 2)


def smooth_position(currentpos, smoothing_fac):
    global smoothpos
    scrnwidth, scrnheight = pyautogui.size()
    winwidth, winheight = scrsize
    mapx = int(currentpos[0] / winwidth * scrnwidth)
    mapy = int(currentpos[1] / winheight * scrnheight)

    smoothpos = (
        int(
            smoothpos[0] * (1 - smoothing_fac) + mapx * smoothing_fac
        ),
        int(
            smoothpos[1] * (1 - smoothing_fac) + mapy * smoothing_fac
        ),
    )

    smoothpos = (
        max(0, min(scrnwidth, smoothpos[0])),
        max(0, min(scrnheight, smoothpos[1])),
    )


def handle_event(wmp, smoothing_fac):
    global following, smoothpos
    wm = wmp[0]
    screen.fill(black)
    radius = 10

    if wm.ir.dot and wm.ir.x and wm.ir.y:
        xcircle = max(radius, min(scrsize[0] - radius, wm.ir.x))
        ycircle = max(radius, min(scrsize[1] - radius, scrsize[1] - wm.ir.y))
        smooth_position((xcircle, ycircle), smoothing_fac)

    for pos, alpha in following:
        if alpha > 0:
            pygame.draw.circle(screen, white, pos, radius, max(0, int(alpha)))

    following.insert(0, ((smoothpos[0], smoothpos[1]), 255))
    if len(following) > following_length:
        following.pop()

    pygame.draw.circle(screen, white, smoothpos, radius)
    pygame.display.flip()

    pyautogui.drag(
        smoothpos[0], smoothpos[1]
    )

    if wiiuse.is_just_pressed(wm, wiiuse.button["A"]):
        following.clear()

    for i in range(len(following)):
        following[i] = ((following[i][0][0], following[i][0][1]), max(0, following[i][1] - 5))


def main(smoothing_fac):
    global wiimotes
    print("finding Wiimote")
    wiimotes = wiiuse.init(nmotes)
    found = wiiuse.find(wiimotes, nmotes, 5)
    if not found:
        print("wiimote not found")
        sys.exit(1)
    print("wiimote found:", found)
    connected = wiiuse.connect(wiimotes, nmotes)
    if connected:
        print("connected to %i wiimote" % connected)
    else:
        print("failed to connect to any wiimote")
        sys.exit(1)

    for i in range(nmotes):
        wiiuse.set_ir(wiimotes[i], 1)
        scrnwidth, scrnheight = pyautogui.size()
        wiiuse.set_ir_vres(wiimotes[i], scrnwidth, scrnheight)

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            r = wiiuse.poll(wiimotes, nmotes)
            if r != 0:
                handle_event(wiimotes[0], smoothing_fac)

    except KeyboardInterrupt:
        pass

    for i in range(nmotes):
        wiiuse.disconnect(wiimotes[i])



if __name__ == "__main__":
    smoothing_fac = 0.08
    main(smoothing_fac)
