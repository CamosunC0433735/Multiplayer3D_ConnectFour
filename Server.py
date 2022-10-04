#!/usr/bin/python3
import socket
import re
BUF_SIZE = 1024
HOST = ''
PORT = 12345

board = [[['_' for i in range(4)]for i in range (4)] for i in range(4)]
turn = 1


def createBoardString():
    stringBoard = ""
    for layer in range(4):
        #stringBoard += 'Layer: ' + str(layer) + '\n'
        for row in range(4):
            for col in range(4):
                stringBoard += str(board[layer][row][col])
            stringBoard += '\n'
        stringBoard += '\n'
    stringBoard += '\n'
    return stringBoard

#Get input - Place a token, get the board or clear the board and reset the turn
def getInput(input, sc):
    input = input.decode('utf-8')
    if re.search('^P[0-3][0-3][0-3][1-3]$', input):
        markBoard(input,sc)
    elif re.search('^G$', input):
        getBoard(sc)
    elif re.search('^C$', input):
        clearBoard(sc)
    else:
        sc.sendall(bytes('E\n','utf-8'))

def getBoard(sc):
    sc.sendall(bytes(createBoardString(),'utf-8'))

def clearBoard(sc):
    global turn
    turn = 1
    for layer in range(4):
        for row in range(4):
            for col in range(4):
                board[layer][row][col] = '_'
    sc.sendall(bytes('O\n','utf-8'))

#Put a mark on the board
def markBoard(input, sc):
    global turn
    print(input[4] + "," + str(turn))
    if int(input[4]) == turn and board[int(input[1])][int(input[2])][int(input[3])] == '_':
        board[int(input[1])][int(input[2])][int(input[3])] = turn
        sc.sendall(bytes('O\n','utf-8'))
        turn = turn + 1
        if turn == 4:
            turn = 1
    else:
        sc.sendall(bytes('E\n','utf-8'))


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock: # TCP socket
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Details later
    sock.bind((HOST, PORT)) # Claim messages sent to port "PORT"
    sock.listen(1) # Enable server to receive 1 connection at a time
    print('Server:', sock.getsockname()) # Source IP and port
    while True:
        sc, sockname = sock.accept() # Wait until a connection is established
        with sc:
            print('Client:', sc.getpeername()) # Dest. IP and port
            # while True:
            data = sc.recv(BUF_SIZE) # recvfrom not needed since address is known
            getInput(data, sc)