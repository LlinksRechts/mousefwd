#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gdk, Gtk, GObject
from cairo import Region, RectangleInt
from Xlib.ext.xtest import fake_input
from Xlib import display, X
import threading

Gdk.threads_init()

s = Gdk.Screen.get_default()
x, y = s.get_width() // 2, s.get_height() // 2
d = display.Display()
xd = Gdk.Display.get_default()
pointer = xd.get_default_seat().get_pointer()
cur = None

def move_pointer_to(dx, dy):
    global x, y
    x += dx
    y += dy
    pointer.warp(s, x, y)
    ppos = pointer.get_position()
    # -> flush
    xd.sync()
    x, y = ppos.x, ppos.y
    if cur is not None:
        cur.move(x+1, y+1)

def click_button(btn):
    fake_input(d, X.ButtonPress, btn, X.CurrentTime, X.NONE, x, 5)
    d.sync()

def release_button(btn):
    fake_input(d, X.ButtonRelease, btn, X.CurrentTime)
    d.sync()

def start():
    if cur is not None:
        cur.show_all()

def stop():
    if cur is not None:
        cur.hide()

def cursor():
    global cur
    win = Gtk.Window(type=Gtk.WindowType.POPUP)
    im = Gtk.Image.new_from_file('cursor.png')
    win.add(im)
    win.set_decorated(False)
    win.set_modal(True)
    win.set_keep_above(True)
    win.set_app_paintable(True)
    win.set_skip_pager_hint(True)
    win.input_shape_combine_region(Region(RectangleInt(0,0,0,0)))

    win.move(x, y)
    cur = win
    return cur

def main():
    # TODO cursor flag
    cursor()
    start()
    stop()
    thread = threading.Thread(target=main_thread)
    thread.start()
    Gtk.main()

def main_thread():
    # fix for 'Fatal IO error 2 (No such file or directory) on X server :0.'
    # start()
    # stop()
    while True:
        try:
            inp = input()
        except EOFError:
            break
        cmd, *args = inp.split(' ')
        Gdk.threads_enter()
        if cmd == 'move':
            dx, dy = [int(x) for x in args]
            move_pointer_to(dx, dy)
        elif cmd == 'press':
            click_button(int(args[0]))
        elif cmd == 'release':
            release_button(int(args[0]))
        elif cmd == 'start':
            start()
        elif cmd == 'stop':
            stop()
        Gdk.threads_leave()
    Gtk.main_quit()

if __name__ == '__main__':
    main()
