#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gdk, Gtk, GLib
from cairo import Region, RectangleInt
from Xlib.ext.xtest import fake_input
from Xlib import display, X
import threading

s = Gdk.Screen.get_default()
d = display.Display()
xd = Gdk.Display.get_default()
geom = xd.get_monitor(0).get_geometry()
x, y = geom.width // 2, geom.height // 2
pointer = xd.get_default_seat().get_pointer()
cur = None
useCursor = False

def move_pointer_to(dx, dy):
    GLib.idle_add(lambda: _move_pointer_to(dx, dy))

def _move_pointer_to(dx, dy):
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
    GLib.idle_add(lambda: _click_button(btn))

def _click_button(btn):
    fake_input(d, X.ButtonPress, btn, X.CurrentTime, X.NONE, x, 5)
    d.sync()

def release_button(btn):
    GLib.idle_add(lambda: _release_button(btn))

def _release_button(btn):
    fake_input(d, X.ButtonRelease, btn, X.CurrentTime)
    d.sync()

def start():
    if cur is not None and useCursor:
        GLib.idle_add(cur.show_all)

def stop():
    if cur is not None and useCursor:
        GLib.idle_add(cur.hide)

def cursor():
    global cur
    win = Gtk.Window(type=Gtk.WindowType.POPUP)
    im = Gtk.Image.new_from_file('cursor.png')
    Gtk.Widget.set_opacity(win, 0)
    win.set_visual(win.get_screen().get_rgba_visual())
    win.add(im)
    Gtk.Widget.set_opacity(win, 1)
    win.set_decorated(False)
    win.set_modal(True)
    win.set_keep_above(True)
    win.set_app_paintable(True)
    win.set_skip_pager_hint(True)
    win.input_shape_combine_region(Region(RectangleInt(0,0,0,0)))

    win.move(x, y)
    cur = win
    return cur

def enableCursor(isEnabled):
    global useCursor
    useCursor = isEnabled

def main():
    cursor()
    start()
    stop()
    thread = threading.Thread(target=main_thread)
    thread.start()
    Gtk.main()

def main_thread():
    while True:
        try:
            inp = input()
        except EOFError:
            break
        cmd, *args = inp.split(' ')
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
        elif cmd == 'cursor':
            enableCursor(args[0] == 'on')
        elif cmd == 'quit':
            break
    Gtk.main_quit()

if __name__ == '__main__':
    main()
