# first of all import the socket library

def main():
    import socket               
    s = socket.socket()         
    print("Socket successfully created") 
    port = 12344             
    s.bind(('10.50.19.210', port))        
    print("socket binded to %s" %(port))
    s.listen(5)     
    print("socket is listening")            
    while True:
       c, addr = s.accept()
       print(c.recv(1024))     
       c.send(("Thank you for connecting").encode("ascii"))
    c.close()
if __name__ == '__main__':
    main()