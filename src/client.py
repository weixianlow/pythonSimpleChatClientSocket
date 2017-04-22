#Name: Wei Xian Low
#CMP_SC4850
#title: Lab3
#Description: This is the client side of the chat application which allows the user to connect to the server and receive messages and responses from the server. This application will forward all user's command and message to the user.



#nesscary library
import socket, select, string, sys

#function for prompt to user on when to type
def prompt() :
    sys.stdout.write('<You> ')
    sys.stdout.flush()
 
#main function
if __name__ == "__main__":
     
    
    #client connection configuration 
    host = 'localhost'
    port = 15100
    
    #enable socket object and timeout 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
     
    # connect to remote host
    try :
        s.connect((host, port))
    except :
        #if fail
        print 'Unable to connect'
        sys.exit()

    #startup message
    print 'My Chat Room Client V2\n' 
    print 'Connected to server at '+ host + ', port number: '+ str(port) +'.'
    prompt()
     
    while 1:
        socket_list = [sys.stdin, s]
         
        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
         
        #to handle incomming message
        for sock in read_sockets:
            #incoming message from remote server
            if sock == s:
                data = sock.recv(4096)
                if not data :
                    #if data didn't contain anything, and received no response, assume server has been disconnected and proceed to exit
                    print '\nDisconnected from chat server'
                    sys.exit()
                else :
                    #print data from server
                    sys.stdout.write(data)
                    prompt()
             
            #user entered a message
            else :
                #send the message to the server for processing
                msg = sys.stdin.readline()
                s.send(msg)
                prompt()
                
