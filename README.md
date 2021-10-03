# Mousefwd
Mousefwd forwards mouse inputs, including movement and clicks, to another host
over SSH while a hotkey is held. Currently, this is only tested on systems
running the X display manager.

## Installation
Mousefwd needs gobject-introspection, cairo, and xlib on both the sender and
the receiver. These can usually be installed via the packages `python3-gi`,
`python3-gi-cairo`, and `python3-xlib` in your package manager.

## Usage
The application is passed an SSH host to forward inputs to, for example
`user@example.com`. Other parameters can be configured via command line flags:

```
usage: mousefwd.py [-h] [-c] [-d DISPLAY] [-r RECEIVER_DIR] [-k HOTKEY]
                   [-s SENSITIVITY]
                   host

Forward mouse inputs to another host over ssh

positional arguments:
  host                  host to connect to

optional arguments:
  -h, --help            show this help message and exit
  -c, --cursor          display cursor on receiver
  -d DISPLAY, --display DISPLAY
                        X display on the receiver (default :0)
  -r RECEIVER_DIR, --receiver-dir RECEIVER_DIR
                        temporary directory on the receiver to store scripts
                        (default /tmp)
  -k HOTKEY, --hotkey HOTKEY
                        hotkey to enable mouse forwarding (default C-grave)
  -s SENSITIVITY, --sensitivity SENSITIVITY
                        mouse sensitivity (default 1.0)
```

### Cursor
If the `cursor` flag is enabled, a cursor is rendered on the receiver as long
as the hotkey is held. This can be useful, e.g., if the system uses a touch
screen where the mouse cursor is normally disabled.

For the cursor to be rendered correctly, a compositing manager like `xcompmgr`
needs to be running on the receiving system. Otherwise, transparency will not
be rendered correctly and a black box will appear around the cursor.

The graphics of the cursor can be changed by replacing the `cursor.png` file
in the root of this project.
