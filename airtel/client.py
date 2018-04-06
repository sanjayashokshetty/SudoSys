import sys
def main(username):
    import socket          
    s = socket.socket()          
    port = 12344             
    s.connect(('10.50.19.210', port))
    print("enter $ to disconnect")
    flag=True
    while(True):
        msg=input()
        if(msg=='$'):
            break
        s.send((username+":").encode("ascii"))
        s.send((msg).encode("ascii"))
        print(s.recv(1024))
    s.close()       
if __name__ == '__main__':
    if(len(sys.argv))!=2:
        print("Name arguement is not provided")
    else:
        main(sys.argv[1])