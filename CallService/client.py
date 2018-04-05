import sys
import socket

incoming_call_port = 8000
server_port = 8001
server_ip = '127.0.0.1'


def msg_routine():
    pass


def read_sock(conn):
    data = b''
    while True:
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

def unr(address):
    sock = socket.socket()
    sock.connect((server_ip, server_port))
    sock.send(('unr:' + address[0]+'\n').encode('ascii'))
    data = read_sock(sock)
    usrname=data.split(':')[1]
    return usrname


def listen_call():
    recv_sock=socket.socket()
    recv_sock.bind(('', incoming_call_port))
    recv_sock.listen(5)
    conn, address = recv_sock.accept()
    usrname=unr(address)
    print(usrname+"is calling u")

def main(username, password):
    msg_sock = socket.socket()
    msg_sock.connect((server_ip, server_port))
    if auth(msg_sock, username, password):
        print('Auth Success')
    else:
        print('Auth Failure')
    msg_sock.close()
    listen_call()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python3 client.py username password')
    else:
        main(sys.argv[1], sys.argv[2])
