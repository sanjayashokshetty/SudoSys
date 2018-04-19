import select
import sys
import socket
import threading
from time import sleep
import pyaudio

incoming_call_port = 8000
call_service_port = 8001
msg_service_port = 8002
server_ip = '10.50.16.223'
incoming_call_thread, outgoing_call_thread = None, None
expecting_call_back_from = None
run = True
recv_sock = None
ans = None
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 64
in_call = False
audio = None

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


def auth(username, password):
    try:
        sock = socket.socket()
        sock.connect((server_ip, call_service_port))
        sock.send(('auth:' + username + ':' + password + '\n').encode('ascii'))
        data = read_sock(sock)
        sock.close()
        return data == 'pass'
    except ConnectionRefusedError:
        print('Could not connect to server')
        return False


def un_auth(username, password):
    try:
        sock = socket.socket()
        sock.connect((server_ip, call_service_port))
        sock.send(('unauth:' + username + ':' + password + '\n').encode('ascii'))
        sock.close()
    except ConnectionRefusedError:
        print('Could not connect to server')


def unr(username):
    try:
        sock = socket.socket()
        sock.connect((server_ip, call_service_port))
        sock.send(('unr:' + username + '\n').encode('ascii'))
        data = read_sock(sock)
        sock.close()
        ip = data.split(':')[2]
        if ip == '-1':
            return None
        return ip
    except ConnectionRefusedError:
        print('Could not connect to server')
        return None


def ipr(ip):
    try:
        sock = socket.socket()
        sock.connect((server_ip, call_service_port))
        sock.send(('ipr:' + ip + '\n').encode('ascii'))
        data = read_sock(sock)
        sock.close()
        username = data.split(':')[2]
        if username == '-1':
            return None
        return username
    except ConnectionRefusedError:
        print('Could not connect to server')
        return None


def listen_call():
    global expecting_call_back_from, outgoing_call_thread, run, recv_sock, ans, in_call
    recv_sock = socket.socket()
    recv_sock.bind(('', incoming_call_port))
    recv_sock.listen(1)
    while run:
        me_caller = False
        conn, address = recv_sock.accept()
        if not run:
            break
        username = ipr(address[0])
        if expecting_call_back_from is not None and expecting_call_back_from != username:
            conn.close()
            continue
        if expecting_call_back_from is None:
            print('\n' + username + ' is calling you! Accept?(y/n): ', end='')
            ans = None
            while run and ans is None:
                sleep(.1)
            if ans == 'y':
                conn.send(b'y\n')
                outgoing_call_thread = threading.Thread(target=call, kwargs={'username': username})
                outgoing_call_thread.start()
            else:
                conn.send(b'n\n')
                conn.close()
                continue
        else:
            me_caller = True
            conn.send(b'y\n')
        in_call = True
        speaker = audio.open(format=FORMAT, channels=CHANNELS,
                             rate=RATE, output=True,
                             frames_per_buffer=CHUNK)
        try:
            while run and in_call:
                frame = conn.recv(CHUNK)
                speaker.write(frame)
                sleep(.001)
        except:
            pass
        speaker.close()
        conn.close()
        in_call = False
        print('Call disconnected!')
        # if not me_caller:+
        print('# ', end='')
    recv_sock.close()


def call(username):
    global expecting_call_back_from, run, in_call, outgoing_call_thread
    ip = unr(username)
    if ip is None:
        return
    expecting_call_back_from = username
    in_call = True
    try:
        call_sock = socket.socket()
        call_sock.connect((ip, incoming_call_port))
        resp = read_sock(call_sock)
        print(resp)
        mic = audio.open(format=FORMAT, channels=CHANNELS,
                         rate=RATE, input=True,
                         frames_per_buffer=CHUNK)
        if resp == 'y':
            try:
                while run and in_call:
                    call_sock.sendall(mic.read(CHUNK))
                    sleep(.001)
            except:
                pass
        mic.close()
        call_sock.close()
    except ConnectionRefusedError:
        print('User unavailable!')
    expecting_call_back_from = None
    in_call = False
    outgoing_call_thread = None


msg_server = None


def pm(req):
    if msg_server is not None:
        msg_server.send(req.encode())


def bc(req):
    if msg_server is not None:
        msg_server.send(req.encode())


inbox = []
broad = []


def msg_service(username, password):
    global run, msg_server
    msg_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    msg_server.connect((server_ip, msg_service_port))
    username += '\n'
    msg_server.send(username.encode())
    password += '\n'
    msg_server.send(password.encode())
    message = msg_server.recv(2048).decode()
    if message == "Invalid Authentication! Connect Again!":
        msg_server.close()
        return
    sockets_list = [msg_server]
    while run:
        read_sockets, write_socket, error_socket = select.select(sockets_list, [], [], 0.1)
        if read_sockets:
            for socks in read_sockets:
                if socks == msg_server:
                    msg = socks.recv(2048).decode()
                    x = msg.split()
                    if x[0] == 'pm':
                        inbox.append(x[1] + ' : ' + ' '.join(x[2:]))
                    if x[0] == 'bc':
                        broad.append(x[1] + ' : ' + ' '.join(x[2:]))
    msg_server.close()


def clear_screen():
    print(chr(27) + "[H" + chr(27) + "[J", end='')


def main(username, password):
    global run, ans, outgoing_call_thread, audio, in_call
    if not auth(username, password):
        print('Auth Failure')
        return
    audio = pyaudio.PyAudio()
    clear_screen()
    print('Welcome to SudoSys. Type "help" for more info.')
    incomming_call_thread = threading.Thread(target=listen_call)
    incomming_call_thread.start()
    msg_service_thread = threading.Thread(target=msg_service, kwargs={'username': username, 'password': password})
    msg_service_thread.start()
    while True:
        try:
            while True:
                x = input("# ")
                y = x.split()
                if y[0] == 'exit':
                    raise KeyboardInterrupt
                elif y[0] == 'call':
                    outgoing_call_thread = threading.Thread(target=call, kwargs={'username': y[1]})
                    outgoing_call_thread.start()
                elif y[0] == 'ipr':
                    print(ipr(y[1]))
                elif y[0] == 'unr':
                    print(unr(y[1]))
                elif y[0] == 'pm':
                    pm(x)
                elif y[0] == 'bc':
                    bc(x)
                elif y[0] == 'inbox':
                    print('Your inbox')
                    for msg in inbox:
                        print(msg)
                    inbox.clear()
                elif y[0] == 'shoutbox':
                    print('Get ready!')
                    for msg in broad:
                        print(msg)
                    broad.clear()
                elif y[0] == 'help':
                    print('HELP')
                elif y[0] == 'y' or y[0] == 'n':
                    ans = y[0]
                else:
                    print('Unknown command')

        except KeyboardInterrupt:
            if in_call:
                in_call = False
                outgoing_call_thread.join()
            else:
                run = False
                term_sock = socket.socket()
                term_sock.connect(('', incoming_call_port))
                term_sock.close()
                break
    incomming_call_thread.join()
    msg_service_thread.join()
    un_auth(username, password)
    print()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python3 client.py username password')
    else:
        main(sys.argv[1], sys.argv[2])
