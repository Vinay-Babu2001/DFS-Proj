#Done by 
#-----Vinay babu Minnakanti
#----- Gopi Krishna jarugula
#----- mariah Roberts
#----- Sushma reddy Gade


#---- Instructor **Dr. Chen pan**
from socket import *
from collections import defaultdict		
import sys

serverAddr = "localhost"
serverPort = 4040
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind((serverAddr, serverPort))
serverSocket.listen(10)
print ('LOCKING SERVICE is ready to receive...')

def check_if_unlocked(filename, filename_locked_map):

	
	if filename in filename_locked_map:		
		if filename_locked_map[filename] == "unlocked":
			return True
		else:
			return False
	else:
		filename_locked_map[filename] = "unlocked"
		return True

def main():

	filename_locked_map = {}
	filename_clients_map = defaultdict(list)
	waiting_client = False
	client_timeout_map = {}


	while 1:
		connectionSocket, addr = serverSocket.accept()
		recv_msg = connectionSocket.recv(1024)
		recv_msg = recv_msg.decode()

		print("\nRECEIVED: " + recv_msg )

		if "_1_:" in recv_msg:
			client_id = recv_msg.split("_1_:")[0]
			filename = recv_msg.split("_1_:")[1]
			waiting_client = False


			unlocked = check_if_unlocked(filename, filename_locked_map)
			if unlocked == True:
				count_temp = 0		

				if len(filename_clients_map[filename]) == 0:	
					filename_locked_map[filename] = "locked"	
					grant_message = "file_granted"
					print("SENT: " + grant_message + " ---- " + client_id)
					connectionSocket.send(grant_message.encode())	

				elif filename in filename_clients_map:			
					for filename,values in filename_clients_map.items():	
						for v in values:									
							if v == client_id and count_temp == 0:			
								filename_clients_map[filename].remove(v)	
								filename_locked_map[filename] = "locked"	
								grant_message = "file_granted"			
								print("SENT: " + grant_message +" ---- " + client_id)	
								connectionSocket.send(grant_message.encode())	
							count_temp += 1

			else:				
				grant_message = "file_not_granted"

				if client_id in client_timeout_map:		
					client_timeout_map[client_id] = client_timeout_map[client_id] + 1	
					print("TIME: " + str(client_timeout_map[client_id]))
				else:
					client_timeout_map[client_id] = 0	


				if client_timeout_map[client_id] == 100:	
					timeout_msg = "TIMEOUT"
					for filename,values in filename_clients_map.items():	
						for v in values:									
							if v == client_id:		
								filename_clients_map[filename].remove(v)	
					del client_timeout_map[client_id]			
					connectionSocket.send(timeout_msg.encode())	
				else:

					if filename in filename_clients_map:						
						for filename,values in filename_clients_map.items():	
							for v in values:							
								if v == client_id:					
									waiting_client = True			
					
					if waiting_client == False:			
						filename_clients_map[filename].append(client_id)	

					print("SENT: " + grant_message + client_id)
					connectionSocket.send(grant_message.encode()) 

		elif "_2_:" in recv_msg:		
			client_id = recv_msg.split("_2_:")[0]
			filename = recv_msg.split("_2_:")[1]

			filename_locked_map[filename] = "unlocked"		
			grant_message = "File unlocked..."
			connectionSocket.send(grant_message.encode())	

		connectionSocket.close()



if __name__ == "__main__":
	main()