import sys
import socket
import threading
from time import sleep

incoming_call_port = 8000
server_port = 8001
server_ip = '10.50.18.161'
incoming_call_thread, outgoing_call_thread = None, None
expecting_call_back_from = None
run = True
recv_sock = None


def msg_routine():
    pass


def read_sock(conn):
    data = b''
    while run:
        block = conn.recv(10)
        data += block
        if block.find(b'\n') >= 0:
            break
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
    global expecting_call_back_from, outgoing_call_thread, run, recv_sock
    recv_sock = socket.socket()
    recv_sock.bind(('', incoming_call_port))
    recv_sock.listen(1)
    conn = None
    try:
        while run:
            conn, address = recv_sock.accept()
            if not run:
                break
            username = unr(address[0])
            if expecting_call_back_from is not None and expecting_call_back_from != username:
                conn.close()
                continue
            if expecting_call_back_from is None:
                print(username + "is calling u")
                if input('Accept? (y/n): ') == 'y':
                    outgoing_call_thread = threading.Thread(target=call, kwargs={'username': username})
                    outgoing_call_thread.start()
                else:
                    conn.close()
                    continue
            for _ in range(10):
                print(read_sock(conn))
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
        for _ in range(10):
            call_sock.send(b'Hello\n')
            sleep(.5)
        call_sock.close()
    except:
        pass
    expecting_call_back_from = None


def main(username, password):
    global run
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
    except KeyboardInterrupt:
        pass
    call_thread.join()
    print()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python3 client.py username password')
    else:
        main(sys.argv[1], sys.argv[2])
