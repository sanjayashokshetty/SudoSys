# Python program to implement server side of chat room.
import socket
import select
import sys
from _thread import *
"""The first argument AF_INET is the address domain of the
socket. This is used when we have an Internet Domain with
any two hosts The second argument is the type of socket.
SOCK_STREAM means that data or characters are read in
a continuous flow."""
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# checks whether sufficient arguments have been provided
# if len(sys.argv) != 3:
#     print ("Correct usage: script, IP address, port number")
#     exit()

# takes the first argument from command prompt as IP address
IP_address = '10.50.19.212'

# takes second argument from command prompt as port number
Port = 8002

"""
binds the server to an entered IP address and at the
specified port number.
The client must be aware of these parameters
"""
server.bind((IP_address, Port))

"""
listens for 100 active connections. This number can be
increased as per convenience.
"""
server.listen(100)

list_of_clients = []
list_of_users={'yash':'149','shreyas':'135','sanjay':'136','srinag':'141'}
def auth(usr,pwd):
    if usr in list_of_users.keys() and list_of_users[usr] == pwd:
        return True
    return False

def clientthread(conn, addr):
    username=conn.recv(2048).decode()
    password=conn.recv(2048).decode()
    print("Client entered:"+username,password)
    if not auth(username,password):
        msg='Invalid Authentication! Connect Again!'
        print(msg)
        # conn.send(msg.encode())
        conn.close()
        return
    else:
        list_of_clients.append([username,conn])
        print("Client has authenticated on address",addr[0])

    # sends a message to the client whose user object is conn
        msg="Welcome to this chatroom!"
        # conn.send(msg.encode())
    while True:
        try:
            message = conn.recv(2048).decode()
            if message:
                if message[:3]=='\p ':
                    print("Private mesg..")
                    print ("<" + username + "> " + message)
                    user=message[3:].split()
                    message_to_send='<'+username+'>(Private) '+' '.join(user[1:])+'\n'
                    user=user[0]
                    print(user,":",message_to_send)
                    if not sendPrivate(message_to_send,user):
                        conn.send("Client not Found!\n".encode())
                else:
                    print("Public msg")
                    print ("<" + username + "> " + message)

                    # Calls broadcast function to send message to all
                    message_to_send = "<" + username + "> " + message
                    broadcast(message_to_send, conn)

            else:
                """message may have no content if the connection
                is broken, in this case we remove the connection"""
                remove(conn)

        except:
            continue

"""Using the below function, we broadcast the message to all
clients who's object is not the same as the one sending
the message """
def broadcast(message, connection):
    for clients in list_of_clients:
        if clients[1]!=connection:
            try:
                #print(message)
                clients[1].send(message.encode())
            except:
                clients[1].close()

                # if the link is broken, we remove the client
                remove(clients)
            break
def sendPrivate(msg,to):
    names=[clients[0] for clients in list_of_clients]
    # print(to in names,names)
    if to in names:
        tosock=list_of_clients[names.index(to)][1]
        #print(tosock)
        try:
            tosock.send(msg.encode())
            print("Sent!")
        except:
            tosock.close()
            remove(tosock)
    else:
    	return False

"""The following function simply removes the object
from the list that was created at the beginning of
the program"""
def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)
def main():
    while True:
        conn, addr = server.accept()

    # prints the address of the user that just connected
        print (addr[0] + " connected")
    # creates and individual thread for every user
    # that connects
        start_new_thread(clientthread,(conn,addr))

if __name__ == '__main__':
    main()
