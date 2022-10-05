#!/usr/bin/python3
import socket
import re
BUF_SIZE = 1024
HOST = ''
PORT = 12345
BOARD_SIZE = 4
GENERIC_ERROR = b'E\n'

# Global board array. '_' means the space is empty. 1-3 means the place has been taken by a player.
board = [[['_' for i in range(BOARD_SIZE)]for i in range (BOARD_SIZE)] for i in range(BOARD_SIZE)]

# Global turn. Represents what player's turn it is. Between 1 to 3.
turn = 1

def sendError(sc):
    """
    Sends a generic error message to the client.

    Args:
        sc (socket): The network socket.
    """
    sc.sendall(GENERIC_ERROR)

def createBoardString():
    """
    This function creates and returns a string, containing the current state of the board.

    Returns:
        string: This string contains a representation of the board.
    """
    stringBoard = ""
    for layer in range(BOARD_SIZE):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                stringBoard += str(board[layer][row][col])
            stringBoard += '\n'
        stringBoard += '\n'
    stringBoard += '\n'
    return stringBoard

def getInput(input, sc):
    """
    Based on user input, decides what action to take.
    1:Mark the board. 2:Print the board. 3:Clear the board.
    Mark: P####, Get: 'G', Clear: 'C'

    Args:
        input (bytes): The user input, in bytes.
        sc (socket): The network socket.
    """
    input = input.decode('utf-8')
    if re.search('^P[0-3][0-3][0-3][1-3]$', input):
        markBoard(input,sc)
    elif re.search('^G$', input):
        getBoard(sc)
    elif re.search('^C$', input):
        clearBoard(sc)
    else:
        sendError(sc)

def getBoard(sc):
    """
    Sends a string representation of the board to the client, using createBoardString()

    Args:
        sc (socket): The network socket.
    """
    sc.sendall(bytes(createBoardString(),'utf-8'))

def clearBoard(sc):
    """
    Clears the board array and sets the turn back to player 1's turn.

    Args:
        sc (socket): The network socket.
    """
    global turn
    turn = 1
    for layer in range(BOARD_SIZE):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                board[layer][row][col] = '_'
    sc.sendall(bytes('O\n','utf-8'))

def markBoard(input, sc):
    """
    Place a mark on the board at the specified location.
    Does NOT validate input, as that should be already done in getInput()
    Input format is: Pxyz[1-3] / P####

    Args:
        input (string): String representation of the put request.
        sc (Socket): The network socket.
    """
    global turn
    print(input[4] + "," + str(turn))
    if int(input[4]) == turn and board[int(input[1])][int(input[2])][int(input[3])] == '_':
        board[int(input[1])][int(input[2])][int(input[3])] = turn
        sc.sendall(bytes('O\n','utf-8'))
        turn = turn + 1
        if turn == 4:
            turn = 1
    else:
        sendError(sc)

def createServer():
    """
    Creates the server and starts listening for player input.
    """
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

createServer()