#!/usr/bin/env python3
import signal
import argparse
import subprocess

from sender import Sender

parser = argparse.ArgumentParser(description='Forward mouse inputs to another host over ssh')
parser.add_argument('host', help='host to connect to')
parser.add_argument('-c', '--cursor', help='display cursor on receiver', action='store_const', const=True)
parser.add_argument('-d', '--display', help='X display on the receiver (default :0)', default=':0')
parser.add_argument('-r', '--receiver-dir', help='temporary directory on the receiver to store scripts (default /tmp)', default='/tmp')
parser.add_argument('-k', '--hotkey', help='hotkey to enable mouse forwarding (default C-grave)', default='C-grave')
# TODO arg for sensitivity

args = parser.parse_args()

sender = None
connection = None

def stopAll(_, __):
    sender.exit()
    connection.stdin.close()

def parseHotkey(hotkeyString):
    split = hotkeyString.split('-')
    return split[-1], split[:-1]

if subprocess.run(['scp', 'receiver.py', 'cursor.png', f'{args.host}:{args.receiver_dir}/']).returncode == 0:
    connection = subprocess.Popen(['ssh', args.host, f'cd {args.receiver_dir}; DISPLAY={args.display} python3 ./receiver.py'], stdin=subprocess.PIPE)
    signal.signal(signal.SIGINT, stopAll)
    signal.signal(signal.SIGTERM, stopAll)
    sender = Sender(connection.stdin, args.cursor, *parseHotkey(args.hotkey))
    sender.run()
else:
    print(f'Error writing client software to receiver. Make sure you have access to the {args.receiver_dir} directory on the client {args.receiver_dir}')
