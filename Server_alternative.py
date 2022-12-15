import asyncio
import re

HOST = ''
PORT = 44444 # Double check the port
MAX_PLAYERS = 2
BOARD_SIZE = 7
PLAYER_TOKENS = ['X','Y']
EMPTY_TOKEN = '_'

turn = 1
connections = 0
board = [[EMPTY_TOKEN for i in range(BOARD_SIZE)]for i in range (BOARD_SIZE)]


async def send_ok(writer):
    writer.write("OK#".encode())
    await writer.drain()
    
    
async def send_no(writer):
    writer.write("NO#".encode())
    await writer.drain()
    
def clearBoard():
    global turn
    global board
    turn = 1
    board = [[EMPTY_TOKEN for i in range(BOARD_SIZE)]for i in range (BOARD_SIZE)]    

def getBoard():
    stringBoard = ""
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            stringBoard += str(board[row][col])
        stringBoard += '\n'
    return(stringBoard + "#")

async def process_connection(reader, writer, client_id):
    global connections
    while True:
        print("Turn: " + str(turn) + ", connection id: " + str(client_id) + ", connections: " + str(connections))
        
        
        data = await reader.readuntil(b'#')  # this includes the final character
        data = data.decode().strip()#[:-1] # remove newline or ending character
        
        if(turn == client_id and re.search(f'^[1-{BOARD_SIZE}][1-{BOARD_SIZE}]#$', data)):
            await attemptPlace(data,reader,writer,client_id)
        elif(re.search(f'^C#$', data)):
            print("running clearboard")
            clearBoard()
            await send_ok(writer)
        elif(re.search(f'^B#$', data)):
            
            writer.write(getBoard().encode())
            await writer.drain()
        else:
            await send_no(writer)
            print("Client " + str(client_id) + " sent unknown data.")
            

def updateBoardAround(row, col, token):
    # Check tokens above
    pointArray = []
    scannerRow = row - 1
    while(scannerRow >= 0 and board[scannerRow][col] != token and board[scannerRow][col] != EMPTY_TOKEN):
        pointArray.append([scannerRow, col])
        if(scannerRow - 1 >= 0 and board[scannerRow - 1][col] == token):
            for p in pointArray:
                board[p[0]][p[1]] = token
        scannerRow -= 1
        
        
    #Check tokens below
    scannerRow = row + 1
    while(scannerRow < BOARD_SIZE and board[scannerRow][col] != token and board[scannerRow][col] != EMPTY_TOKEN):
        pointArray.append([scannerRow, col])
        if(scannerRow + 1 < BOARD_SIZE and board[scannerRow + 1][col] == token):
            for p in pointArray:
                board[p[0]][p[1]] = token
        scannerRow += 1
        
    #Check tokens left
    scannerCol = col - 1
    while(scannerCol >= 0 and board[row][scannerCol] != token and board[row][scannerCol] != EMPTY_TOKEN):
        pointArray.append([row, scannerCol])
        if(scannerCol - 1 >= 0 and board[row][scannerCol - 1] == token):
            for p in pointArray:
                board[p[0]][p[1]] = token
        scannerCol -= 1
        
    #Check tokens right
    scannerCol = col + 1
    while(scannerCol < BOARD_SIZE and board[row][scannerCol] != token and board[row][scannerCol] != EMPTY_TOKEN):
        pointArray.append([row, scannerCol])
        if(scannerCol + 1 < BOARD_SIZE and board[row][scannerCol + 1] == token):
            for p in pointArray:
                board[p[0]][p[1]] = token
        scannerCol += 1
    
    
              
async def attemptPlace(data,reader,writer,client_id):
    global turn
    global board
    if (board[int(data[0]) - 1 ] [int(data[1]) - 1] == EMPTY_TOKEN):
        board[int(data[0]) - 1 ] [int(data[1]) - 1] = PLAYER_TOKENS[client_id - 1]
        updateBoardAround(int(data[0]) - 1, int(data[1]) - 1, PLAYER_TOKENS[client_id - 1])
        await send_ok(writer)
        print(getBoard())
        
        
        turn = turn + 1
        if turn > MAX_PLAYERS:
                turn = 1
        
    else:
        print("FAILED ATTEMPT PLACE REGEX")
        await send_no(writer)

async def createServer(reader, writer):
    """
    Creates the server and starts listening for player input.
    """
    global connections
    connections += 1
    if connections <= MAX_PLAYERS:
        # try:
            await process_connection(reader, writer, connections)
        # except Exception as e:
        #     print(e)
    connections -= 1
    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(createServer, HOST, PORT)
    await server.serve_forever()

asyncio.run(main())