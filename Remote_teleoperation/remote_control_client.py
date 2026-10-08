import socket
import time

RASPBERRY_IP = "192.168.1.79"
PORT = 5000

sock = socket.socket()
sock.connect((RASPBERRY_IP, PORT))

print("Connected to robot")

# test simple
while True:
    cmd = input("command: ")
    sock.send((cmd + "\n").encode())
