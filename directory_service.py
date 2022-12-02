#Done by 
#-----Vinay babu Minnakanti
#----- Gopi Krishna jarugula
#----- mariah Roberts
#----- Sushma reddy Gade


#---- Instructor **Dr. Chen pan**
import os
import csv      
from socket import *

serverPort = 9090
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('localhost', serverPort))
serverSocket.listen(10)
print ('DIRECTORY SERVICE is ready to receive...')

def check_mappings(client_msg, list_files):

	filename = client_msg.split('|')[0]
	RW = client_msg.split('|')[1]

	with open("file_mappings.csv",'rt') as infile:        
		d_reader = csv.DictReader(infile, delimiter=',')    
		header = d_reader.fieldnames    	
		file_row = ""
		for row in d_reader:
			if list_files == False:
				
				user_filename = row['user_filename']
				primary_copy = row['primary']

				if user_filename == filename and RW == 'w':		
					print("WRITING")
					actual_filename = row['actual_filename']	
					server_addr = row['server_addr']			
					server_port = row['server_port']			

					print("actual_filename: " + actual_filename)
					print("server_addr: " + server_addr)
					print("server_port: " + server_port)

					return actual_filename + "|" + server_addr + "|" + server_port	

				elif user_filename == filename and RW == 'r' and primary_copy == 'no':
					print("READING")
					actual_filename = row['actual_filename']	
					server_addr = row['server_addr']			
					server_port = row['server_port']			

					print("actual_filename: " + actual_filename)
					print("server_addr: " + server_addr)
					print("server_port: " + server_port)

					return actual_filename + "|" + server_addr + "|" + server_port	

			else:
				user_filename = row['user_filename']
				file_row = file_row + user_filename +  "\n"		
		if list_files == True:
			return file_row		
	return None 	

def main():

	while 1:
		connectionSocket, addr = serverSocket.accept()

		response = ""
		recv_msg = connectionSocket.recv(1024)
		recv_msg = recv_msg.decode()

		if "LIST" not in recv_msg:
			response = check_mappings(recv_msg, False)		
		elif "LIST" in recv_msg:
			response = check_mappings(recv_msg, True)

		if response is not None:	
			response = str(response)
			print("RESPONSE: \n" + response)
			print("\n")
		else:
			response = "FILE_DOES_NOT_EXIST"
			print("RESPONSE: \n" + response)
			print("\n")

		connectionSocket.send(response.encode())	
			
		connectionSocket.close()


if __name__ == "__main__":
	main()