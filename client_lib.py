from socket import *
import sys
import os
import time
import os.path

#Done by 
#-----Vinay babu Minnakanti
#----- Gopi Krishna jarugula
#----- mariah Roberts
#----- Sushma reddy Gade


#---- Instructor **Dr. Chen pan**

curr_path = os.path.dirname(os.path.realpath(sys.argv[0]))      


def create_socket():
    s = socket(AF_INET, SOCK_STREAM)
    return s

def send_write(client_socket, fileserverIP_DS, fileserverPORT_DS, filename , RW, file_version_map, msg):
    if filename not in file_version_map:
        file_version_map[filename] = 0

    elif RW != "r":
        file_version_map[filename] = file_version_map[filename] + 1

    send_msg = filename + "|" + RW + "|" + msg 

    print("Sending version: " + str(file_version_map[filename]))

    
    client_socket.connect((fileserverIP_DS,fileserverPORT_DS))
    client_socket.send(send_msg.encode())
    #print ("SENT " + send_msg + " to " + str(fileserverIP_DS) + " " + str(fileserverPORT_DS))

def send_read(client_socket, fileserverIP_DS, fileserverPORT_DS, filename , RW, file_version_map, msg, filename_DS, client_id):
    if filename not in file_version_map:
        file_version_map[filename] = 0
        print("REQUESTING FILE FROM FILE SERVER - FILE NOT IN CACHE")
        send_msg = filename + "|" + RW + "|" + msg    
        client_socket.connect((fileserverIP_DS,fileserverPORT_DS))
        client_socket.send(send_msg.encode())
        return False

    cache_file = curr_path + "\\client_cache" + client_id + "\\" + filename_DS  
    if os.path.exists(cache_file) == True:
        send_msg = "CHECK_VERSION|" + filename
        client_socket1 = create_socket()
        client_socket1.connect((fileserverIP_DS,fileserverPORT_DS))
        client_socket1.send(send_msg.encode())
        print ("Checking version...")
        version_FS = client_socket1.recv(1024)    
        version_FS = version_FS.decode()
        client_socket1.close()

    if version_FS != str(file_version_map[filename]):
        print("Versions do not match...")
        print("REQUESTING FILE FROM FILE SERVER...")
        file_version_map[filename] = int(version_FS) 
        send_msg = filename + "|" + RW + "|" + msg    

        
        client_socket.connect((fileserverIP_DS,fileserverPORT_DS))
        client_socket.send(send_msg.encode())
        #print ("SENT MSG: " + send_msg)
        return False    
    else:
        
        print("Versions match, reading from cache...")
        cache(filename_DS, "READ", "r", client_id)

    return True     




def lock_unlock_file(client_socket, client_id, filename, lock_or_unlock):

    serverName = 'localhost'
    serverPort = 4040   
    client_socket.connect((serverName,serverPort))

    if lock_or_unlock == "lock":
        msg = client_id + "_1_:" + filename 
    elif lock_or_unlock == "unlock":
        msg = client_id + "_2_:" + filename   

    
    client_socket.send(msg.encode())
    reply = client_socket.recv(1024)
    reply = reply.decode()

    return reply

