import socket

username_password_db = {'srinag': 'password', 'shreyas': 'password', 'skitty': 'password'}
username_resolver = {}
ip_resolver = {}
username_conn = {}
server_port = 8001


def auth(username, password):
    return username in username_password_db and username_password_db[username] == password


def read_sock(conn):
    data = b''
    while True:
        block = conn.recv(10)
        data += block
        if block.find(b'\n') >= 0:
            break
    data = data.decode()
    return data.strip()


def main():
    sock = socket.socket()
    sock.bind(('', server_port))
    sock.listen(5)
    try:
        while True:
            conn, address = sock.accept()
            print('Got connection from', address)
            data = read_sock(conn)
            print(data)
            x = data.split(':')
            if x[0] == 'auth':
                if auth(x[1], x[2]):
                    username_resolver[x[1]] = address[0]
                    ip_resolver[address[0]] = x[1]
                    conn.send(b'pass\n')
                else:
                    conn.send(b'fail\n')
            elif x[0] == 'unr':
                # Check auth
                if x[1] in username_resolver:
                    ip = username_resolver[x[1]]
                else:
                    ip = '-1'
                conn.send((':'.join(['unr', x[1], ip]) + '\n').encode('ascii'))
            elif x[0] == 'ipr':
                # Check auth
                if x[1] in ip_resolver:
                    username = ip_resolver[x[1]]
                else:
                    username = '-1'
                conn.send((':'.join(['ipr', x[1], username]) + '\n').encode('ascii'))
            conn.close()
    except KeyboardInterrupt:
        pass
    sock.close()


main()
