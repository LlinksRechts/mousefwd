#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gdk, Gtk, GLib
from Xlib import display, X
from Xlib.keysymdef import latin1
import threading
import signal
import sys

def evt(_, __, handle=None):
    global pos, x, y, rel, dx, dy, count, running
    handle = handle or rt.display
    ev = handle.next_event()
    if rel and ev.type != X.KeyPress:
        print("stop")
        running = False
        d.ungrab_pointer(X.CurrentTime)
        rel = False
        sys.stdout.flush()
        return True
    if ev.type == X.MotionNotify:
        dx += (ev.root_x - x) // 1
        dy += (ev.root_y - y) // 1
        if ev.root_x != x or ev.root_y != y:
            pointer.warp(screen, x, y)
            # -> flush
            xd.sync()
        # if dx != 0 or dy != 0:
        #     print("move", dx, dy)
        #     if ev.root_x != x or ev.root_y != y:
        #         pointer.warp(screen, x, y)
        #         # -> flush
        #         xd.sync()
        #     dx, dy = 0, 0
    elif ev.type == X.ButtonPress:
        print("press", ev.detail)
    elif ev.type == X.ButtonRelease:
        print("release", ev.detail)
    elif ev.type == X.KeyPress:
        if rel:
            rel = False
            return True
        print("start")
        running = True
        pos = pointer.get_position()
        x, y = pos.x, pos.y
        rt.grab_pointer(False, X.ButtonPressMask | X.ButtonReleaseMask | X.PointerMotionMask, X.GrabModeAsync, X.GrabModeAsync, 0, 0, X.CurrentTime)
    elif ev.type == X.KeyRelease:
        rel = True
        # print("stop")
        # d.ungrab_pointer(X.CurrentTime)
    sys.stdout.flush()
    return True

class MoveThread(threading.Thread):
    def __init__(self, event=threading.Event()):
        threading.Thread.__init__(self)
        self.stopped = event

    def run(self):
        global dx, dy, running
        while not self.stopped.wait(0.01):
            if (dx != 0 or dy != 0) and running:
                print("move", dx, dy)
                sys.stdout.flush()
                dx, dy = 0, 0

xd = Gdk.Display.get_default()
screen = Gdk.Screen.get_default()
pointer = xd.get_default_seat().get_pointer()
rel, running = False, False
dx, dy = 0, 0
count = 0

d = display.Display()
rt = d.screen().root

def main():
    rt.change_attributes(event_mask=X.KeyPressMask)
    rt.grab_key(d.keysym_to_keycode(getattr(latin1, 'XK_grave')), X.ControlMask, 1, X.GrabModeAsync, X.GrabModeAsync)
    rt.grab_key(d.keysym_to_keycode(getattr(latin1, 'XK_grave')), X.ControlMask | X.Mod2Mask, 1, X.GrabModeAsync, X.GrabModeAsync)

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)

    mt = MoveThread()
    mt.start()

    while True:
        evt(0, 0)

if __name__ == '__main__':
    main()
