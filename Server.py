#!/usr/bin/python3
import socket
import re
import threading
import logging
import logging.handlers

BUF_SIZE = 1024
HOST = ''
PORT = 12345
BOARD_SIZE = 4
GENERIC_ERROR = b'E*'
GENERIC_OKAY = b'O*'
GENERIC_REJECT = b'R*'
NUM_PLAYERS = 3
ARRAY_DIMENSION = 3

# Setup logging
logger = logging.getLogger('client.py')
logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

# Global board array. '_' means the space is empty. 1-3 means the place has been taken by a player.
board = [[['_' for i in range(BOARD_SIZE)]for i in range (BOARD_SIZE)] for i in range(BOARD_SIZE)]

# Global turn. Represents what player's turn it is. Between 1 to 3.
turn = 1

#Global game won bool
game_won = False

#Senaphore Locks
locks = []
for i in range(NUM_PLAYERS):
    locks.append(threading.Semaphore())
    locks[-1].acquire()

def contactPlayer(sc, player_id):
    """Allows the player to send data to the server. Rejects out of turn place statements.

    Args:
        sock (socket): The network socket
        player_id (int): Player's turn thread ID.
    """
    global turn
    while True:
        data = b''
        while True:
            inputChar = sc.recv(1)
            if inputChar == b'*':
                break
            if inputChar == b'\n':
                continue
            data += inputChar

        #If it was not your turn to play, do validation, it will catch it.
        #If it was a bad format, P or C, do validation, it will catch it.
        if not re.search('^P[0-3][0-3][0-3][1-3]$', data.decode('utf-8')) or turn - 1 != player_id or game_won:
            if(data.decode('utf-8')[0] != 'P'):
                handleInput(data, sc)
            else:
                sendError(sc)
        #If it was your turn and the command is valid, place your token!
        else:
            locks[0].acquire()
            handleInput(data, sc)
            locks[0].release()

def sendError(sc):
    """
    Sends a generic error message to the client.

    Args:
        sc (socket): The network socket.
    """
    sc.sendall(GENERIC_ERROR)

def sendOkay(sc):
    """
    Sends a generic error message to the client.

    Args:
        sc (socket): The network socket.
    """
    
    sc.sendall(GENERIC_OKAY)

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
    if(not game_won):
        stringBoard += 'Player ' + str(turn) + '\'s turn'
    else:
        stringBoard += "Player " + str(turn) + " wins"
    return stringBoard

def handleInput(input, sc):
    """
    Based on user input, decides what action to take.
    1:Mark the board. 2:Print the board. 3:Clear the board.
    Mark: P####, Get: 'G', Clear: 'C'

    Args:
        input (bytes): The user input, in bytes.
        sc (socket): The network socket.
    """
    input = input.decode('utf-8')

    if re.search('^C$', input):
        clearBoard(sc)
    elif re.search('^G$', input):
            getBoard(sc)
    elif game_won:
        sendError(sc)
    else:
        if re.search(f'^P[0-3][0-3][0-3][{turn}]$', input):
            markBoard(input,sc)
        else:
            sendError(sc)

def getBoard(sc):
    """
    Sends a string representation of the board to the client, using createBoardString()

    Args:
        sc (socket): The network socket.
    """
    sc.sendall(bytes(createBoardString() + '*','utf-8'))

def clearBoard(sc):
    """
    Clears the board array and sets the turn back to player 1's turn.

    Args:
        sc (socket): The network socket.
    """
    sendOkay(sc)
    global turn
    global game_won
    turn = 1
    #locks[0].release()
    game_won = False
    for layer in range(BOARD_SIZE):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                board[layer][row][col] = '_'

def markBoard(input, sc):
    """
    Place a mark on the board at the specified location.
    Does NOT validate input, as that should be already done in handleInput()
    Input format is: Pxyz[1-3] / P####

    Args:
        input (string): String representation of the put request.
        sc (Socket): The network socket.
    """
    global game_won
    global turn
    if int(input[4]) == turn and board[int(input[1])][int(input[2])][int(input[3])] == '_':
        board[int(input[1])][int(input[2])][int(input[3])] = turn
        sendOkay(sc)
        game_won = checkWin()
        
    else:
        sendError(sc)
    if not game_won:
                turn = turn + 1
                if turn == 4:
                    turn = 1

def checkWin():
    """Checks if the player's who's turn it currently is has won the game.

    Returns:
        bool: Returns true if the player has won, false otherwise.
    """
    # Non-3D diagonal win checking
    for offset in range(ARRAY_DIMENSION):
        for angle in range(2):
            for layer in range(BOARD_SIZE):
                count = 0
                for row in range(BOARD_SIZE):
                    if (
                        (offset == 0 and angle == 0 and board[layer][row][row]==turn)  or
                        (offset == 0 and angle == 1 and board[layer][row][BOARD_SIZE-1 - row]==turn) or 
                        (offset == 1 and angle == 0 and board[row][row][layer]==turn) or
                        (offset == 1 and angle == 1 and board[row][BOARD_SIZE-1 - row][layer]==turn) or
                        (offset == 2 and angle == 0 and board[row][layer][row]==turn) or
                        (offset == 2 and angle == 1 and board[row][layer][BOARD_SIZE-1 - row]==turn)
                        ):
                            count += 1
                if count == BOARD_SIZE:
                    return True

    # Direct line win checking
    for offset in range(ARRAY_DIMENSION):
        for layer in range(BOARD_SIZE):
            for row in range(BOARD_SIZE):
                count = 0
                for col in range(BOARD_SIZE):
                    if (
                        (offset == 0 and board[layer][row][col] == turn) or
                        (offset == 1 and board[col][layer][row] == turn) or
                        (offset == 2 and board[layer][col][row] == turn)
                        ):
                        count += 1
                if count == BOARD_SIZE:
                    return True
    
    
    # 3D Diagonal win checking
    for angle in range(4):
        count = 0
        for row in range(BOARD_SIZE):
            if (
                (angle == 0 and board[row][row][row]==turn)  or
                (angle == 1 and board[row][row][BOARD_SIZE-1 - row]==turn) or 
                (angle == 2 and board[row][BOARD_SIZE-1 - row][row]==turn) or 
                (angle == 3 and board[BOARD_SIZE-1 - row][row][row]==turn)
                ):
                    count += 1
        if count == BOARD_SIZE:
            return True
    
    return False

def createServer():
    """
    Creates the server and starts listening for player input.
    """
    connected_clients = 0
    locks[0].release()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock: # TCP socket
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Details later
        sock.bind((HOST, PORT)) # Claim messages sent to port "PORT"
        sock.listen(NUM_PLAYERS) # Enable server to receive 1 connection at a time
        logger.info('Server:' + str(sock.getsockname())) # Source IP and port
        while True:
            sc, sockname = sock.accept()
            if connected_clients < NUM_PLAYERS:
                threading.Thread(target = contactPlayer, args = (sc, connected_clients)).start()
                connected_clients += 1
            else:
                sc.sendall(GENERIC_REJECT)
                sc.close()
                
            
createServer()