def handle_write(filename, client_id, file_version_map):
    # ------ INFO FROM DS ------
    client_socket = create_socket()  # create socket to directory service
    reply_DS = send_directory_service(client_socket, filename, 'w', False)  
    client_socket.close()   

    if reply_DS == "FILE_DOES_NOT_EXIST":
        print(filename + " does not exist on a fileserver")
    else:
        filename_DS = reply_DS.split('|')[0]
        fileserverIP_DS = reply_DS.split('|')[1]
        fileserverPORT_DS = reply_DS.split('|')[2]

        # ------ LOCKING ------
        client_socket = create_socket()
        grant_lock = lock_unlock_file(client_socket, client_id, filename_DS, "lock")
        client_socket.close()

        while grant_lock != "file_granted":
            print("File not granted, polling again...")
            client_socket = create_socket()
            grant_lock = lock_unlock_file(client_socket, client_id, filename_DS, "lock")
            client_socket.close()

            if grant_lock == "TIMEOUT":     
                return False

            time.sleep(0.1)     

        print("You are granted the file...")

        # ------ ClIENT WRITING TEXT ------
        print ("Write some text...")
        print ("<end> to finish writing")
        print_breaker()
        write_client_input = ""
        while True:
            client_input = sys.stdin.readline()
            if "<end>" in client_input:  # check if user wants to finish writing
                break
            else: 
                write_client_input += client_input
        print_breaker()

        

        # ------ WRITING TO FS ------
        client_socket = create_socket()
        send_write(client_socket, fileserverIP_DS, int(fileserverPORT_DS), filename_DS, "a+", file_version_map, write_client_input) # send text and filename to the fileserver
        #print ("SENT FOR WRITE")
        reply_FS = client_socket.recv(1024)
        reply_FS = reply_FS.decode()
        client_socket.close()

        print (reply_FS.split("...")[0])   
        version_num = int(reply_FS.split("...")[1]) 
        
        if version_num != file_version_map[filename_DS]:
            print("Server version no changed - updating client version no.")
            file_version_map[filename_DS] = version_num


        # ------ CACHING ------
        cache(filename_DS, write_client_input, "a+", client_id)

        # ------ UNLOCKING ------
        client_socket = create_socket()
        reply_unlock = lock_unlock_file(client_socket, client_id, filename_DS, "unlock")
        client_socket.close()
        print (reply_unlock)

        return True

def cache(filename_DS, write_client_input, RW, client_id):
    cache_file = curr_path + "\\client_cache" + client_id + "\\" + filename_DS       # append the cache folder and filename to the path
    
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)        

    if RW == "a+" or RW == "w":
        with open(cache_file, RW) as f:        
            f.write(write_client_input)
    else:
        with open(cache_file, "r") as f:        
            print_breaker()
            print(f.read())
            print_breaker()

    

def handle_read(filename, file_version_map, client_id):
    client_socket = create_socket()  # create socket to directory service
    reply_DS = send_directory_service(client_socket, filename, 'r', False)  
    client_socket.close()   # close directory service connection

    if reply_DS == "FILE_DOES_NOT_EXIST":
        print(filename + " does not exist on a fileserver")
    else:
        
        filename_DS = reply_DS.split('|')[0]
        fileserverIP_DS = reply_DS.split('|')[1]
        fileserverPORT_DS = reply_DS.split('|')[2]

        client_socket = create_socket()  
        read_cache = send_read(client_socket, fileserverIP_DS, int(fileserverPORT_DS), filename_DS, "r", file_version_map, "READ", filename_DS, client_id) # send filepath and read to file server

        if not read_cache:
            reply_FS = client_socket.recv(1024)    
            reply_FS = reply_FS.decode()
            client_socket.close()

            if reply_FS != "EMPTY_FILE":
                print_breaker()
                print (reply_FS)
                print_breaker()

                cache(filename_DS, reply_FS, "w", client_id)  
                print (filename_DS + " successfully cached...")
            else:
                print(filename_DS + " is empty...")
                del file_version_map[filename_DS]


def send_directory_service(client_socket, filename, RW, list_files):
    serverName = 'localhost'
    serverPort = 9090   # port of directory service
    client_socket.connect((serverName,serverPort))

    if not list_files:
        msg = filename + '|' + RW
        
        client_socket.send(msg.encode())
        reply = client_socket.recv(1024)
        reply = reply.decode()
    else:
        msg = "LIST"
        
        client_socket.send(msg.encode())
        reply = client_socket.recv(1024)
        reply = reply.decode()
        client_socket.close()
        print ("Listing files on directory server...")
        print (reply)

    #print (reply)
    return reply

def instructions():
    print("Client server is running and ready for your command\n")
    # instructions to the user
    print ("------------------- INSTRUCTIONS ----------------------")
    print ("<write> [filename] - write to file mode")
    print ("<end> - finish writing")
    print ("<read> [filename] - read from file mode")
    print ("<list> - lists all existing files")
    print ("<instructions> - lets you see the instructions again")
    print ("<quit> - exits the application")
    print ("-------------------------------------------------------\n")

def print_breaker():
    print ("--------------------------------")

def check_valid_input(input_string):
    
    if len(input_string.split()) < 2:
        print ("Incorrect format")
        instructions()
        return False
    else:
        return True