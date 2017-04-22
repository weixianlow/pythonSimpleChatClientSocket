

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

def check_if_being_used(list, username):
	for x in list:
		if list[x] == username:
			return True

	return False


def broadcast_online_list(sock, list):
	result="\r<SERVER> Online List: "
	for x in list:
		if list[x] != False:
			result = result + list[x] + ','

	sock.send(result+"\n")

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
				if userportList[sock] != False:
					broadcast_data(sock, "\r<SERVER> %s is offline\n" % userportList[sock])



    
userpassList=read_file()



userportList= {}    
# List to keep track of socket descriptors
CONNECTION_LIST = []
RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
PORT = 15100
MAX_CONNECTION = 3
 
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
				
				if data:
					#if user use send command:
					data = data.split(" ", 1)
					
					if data[0] == 'send':
						if userportList[sock] == False:
							sock.send("\r<SERVER> Error: Sorry, Please login to send message. Enter 'login' to start\n")

						else:
							content = data[1].split(" ", 1)
							if content[0] == 'all':
								print userportList[sock] +" to all: " + content[1]
								broadcast_data(sock, "\r" + '<' + userportList[sock] + ' to all> ' + content[1])
							else:
								check=0
								for x in userportList:
									if userportList[x] == content[0] and userportList[sock] != content[0]:
										x.send("\r" + '<'+ userportList[sock] +' to you>' + content[1])
										print userportList[sock] +" to ("+userportList[x]+"): "+content[1]
										check=1
								if check == 0:
									if userportList[sock] == content[0]:
										sock.send("\r<SERVER> Error: You can't send a message to yourself\n")
									else:
										sock.send("\r<SERVER> Error: Username provided is not currently online or found.\n")
					elif data[0] == 'send\n':
						sock.send("\r<SERVER> Error: not enough argument. Please use the following: 'send all 'message' ' or 'send username 'message' '\n")
					#if user use login command:		
					elif data[0] == 'login':
						content = data[1].split(" ", 1)
						
						if len(userportList) > MAX_CONNECTION:
							sock.send("\r<SERVER> Error: Sorry, maximum amount of user connected is acheived. Please try again later.\n")
						else:
							if check_if_being_used(userportList, content[0]) == True:
								sock.send("\r<SERVER> Error: Sorry, the user has already logon with a different client.\n")
							else:
								if check_user_exist(userpassList, content[0]) == True:
									if check_password(userpassList, content[0], content[1].rstrip("\n")):
										sock.send("\r<SERVER> Welcome %s, you have been logon.\n" % content[0])
										print "%s logon to the server"%content[0]
										update_online_list(userportList, content[0], sock)
										broadcast_data(sock, "\r" + '<SERVER> %s is online.\n'%content[0])
										
									else:
										sock.send("\r<SERVER> Error: Incorrect Login Credentials\n")
								else:
									sock.send("\r<SERVER> Error: No User Found\n")
					#if user use newuser command:
					elif data[0] == 'newuser':
						content = data[1].split(" ", 1)
						if check_user_exist(userpassList, content[0]) == False:
							add_user(userpassList, content[0],content[1].rstrip("\n"))
							sock.send("\r<SERVER> Welcome %s, you have been registed. Please login to proceed.\n"%content[0]+'\n')
						else:
							sock.send("\r<SERVER> Error: Username exist, please try again with a different username.\n")
					#if user use logout command:
					elif data[0].rstrip("\n") == 'logout':
						sock.send("\r<SERVER> Loging you out now\n")
						
						if userportList[sock]!=False:
							
							broadcast_data(sock, "\r<SERVER> %s is offline\n" % userportList[sock])
						if userportList[sock]!=False:
							print "%s is offline.\n" % userportList[sock]
						sock.close()
						CONNECTION_LIST.remove(sock)
						remove_online_list(userportList,sock)
					elif data[0] == 'login\n':
						sock.send("\r<SERVER> Error: Please use the following format to login: 'login username password'\n")

						
					#if user use who command:
					elif data[0].rstrip("\n") == 'who':
						broadcast_online_list(sock, userportList)


					#if user use random garbish command:
					else:
						sock.send("\r<SERVER> Error: Sorry, Incorrect command received or incorrect command format detected.\n")

			except:
				print "ERROR"
				
				sock.close()
				CONNECTION_LIST.remove(sock)

				
				continue
 
server_socket.close()

