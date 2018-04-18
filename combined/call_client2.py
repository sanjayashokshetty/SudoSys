import sys
import socket
import threading
from time import sleep
import pyaudio
import msg_client

incoming_call_port = 8003
server_port = 8001
msg_server_port=8002
server_ip = '10.50.19.212'
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
msg_run=True
buffer = b''
#msg client
def msg_client(IP_address,Port,username,password):
    global msg_run,server_ip,msg_server_port
    IP_address=server_ip
    Port=msg_server_port
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # if len(sys.argv) != 3:
    #     print("Correct usage: script, IP address, port number")
    #     exit()
    # IP_address = str(sys.argv[1])
    # Port = int(sys.argv[2])
    server.connect((IP_address, Port))
    # usr=input("Enter username:")
    server.send(username.encode())
    # pwd=input("Enter password:")
    server.send(password.encode())
    # message = server.recv(2048).decode()
    # if message == "Invalid Authentication! Connect Again!":
    #     run=False
    #     print(message)
    # else:
    #     print(message)
    while msg_run:
        sockets_list = [sys.stdin,server]
        read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])
        for socks in read_sockets:
            if socks == server:
                msg=socks.recv(2048).decode()
                # usr=msg.split()
                # msg=' '.join(usr[1:])
                # usr=usr[0]
                sys.stdout.write(msg)
            else:
                #sys.stdout.write("Enter message:")
                message = sys.stdin.readline()
                server.send(message.encode())
                sys.stdout.write("<You>")
                sys.stdout.write(message)

    server.close()


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
        sock.connect((server_ip, server_port))
        sock.send(('auth:' + username + ':' + password + '\n').encode('ascii'))
        # sock1=socket.socket()
        # sock1.connect((server_ip,msg_server_port))
        # sock1.send((username).encode('ascii'))
        # sock1.send((password).encode('ascii'))
        data = read_sock(sock)
        # data = read_sock(sock1)
        sock.close()
        if data=='pass':
            sock1=socket.socket()
            sock1.connect((server_ip,msg_server_port))
            sock1.send((username).encode('ascii'))
            sock1.send((password).encode('ascii'))
            # data1 = read_sock(sock1)
            sock1.close()
        return data == 'pass'
    except ConnectionRefusedError:
        print('Could not connect to server')
        return False


def un_auth(username, password):
    try:
        sock = socket.socket()
        sock.connect((server_ip, server_port))
        sock.send(('unauth:' + username + ':' + password + '\n').encode('ascii'))
        sock.close()
    except ConnectionRefusedError:
        print('Could not connect to server')


def pm(username, msg):
    pass


def unr(username):
    try:
        sock = socket.socket()
        sock.connect((server_ip, server_port))
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
        sock.connect((server_ip, server_port))
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
            print('\n' + username + ' is calling you! Accept?(y/n): ')
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
        # if not me_caller:
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
                    print('pm')
                elif y[0] == 'inbox':
                    print('Your inbox')
                elif y[0] == 'shoutbox':
                    print('Get ready!')
                elif y[0] == 'help':
                    print('HELP')
                elif y[0] == 'y' or y[0] == 'n':
                    ans = y[0]
                elif y[0] == 'msg':
                    msg_run=True
                    msg_client(username,password)
                else:
                    print('Unknown command')

        except KeyboardInterrupt:
            if msg_run==True:
                msg_run=False
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
    un_auth(username, password)
    print()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python3 client.py username password')
    else:
        main(sys.argv[1], sys.argv[2])
