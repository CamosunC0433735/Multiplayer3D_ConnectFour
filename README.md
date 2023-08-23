# Multiplayer3D Connect Four

This project is a basic networked game.

### How to run:
Download the repository, and run Server.py

### How to play:
For the most simple manner of connecting to the server, use netcat, ncat or related tools.
By default, the server runs on port 12345.
`netcat [local ip] 12345`

Once you are connected, a few options are available.
Note that you must always send '*' at the end of your command, as that lets the server know that no more input is coming.

#### Get the board:
Use `G*`
#### Place a token:
On your turn, use `P[0-3][0-3][0-3][1-3]*`
The first three parameters represent the location on the board.
The final parameter represents your player number.
#### Clear the board:
You may use `C*` to wipe the board and start over.

### Winning:
To win the game, match 4 of your tokens in any way, including diagonals.
Think of the board as a 4x4 cube--you can match tokens across the board in any direction.
