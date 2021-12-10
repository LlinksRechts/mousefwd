#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gdk, Gtk, GLib
from Xlib import display, X
from Xlib.keysymdef import latin1
from functools import reduce
import threading
import sys


keyModifiers = {
    'C': X.ControlMask, # Control
    'S': X.ShiftMask, # Shift
    'A': X.Mod1Mask, # Alt
    'M': X.Mod4Mask, # Meta
}

class MoveThread(threading.Thread):
    def __init__(self, action, event=threading.Event()):
        self.action = action
        threading.Thread.__init__(self)
        self.stopped = event

    def run(self):
        while not self.stopped.wait(0.01):
            self.action()

class Sender:
    def __init__(self, connection=sys.stdout, cursor=False, hotkey='grave', modifiers=['C'], sensitivity=1):
        self.connection = connection
        self.cursor = cursor
        self.hotkey = hotkey
        self.modifiers = modifiers
        self.sensitivity = sensitivity

        self.xd = Gdk.Display.get_default()
        self.screen = Gdk.Screen.get_default()
        self.pointer = self.xd.get_default_seat().get_pointer()
        self.rel, self.running = False, False
        self.dx, self.dy = 0, 0
        self.leftoverX, self.leftoverY = 0.0, 0.0

        self.d = display.Display()
        self.rt = self.d.screen().root

        self.active = True
        self.stopped = threading.Event()
        self.mouseLock = threading.Lock()

    def printconn(self, *args):
        self.connection.write(' '.join((str(x) for x in args)).encode('UTF-8'))
        self.connection.write(b'\n')

    def evt(self):
        while not self.rt.display.pending_events():
            if self.stopped.wait(0.001): # TODO find a way not to busy wait
                return False
        ev = self.rt.display.next_event()
        if self.rel and ev.type != X.KeyPress:
            self.x = self.pos.x
            self.y = self.pos.y
            self.pointer.warp(self.screen, self.x, self.y)
            self.xd.sync()
            self.printconn("stop")
            self.running = False
            self.d.ungrab_pointer(X.CurrentTime)
            self.rel = False
            self.connection.flush()
            return True
        if ev.type == X.MotionNotify:
            self.mouseLock.acquire()
            self.dx += (ev.root_x - self.x) // 1
            self.dy += (ev.root_y - self.y) // 1
            if ev.root_x != self.x or ev.root_y != self.y:
                self.pointer.warp(self.screen, self.x, self.y)
                # -> flush
                self.xd.sync()
            self.mouseLock.release()
        elif ev.type == X.ButtonPress:
            self.printconn("press", ev.detail)
        elif ev.type == X.ButtonRelease:
            self.printconn("release", ev.detail)
        elif ev.type == X.KeyPress:
            if self.rel:
                self.rel = False
                return True
            self.printconn("start")
            self.running = True
            self.pos = self.pointer.get_position()
            self.x, self.y = self.screen.width() // 2, self.screen.height() // 2
            self.pointer.warp(self.screen, self.x, self.y)
            self.xd.sync()
            self.rt.grab_pointer(False, X.ButtonPressMask | X.ButtonReleaseMask | X.PointerMotionMask, X.GrabModeAsync, X.GrabModeAsync, 0, 0, X.CurrentTime)
        elif ev.type == X.KeyRelease:
            self.rel = True
        self.connection.flush()
        return True

    def sendMove(self):
        if (self.dx != 0 or self.dy != 0) and self.running:
            self.mouseLock.acquire()
            self.dx *= self.sensitivity
            self.dy *= self.sensitivity
            self.dx += self.leftoverX
            self.dy += self.leftoverY
            moveX = int(self.dx)
            moveY = int(self.dy)
            self.printconn("move", moveX, moveY)
            self.connection.flush()
            self.leftoverX, self.leftoverY = self.dx - moveX, self.dy - moveY
            self.dx, self.dy = 0, 0
            self.mouseLock.release()

    def run(self):
        modifiers = [keyModifiers.get(mod, None) for mod in self.modifiers]
        if None in modifiers:
            print(f"Unknown modifier {self.modifiers[modifiers.index(None)]}")
            self.exit()
            return
        if getattr(latin1, f'XK_{self.hotkey}', None) is None:
            print(f"Unknown hotkey {self.hotkey}")
            self.exit()
            return
        hotkey = self.d.keysym_to_keycode(getattr(latin1, f'XK_{self.hotkey}'))
        xModifiers = reduce(lambda a, b: a | b, modifiers)
        self.rt.change_attributes(event_mask=X.KeyPressMask)
        self.rt.grab_key(hotkey, xModifiers, 1, X.GrabModeAsync, X.GrabModeAsync)
        self.rt.grab_key(hotkey, xModifiers | X.Mod2Mask, 1, X.GrabModeAsync, X.GrabModeAsync)

        if self.cursor:
            self.printconn("cursor on")

        self.mt = MoveThread(self.sendMove, self.stopped)
        self.mt.start()

        while self.active:
            self.evt()

    def exit(self):
        self.printconn("quit")
        self.active = False
        self.stopped.set()

if __name__ == '__main__':
    Sender().run()
