#!/usr/bin/env python3
import signal
import argparse
import subprocess

from sender import Sender

parser = argparse.ArgumentParser(description='Forward mouse inputs to another host over ssh')
parser.add_argument('host', help='host to connect to')
parser.add_argument('-m', help='display mouse on receiver', action='store_const', const=True)
parser.add_argument('-d', '--display', help='X display on the receiver (default :0)', default=':0')
parser.add_argument('-r', '--receiver-dir', help='temporary directory on the receiver to store scripts (default /tmp)', default='/tmp')

args = parser.parse_args()

sender = None
connection = None

def stopAll(_, __):
    sender.exit()
    connection.stdin.close()

if subprocess.run(['scp', 'receiver.py', 'cursor.png', f'{args.host}:{args.receiver_dir}/']).returncode == 0:
    connection = subprocess.Popen(['ssh', args.host, f'cd {args.receiver_dir}; DISPLAY={args.display} python3 ./receiver.py'], stdin=subprocess.PIPE)
    signal.signal(signal.SIGINT, stopAll) # TODO this catches sigint via kill -2, but not ctrl+c?
    signal.signal(signal.SIGTERM, stopAll)
    sender = Sender(connection.stdin)
    sender.run()
else:
    print(f'Error writing client software to receiver. Make sure you have access to the {args.receiver_dir} directory on the client {args.receiver_dir}')
