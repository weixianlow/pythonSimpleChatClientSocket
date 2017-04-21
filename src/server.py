

#needed libraries
import pickle


#to check is the user exist in the savefile
def check_user_exist(list, input):
	if input in list:
		return True
	else
		return False

#to add user into the list, then update savefile
def add_user(list, inputUser, inputPass):
	list[inputUser] = inputPass
	save_file(list)
#to check if the user inputed the right password
def check_password(list, inputUser, inputPass):
	if list[inputUser] == inputPass:
		return 1
#update username to port list association
def update_online_list(list, inputUser, port):
	list[port] = inputUser

def remove_online_list(list, port):
	list.pop(port, None)

#def new_user(list):

#def send_message(socket, message):

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

			

userpassList={	"Tom":"Tom11",
			 	"David":"David22",
			  	"Beth":"Beth33"
			 }

userportList = {}




