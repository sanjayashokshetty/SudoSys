import socket
import threading
from select import select

server_port = 8001

clients = []
run = True


def man():
    global run, clients
    while run:
        try:
            readable_client, _, _ = select(clients, [], [], .1)
            for client in readable_client:
                try:
                    msg = client.recv(69).decode('utf-8')
                    if len(msg) == 0:
                        client.close()
                        clients.remove(client)
                    else:
                        print('Got: ' + str(msg))
                except UnicodeDecodeError:
                    pass
        except KeyboardInterrupt:
            pass


def main():
    global run, clients
    man_thread = threading.Thread(target=man)
    man_thread.start()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', server_port))
    sock.listen(5)
    try:
        while True:
            conn, address = sock.accept()
            print('Got connection from', address)
            clients.append(conn)
    except KeyboardInterrupt:
        pass
    run = False
    man_thread.join()
    for client in clients:
        client.close()
    sock.close()


main()
