#!/usr/bin/python3
import socket
import re
# import threading
import asyncio
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
LAYER = 1
COL = 2
ROW = 3
TOKEN = 4


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

#Global number of current connections
connections = 0

# Senaphore Locks
# locks = []
#for i in range(NUM_PLAYERS):
    # locks.append(threading.Semaphore())
    # locks[-1].acquire()

async def contactPlayer(reader, writer, player_id):
    """Allows the player to send data to the server. Rejects out of turn place statements.

    Args:
        sock (socket): The network socket
        player_id (int): Player's turn thread ID.
    """
    global turn
    while True:
        data = await reader.readuntil(b'*')
        data = data[:-1].strip()

        #If it was not your turn to play, do validation, it will catch it.
        #If it was a bad format, P or C, do validation, it will catch it.
        if not re.search('^P[0-3][0-3][0-3][1-3]$', data.decode('utf-8')) or turn - 1 != player_id or game_won:
            if(data.decode('utf-8')[0] != 'P'):
                await handleInput(data, writer)
            else:
                await sendError(writer)
        #If it was your turn and the command is valid, place your token!
        else:
            # locks[0].acquire()
            await handleInput(data, writer)
            # locks[0].release()

async def sendError(sc):
    """
    Sends a generic error message to the client.

    Args:
        sc (socket): The network socket.
    """
    sc.write(GENERIC_ERROR)
    await sc.drain()

async def sendOkay(sc):
    """
    Sends a generic success message to the client.

    Args:
        sc (socket): The network socket.
    """
    
    sc.write(GENERIC_OKAY)
    await sc.drain()

async def sendReject(sc):
    """
    Sends a generic connection rejection message to the client.

    Args:
        sc (socket): The network socket.
    """
    
    sc.write(GENERIC_REJECT)
    await sc.drain()

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

SEARCH_TOKEN = '^C$'
GET_TOKEN = '^G$'

async def handleInput(input, sc):
    """
    Based on user input, decides what action to take.
    1:Mark the board. 2:Print the board. 3:Clear the board.
    Mark: P####, Get: 'G', Clear: 'C'

    Args:
        input (bytes): The user input, in bytes.
        sc (socket): The network socket.
    """
    input = input.decode('utf-8')

    if re.search(SEARCH_TOKEN, input):
        await clearBoard(sc)
    elif re.search(GET_TOKEN, input):
            await getBoard(sc)
    elif game_won:
        await sendError(sc)
    else:
        if re.search(f'^P[0-{ARRAY_DIMENSION}][0-{ARRAY_DIMENSION}][0-{ARRAY_DIMENSION}][{turn}]$', input):
            await markBoard(input,sc)
        else:
            await sendError(sc)

async def getBoard(sc):
    """
    Sends a string representation of the board to the client, using createBoardString()

    Args:
        sc (socket): The network socket.
    """
    sc.write(bytes(createBoardString() + '*','utf-8'))
    await sc.drain()

async def clearBoard(sc):
    """
    Clears the board array and sets the turn back to player 1's turn.

    Args:
        sc (socket): The network socket.
    """
    await sendOkay(sc)
    global turn
    global game_won
    turn = 1
    # locks[0].release()
    game_won = False
    for layer in range(BOARD_SIZE):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                board[layer][row][col] = '_'

async def markBoard(input, sc):
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
    if int(input[TOKEN]) == turn and board[int(input[LAYER])][int(input[COL])][int(input[ROW])] == '_':
        board[int(input[LAYER])][int(input[COL])][int(input[ROW])] = turn
        await sendOkay(sc)
        game_won = checkWin()
        
    else:
        await sendError(sc)
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

async def createServer(reader, writer):
    """
    Creates the server and starts listening for player input.
    """
    global connections
    connections += 1
    if connections <= NUM_PLAYERS:
        await contactPlayer(reader, writer, connections-1)
    else:
        await sendReject(writer)
    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(createServer, HOST, PORT)
    await server.serve_forever()


            
asyncio.run(main())