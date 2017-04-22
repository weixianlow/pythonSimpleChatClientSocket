#Name: Wei Xian Low
#CMP_SC 4850
#Title: Lab 3
#Description: Server Side Socket Client, the server will handle all client interaction and forward all message received to other clients. The server will also respond to client's command request, such as 'who', 'send', 'login', 'logout', and 'newuser'

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

#remove username from onlinelist after user logout
def remove_online_list(list, port):
	list.pop(port, None)

#check if the username is logon from a different client
def check_if_being_used(list, username):
	for x in list:
		if list[x] == username:
			return True

	return False

#gather client that is online and send to requesting user
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



#application will attempt to grab registered user list from savefile    
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

#while loop for server
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
				#check is data is empty, reduce error
				if data:
					# scraping command from client and check command
					data = data.split(" ", 1)
					#if user used 'send' command
					if data[0] == 'send':
						#check if user has authenticated
						if userportList[sock] == False:
							sock.send("\r<SERVER> Error: Sorry, Please login to send message. Enter 'login' to start\n")

						else:
							#scrape second command from 'send' command
							content = data[1].split(" ", 1)
							#if user send to 'all'
							if content[0] == 'all':
								print userportList[sock] +" to all: " + content[1]
								#call broadcast_data
								broadcast_data(sock, "\r" + '<' + userportList[sock] + ' to all> ' + content[1])
							#if user didn't specify a command or specify a specific user
							else:
								check=0
								#if user specified a user
								for x in userportList:
									if userportList[x] == content[0] and userportList[sock] != content[0]:
										x.send("\r" + '<'+ userportList[sock] +' to you>' + content[1])
										print userportList[sock] +" to ("+userportList[x]+"): "+content[1]
										check=1
								#if user didn't specify a user or left empty
								if check == 0:
									#prevent user from sending message to themselve
									if userportList[sock] == content[0]:
										sock.send("\r<SERVER> Error: You can't send a message to yourself\n")
									else:
										#to prevent sending to user that's not connected or incorrect username
										sock.send("\r<SERVER> Error: Username provided is not currently online or found.\n")

					#error checking
					elif data[0] == 'send\n':
						
						sock.send("\r<SERVER> Error: not enough argument. Please use the following: 'send all 'message' ' or 'send username 'message' '\n")


					#if user use login command:		
					elif data[0] == 'login':
						content = data[1].split(" ", 1)
						#to check if number of current connection doesn't break maximum
						if len(userportList) > MAX_CONNECTION:

							sock.send("\r<SERVER> Error: Sorry, maximum amount of user connected is acheived. Please try again later.\n")
						else:
							#check if the user has already been log on
							if check_if_being_used(userportList, content[0]) == True:

								sock.send("\r<SERVER> Error: Sorry, the user has already logon with a different client.\n")
							else:
								#check if username valid or not
								if check_user_exist(userpassList, content[0]) == True:
									#check if password credential valid
									if check_password(userpassList, content[0], content[1].rstrip("\n")):

										#notify user has logon successfully
										sock.send("\r<SERVER> Welcome %s, you have been logon.\n" % content[0])
										print "%s logon to the server"%content[0]
										update_online_list(userportList, content[0], sock)

										#notify online client that new user is added to server
										broadcast_data(sock, "\r" + '<SERVER> %s is online.\n'%content[0])
										
									else:
										#notify user password invalide
										sock.send("\r<SERVER> Error: Incorrect Login Credentials\n")
								else:
									#notify user username not found
									sock.send("\r<SERVER> Error: No User Found\n")

					#error checking from incorrect number of argument				
					elif data[0] == 'login\n':

						sock.send("\r<SERVER> Error: Please use the following format to login: 'login username password'\n")

					#if user use newuser command:
					elif data[0] == 'newuser':
						content = data[1].split(" ", 1)
						if check_user_exist(userpassList, content[0]) == False:

							add_user(userpassList, content[0],content[1].rstrip("\n"))
							#notify user new user added
							sock.send("\r<SERVER> Welcome %s, you have been registed. Please login to proceed.\n"%content[0]+'\n')
						else:
							#notify user username has taken
							sock.send("\r<SERVER> Error: Username exist, please try again with a different username.\n")


					#if user use logout command:
					elif data[0].rstrip("\n") == 'logout':
						sock.send("\r<SERVER> Loging you out now\n")
						
						if userportList[sock]!=False:
							#broadcast to people a client has disconnected
							broadcast_data(sock, "\r<SERVER> %s is offline\n" % userportList[sock])
						if userportList[sock]!=False:

							print "%s is offline.\n" % userportList[sock]

						#closing socket
						sock.close()
						CONNECTION_LIST.remove(sock)
						#update online list
						remove_online_list(userportList,sock)


					

						
					#if user use who command:

					elif data[0].rstrip("\n") == 'who':
						#notify user who is online
						broadcast_online_list(sock, userportList)


					#if user use random garbish command:
					else:
						sock.send("\r<SERVER> Error: Sorry, Incorrect command received or incorrect command format detected.\n")

			except:
				print "ERROR"
				#if error detected, close socket for best practice
				sock.close()
				CONNECTION_LIST.remove(sock)

				
				continue
 
server_socket.close()

