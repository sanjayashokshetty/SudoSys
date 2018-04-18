import socket
import threading

username_password_db = {'srinag': 'password', 'shreyas': 'password', 'skitty': 'password'}
username_resolver = {}
ip_resolver = {}
username_conn = {}
call_service_port = 8001
run = True
call_processor_sock = None


def auth(username, password):
    return username in username_password_db and username_password_db[username] == password


buffer = b''


def read_sock(conn):
    global buffer
    data = buffer
    buffer = b''
    while True:
        block = conn.recv(10)
        end = block.find(b'\n')
        if end >= 0:
            buffer += block[end + 1:]
            data += block[:end + 1]
            break
        data += block
    data = data.decode()
    return data.strip()


def call_processor():
    global run, call_processor_sock
    call_processor_sock = socket.socket()
    call_processor_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    call_processor_sock.bind(('', call_service_port))
    call_processor_sock.listen(5)
    while run:
        conn, address = call_processor_sock.accept()
        if not run:
            break
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
        elif x[0] == 'unauth':
            if auth(x[1], x[2]):
                username_resolver.pop(x[1], None)
                ip_resolver.pop(address[0], None)
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
    call_processor_sock.close()


def main():
    global run, call_processor_sock
    call_processor_thread = threading.Thread(target=call_processor)
    call_processor_thread.start()
    try:
        call_processor_thread.join()
    except KeyboardInterrupt:
        print('Stopping')
        run = False
        term_sock = socket.socket()
        term_sock.connect(('', call_service_port))
        term_sock.close()
        call_processor_thread.join()


if __name__ == '__main__':
    main()
