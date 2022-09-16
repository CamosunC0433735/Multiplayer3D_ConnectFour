#!/usr/bin/python3
import socket
import re
BUF_SIZE = 1024
HOST = ''
PORT = 12345

board = [[[0 for i in range(4)]for i in range (4)] for i in range(4)]

def createBoardString():
    stringBoard = ""
    for layer in range(4):
        stringBoard += 'Layer: ' + str(layer) + '\n'
        for row in range(4):
            for col in range(4):
                stringBoard += str(board[layer][row][col])
            stringBoard += '\n'
        stringBoard += '\n'
    return stringBoard

def markBoard(coords, sc):
    coords = coords.decode('utf-8')
    validInput = re.search('^P[0-3][0-3][0-3][1-3]', coords)
    print(validInput)
    if validInput:
        board[int(coords[1])][int(coords[2])][int(coords[3])] = 1
    else:
        sc.sendall(bytes('Invalid input\n','utf-8'))


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock: # TCP socket
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Details later
	sock.bind((HOST, PORT)) # Claim messages sent to port "PORT"
	sock.listen(1) # Enable server to receive 1 connection at a time
	print('Server:', sock.getsockname()) # Source IP and port
	while True:
		sc, sockname = sock.accept() # Wait until a connection is established
		with sc:
			print('Client:', sc.getpeername()) # Dest. IP and port
			while True:
				data = sc.recv(BUF_SIZE) # recvfrom not needed since address is known
				markBoard(data, sc)
				sc.sendall(bytes(createBoardString(), 'utf-8'))