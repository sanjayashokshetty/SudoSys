import threading    
list_of_clients = []
 
def clientthread(conn, addr):
    conn.send(("Welcome to this chatroom!").encode("ascii"))
    while True:
        try:
            message = conn.recv(2048)
            print(message)
            if message:

                """prints the message and address of the
                user who just sent the message on the server
                terminal"""
                print("<" + addr[0] + "> " + message)

                # Calls broadcast function to send message to all
                message_to_send = "<" + addr[0] + "> " + message
                broadcast(message_to_send, conn)

            else:
                """message may have no content if the connection
                is broken, in this case we remove the connection"""
                remove(conn)

        except:
            continue
def broadcast(message, connection):
    for clients in list_of_clients:
        if clients!=connection:
            try:
                clients.send(message.encode("ascii"))
            except:
                clients.close()
 
                # if the link is broken, we remove the client
                remove(clients)
def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)
def main():
    import socket               
    s = socket.socket()         
    print("Socket successfully created") 
    port = 12345           
    s.bind(('10.50.19.210', port))        
    print("socket binded to %s" %(port))
    s.listen(5)     
    print("socket is listening")            
    while True:
        conn, addr = s.accept()
        list_of_clients.append(conn)
        t=threading.Thread(target=clientthread,args=(conn,addr))
        t.start() 
    c.close()
    s.close()
if __name__ == '__main__':
    main()
