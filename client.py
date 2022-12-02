import sys
import client_lib
from datetime import datetime
from time import gmtime, strftime

#Done by 
#-----Vinay babu Minnakanti
#----- Gopi Krishna jarugula
#----- mariah Roberts
#----- Sushma reddy Gade


#---- Instructor **Dr. Chen pan**

def main():

    print ("\n")
    client_lib.instructions()
    client_id = strftime("%Y%m%d%H%M%S", gmtime())
    file_version_map = {}

    while True:
       
        client_input = sys.stdin.readline()
            
        if "<write>" in client_input:
            while not client_lib.check_valid_input(client_input):       
                 client_input = sys.stdin.readline()
            
            filename = client_input.split()[1]      
            response = client_lib.handle_write(filename, client_id, file_version_map)    
            if response == False:
                print("File unlock polling timeout...")
                print("Try again later...")
            print ("Exiting <write> mode...\n")
            

        if "<read>" in client_input:
            while not client_lib.check_valid_input(client_input):    
                 client_input = sys.stdin.readline()

            filename = client_input.split()[1]   
            client_lib.handle_read(filename, file_version_map, client_id)        
            print("Exiting <read> mode...\n")
        
        if "<list>" in client_input:
            client_socket = client_lib.create_socket()
            client_lib.send_directory_service(client_socket, "", True)
            client_socket.close()

        

        if "<instructions>" in client_input:
            client_lib.instructions()


        if "<quit>" in client_input:
            print("Exiting application...")
            sys.exit()

if __name__ == "__main__":
    main()