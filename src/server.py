

#needed libraries
import pickle
import socket
import select



#to check is the user exist in the savefile
def check_user_exist(list, input):
	if input in list:
		return True
	else:
		return False

#to add user into the list, then update savefile
def add_user(list, inputUser, inputPass):
	list[inputUser] = inputPass
	save_file(list)
#to check if the user inputed the right password
def check_password(list, inputUser, inputPass):
	
	if list[inputUser] == inputPass:
	
		return True
	else:
	
		return False
#update username to port list association
def update_online_list(list, inputUser, port):
	list[port] = inputUser

def remove_online_list(list, port):
	list.pop(port, None)

#def new_user(list):

#def broadcast_online_list():

#save user and password list to a pickle file
def save_file(list):
	with open('userList.pickle', 'wb') as handle:
		pickle.dump(list, handle)
#reading user and password list from a pickle file
def read_file():
	with open('userList.pickle', 'rb') as handle:
		list = pickle.load(handle)
		return list

#Function to broadcast chat messages to all connected clients
def broadcast_data (sock, message):
	
    #Do not send the message to master socket and the client who has send us the message
	for socket in CONNECTION_LIST:
		if socket != server_socket and socket != sock :
			try :
				socket.send(message)
			except :
                # broken socket connection may be, chat client pressed ctrl+c for example
				socket.close()
				CONNECTION_LIST.remove(socket)

    
userpassList=read_file()



userportList= {}    
# List to keep track of socket descriptors
CONNECTION_LIST = []
RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
PORT = 5000
 
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# this has no effect, why ?
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("0.0.0.0", PORT))
server_socket.listen(10)

# Add server socket to the list of readable connections
CONNECTION_LIST.append(server_socket)

print "Chat server started on port " + str(PORT)

while 1:
    # Get the list sockets which are ready to be read through select
	read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])

	for sock in read_sockets:
        #New connection
        
		if sock == server_socket:
        	
            # Handle the case in which there is a new connection recieved through server_socket
				sockfd, addr = server_socket.accept()
				CONNECTION_LIST.append(sockfd)
				update_online_list(userportList, False, sockfd)
		        
        #Some incoming message from a client
		else:
            # Data recieved from client, process it
			try:
                #In Windows, sometimes when a TCP program closes abruptly,
                # a "Connection reset by peer" exception will be thrown
				data = sock.recv(RECV_BUFFER)
				data = data.split(" ", 1)
				if data:
					if data[0] == 'send':
						if userportList[sock] == False:
							sock.send("Sorry, Please login to send message. Enter 'login' to start\n")

						else:
							print "Broadcasting: %s" % data[1]
							broadcast_data(sock, "\r" + '<' + userportList[sock] + '> ' + data[1])
					elif data[0] == 'login':
						content = data[1].split(" ", 1)	
						
						if check_user_exist(userpassList, content[0]) == True:
							if check_password(userpassList, content[0], content[1].rstrip("\n")):
								sock.send("Welcome %s, you have been accepted.\n" % content[0])
								print "%s has been authenticated correctly"%content[0]
								update_online_list(userportList, content[0], sock)
								broadcast_data(sock, "\r" + '<SERVER> %s is online.\n'%content[0])
							else:
								sock.send("Incorrect Login Credentials\n")
						else:
							sock.send("Incorrect Login Credentials\n")
					elif data[0] == 'newuser':
						content = data[1].split(" ", 1)
						if check_user_exist(userpassList, content[0]) == False:
							add_user(userpassList, content[0],content[1].rstrip("\n"))
							sock.send("Welcome %s, you have been registed. Please login to proceed.\n"%content[0])
						else:
							sock.send("Username exist, please try again with a different username.\n")
					elif data[0].rstrip("\n") == 'logout':
						sock.send("Loging you out now\n")
						
						broadcast_data(sock, "%s is offline\n" % userportList[sock])
						print "Client (%s, %s) is offline. Username: %s" % addr, userportList[sock]
						sock.close()
						CONNECTION_LIST.remove(sock)
						remove_online_list(userportList,sock)



					else:
						sock.send("Sorry, Incorrect Command Received.\n")

			except:
				
				print "Client (%s, %s) is offline" % addr
				sock.close()
				CONNECTION_LIST.remove(sock)
				continue
 
server_socket.close()

