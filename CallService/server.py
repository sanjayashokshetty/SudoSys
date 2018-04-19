import socket
import threading
from _thread import start_new_thread

username_password_db = {'srinag': 'password', 'shreyas': 'password', 'skitty': 'password'}
username_resolver = {}
ip_resolver = {}
username_conn = {}
call_service_port = 8001
msg_service_port = 8002
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


list_of_clients = []


def client_thread(conn, addr):
    global run
    username = read_sock(conn)
    password = read_sock(conn)
    print("Client entered:" + username, password)
    if not auth(username, password):
        msg = 'Invalid Authentication! Connect Again!\n'
        print(msg)
        conn.send(msg.encode())
        conn.close()
        return
    else:
        list_of_clients.append([username, conn])
        print("Client has authenticated on address", addr[0])
        msg = "Welcome to this chatroom!"
        conn.send(msg.encode())
    while run:
        try:
            message = conn.recv(2048).decode()
            if message:
                print(message)
                if message[:3] == 'pm ':
                    user = message[3:].split()
                    message_to_send = 'pm ' + username + ' ' + ' '.join(user[1:]) + '\n'
                    user = user[0]
                    if not pm(message_to_send, user):
                        conn.send("Client not Found!\n".encode())
                else:
                    broadcast('bc ' + username + ' ' + message, conn)

            else:
                remove(conn)

        except:
            continue


client_threads = {}


def msg_listener():
    global run
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('', msg_service_port))
    server.listen(100)
    while run:
        conn, addr = server.accept()
        if not run:
            break
        print(addr[0] + " connected")
        start_new_thread(client_thread, (conn, addr))


def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)


def broadcast(message, connection):
    for clients in list_of_clients:
        if clients[1] != connection:
            try:
                clients[1].send(message.encode())
            except:
                clients[1].close()
                remove(clients)
            break


def pm(msg, to):
    names = [clients[0] for clients in list_of_clients]
    if to in names:
        tosock = list_of_clients[names.index(to)][1]
        try:
            tosock.send(msg.encode())
            print("Sent!")
        except:
            tosock.close()
            remove(tosock)
    else:
        return False


def main():
    global run, call_processor_sock
    call_processor_thread = threading.Thread(target=call_processor)
    call_processor_thread.start()
    msg_listener_thread = threading.Thread(target=msg_listener)
    msg_listener_thread.start()
    try:
        call_processor_thread.join()
        msg_listener_thread.join()
    except KeyboardInterrupt:
        print('Stopping...')
        run = False
        term_sock = socket.socket()
        term_sock.connect(('', call_service_port))
        term_sock.close()
        call_processor_thread.join()
        term_sock = socket.socket()
        term_sock.connect(('', msg_service_port))
        term_sock.close()
        msg_listener_thread.join()
        print('Stopped')


if __name__ == '__main__':
    main()
