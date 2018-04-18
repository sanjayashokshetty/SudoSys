# Python program to implement client side of chat room.
import socket
import select
import sys

def msg_client(IP_address,Port,username,password,run):
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
    run=True
    server.send(password.encode())
    # message = server.recv(2048).decode()
    # if message == "Invalid Authentication! Connect Again!":
    #     run=False
    #     print(message)
    # else:
    #     print(message)
    while run:
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
