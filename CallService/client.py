import sys
import socket
import threading
from time import sleep

import pyaudio

incoming_call_port = 8000
server_port = 8001
server_ip = '10.50.18.161'
incoming_call_thread, outgoing_call_thread = None, None
expecting_call_back_from = None
run = True
recv_sock = None
ans = None

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1000

audio = pyaudio.PyAudio()

mic = audio.open(format=FORMAT, channels=CHANNELS,
                 rate=RATE, input=True,
                 frames_per_buffer=CHUNK)
speaker = audio.open(format=FORMAT, channels=CHANNELS,
                     rate=RATE, output=True,
                     frames_per_buffer=CHUNK)
buffer = b''


def read_sock(conn):
    global buffer
    data = buffer
    buffer = b''
    while run:
        block = conn.recv(10)
        end = block.find(b'\n')
        if end >= 0:
            buffer += block[end + 1:]
            data += block[:end + 1]
            break
        data += block
    data = data.decode()
    return data.strip()


def auth(sock, username, password):
    sock.send(('auth:' + username + ':' + password + '\n').encode('ascii'))
    data = read_sock(sock)
    return data == 'pass'


def unr(username):
    sock = socket.socket()
    sock.connect((server_ip, server_port))
    sock.send(('unr:' + username + '\n').encode('ascii'))
    data = read_sock(sock)
    sock.close()
    ip = data.split(':')[2]
    if ip == '-1':
        return None
    return ip


def ipr(ip):
    sock = socket.socket()
    sock.connect((server_ip, server_port))
    sock.send(('ipr:' + ip + '\n').encode('ascii'))
    data = read_sock(sock)
    sock.close()
    username = data.split(':')[2]
    if username == '-1':
        return None
    return username


def listen_call():
    global expecting_call_back_from, outgoing_call_thread, run, recv_sock, ans
    recv_sock = socket.socket()
    recv_sock.bind(('', incoming_call_port))
    recv_sock.listen(1)
    conn = None
    try:
        while run:
            conn, address = recv_sock.accept()
            if not run:
                break
            username = ipr(address[0])

            if expecting_call_back_from is not None and expecting_call_back_from != username:
                conn.close()
                continue
            if expecting_call_back_from is None:
                print(username + ' is calling you! Accept?(y/n): ')
                ans = None
                while run and ans is None:
                    sleep(.1)
                if ans == 'y':
                    outgoing_call_thread = threading.Thread(target=call, kwargs={'username': username})
                    outgoing_call_thread.start()
                else:
                    conn.close()
                    continue
            for _ in range(1000):
                frame = conn.recv(CHUNK)
                speaker.write(frame, len(frame))
            conn.close()
    except KeyboardInterrupt:
        if conn is not None:
            conn.close()
        recv_sock.close()
        raise KeyboardInterrupt


def call(username):
    global expecting_call_back_from
    ip = unr(username)
    if ip is None:
        return
    expecting_call_back_from = username
    try:
        call_sock = socket.socket()
        call_sock.connect((ip, incoming_call_port))
        for _ in range(1000):
            call_sock.send(mic.read(CHUNK))
        call_sock.close()
    except:
        pass
    expecting_call_back_from = None


def main(username, password):
    global run, ans
    msg_sock = socket.socket()
    msg_sock.connect((server_ip, server_port))
    if auth(msg_sock, username, password):
        print('Auth Success')
    else:
        print('Auth Failure')
    msg_sock.close()
    call_thread = threading.Thread(target=listen_call)
    call_thread.start()
    try:
        while True:
            x = input("# ")
            y = x.split()
            if y[0] == 'exit':
                run = False
                recv_sock.close()
                break
            elif y[0] == 'call':
                outgoing_call_thread = threading.Thread(target=call, kwargs={'username': y[1]})
                outgoing_call_thread.start()
            elif y[0] == 'ipr':
                print(ipr(y[1]))
            elif y[0] == 'unr':
                print(unr(y[1]))
            elif y[0] == 'y' or y[0] == 'n':
                ans = y[0]
    except KeyboardInterrupt:
        pass
    call_thread.join()
    print()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python3 client.py username password')
    else:
        main(sys.argv[1], sys.argv[2])
