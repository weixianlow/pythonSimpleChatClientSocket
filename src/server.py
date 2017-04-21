

#needed libraries
import pickle



def check_user_exist(list, input):
	for i in list:
		print list
		if input in list:
			return 1

def add_user(list, inputUser, inputPass):
	list[inputUser] = inputPass

def check_password(list, inputUser, inputPass):
	if list[inputUser] == inputPass:
		return 1

#def new_user(list):

#def send_message():

#def broadcast_online_list():

def save_file(list):
	with open('userList.pickle', 'wb') as handle:
		pickle.dump(list, handle)

def read_file():
	with open('userList.pickle', 'rb') as handle:
		list = pickle.load(handle)
		return list

			

userpassList={	"Tom":"Tom11",
			 	"David":"David22",
			  	"Beth":"Beth33"
			 }

print userpassList

add_user(userpassList, "me", "me11")

print check_user_exist(userpassList, "me")

check_password(userpassList, "me", "me11")


print "savingfile"

save_file(userpassList)

new=read_file()




print new == userpassList


