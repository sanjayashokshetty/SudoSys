import sys
import select
import socket         
def main(username):
    s = socket.socket()          
    port = 12345           
    s.connect(('10.50.19.210', port))
    print("enter $ to disconnect")
    flag=True
    while(True):
        sockets_list = [sys.stdin, s]
        read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])
        print(read_sockets)
        for socks in read_sockets:
            if socks == s:
                print("true")
                message = socks.recv(2048)
                print(message)
            else:
                print("false")
                message = sys.stdin.readline()
                s.send(message.encode("ascii"))
                sys.stdout.write("<You>")
                sys.stdout.write(message)
                sys.stdout.flush()
    s.close()       
if __name__ == '__main__':
    if(len(sys.argv))!=2:
        print("Name arguement is not provided")
    else:
        main(sys.argv[1])
