import pytest
import subprocess
import time
import socket

#
# DO NOT CHANGE THE CODE BELOW
#

ERROR = b'E'
OK = b'O'
END = b'*'
REJECT = b'R'

BUF_SIZE = 1024
HOST = '127.0.0.1'
PORT = 12345
connections = []

def setup_cnx():
    print('Client starting')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    time.sleep(1) # Ugly; should properly detect when a connection is established
    return sock

def get_line(current_socket):
    buffer = b''
    size = 1
    while True:
        data = current_socket.recv(1)
        size += 1
        if data == END or size >= BUF_SIZE:
            return buffer
        buffer = buffer + data

def put_line(current_socket, data):
    current_socket.sendall((data + '*').encode('utf-8'))

def stop_container():
    cmd = subprocess.run(['sudo', 'docker', 'stop', '226-server'], capture_output=True)
    print(cmd)
    cmd = subprocess.run(['sudo', 'docker', 'rm', '226-server'], capture_output=True)
    print(cmd)

def setup_module(module):
    global connections

    print('\n\n')

    stop_container()
    cmd = subprocess.run(['sudo', 'docker', 'build', '-t', '226-server', '.'], capture_output=True)
    print(cmd)
    cmd = subprocess.run(['sudo', 'docker', 'run', '-d', '--rm', '--log-driver', 'journald', '--name', '226-server', '-p', '12345:12345', '-v', '/dev/log:/dev/log', '226-server'], capture_output=True)
    print(cmd)
    time.sleep(5) # Ugly; should properly detect when the container is up and running

    connections.append(setup_cnx())
    connections.append(setup_cnx())
    connections.append(setup_cnx())
    connections.append(setup_cnx())

    print('\n\n')

def teardown_module(module):
    print('\n\n')

    for c in connections:
        c.close()

    stop_container()

    print('\n\n')

def transmit(client, message):
    print('----\n')
    print('>', client, message)
    put_line(connections[client], message)
    output = get_line(connections[client])
    print('<', client, output)
    return output

#
# DO NOT CHANGE THE CODE ABOVE
#

# def test_invalid_command():
#     output = transmit(0, 'Test') # invalid command
#     assert output == ERROR

# def test_get_board_command():
#     output = transmit(0, 'G')
#     assert output == b'____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\nPlayer 1\'s turn'

# def test_put_and_clear_commands():
#     output = transmit(0, 'P1231')
#     assert output == OK
#     output = transmit(0, 'G')
#     assert output == b'____\n____\n____\n____\n\n____\n____\n___1\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\nPlayer 2\'s turn'
#     output = transmit(0, 'C')
#     assert output == OK
#     output = transmit(0, 'G')
#     assert output == b'____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\nPlayer 1\'s turn'

# def test_out_of_sequence_put():
#     output = transmit(0, 'P1231')
#     assert output == OK
#     output = transmit(0, 'G')
#     assert output == b'____\n____\n____\n____\n\n____\n____\n___1\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\nPlayer 2\'s turn'
#     output = transmit(1, 'P2102')
#     assert output == OK
#     output = transmit(0, 'G')
#     assert output == b'____\n____\n____\n____\n\n____\n____\n___1\n____\n\n____\n2___\n____\n____\n\n____\n____\n____\n____\n\nPlayer 3\'s turn'
#     output = transmit(2, 'P3023')
#     assert output == OK
#     output = transmit(0, 'G')
#     assert output == b'____\n____\n____\n____\n\n____\n____\n___1\n____\n\n____\n2___\n____\n____\n\n__3_\n____\n____\n____\n\nPlayer 1\'s turn'
#     output = transmit(0, 'P0311')
#     assert output == OK
#     output = transmit(0, 'G')
#     assert output == b'____\n____\n____\n_1__\n\n____\n____\n___1\n____\n\n____\n2___\n____\n____\n\n__3_\n____\n____\n____\n\nPlayer 2\'s turn'
#     output = transmit(0, 'P1221') # 2's turn, not 1's turn
#     assert output == ERROR
#     output = transmit(0, 'G')
#     assert output == b'____\n____\n____\n_1__\n\n____\n____\n___1\n____\n\n____\n2___\n____\n____\n\n__3_\n____\n____\n____\n\nPlayer 2\'s turn'
#     output = transmit(0, 'C')
#     assert output == OK
#     output = transmit(0, 'G')
#     assert output == b'____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\nPlayer 1\'s turn'

# def test_invalid_layer():
#     output = transmit(0, 'P4231') # layer out of range
#     assert output == ERROR
#     output = transmit(0, 'G')
#     assert output == b'____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\nPlayer 1\'s turn'
#     output = transmit(0, 'C')
#     assert output == OK

# def test_invalid_row():
#     output = transmit(0, 'P1431') # row out of range
#     assert output == ERROR
#     output = transmit(0, 'G')
#     assert output == b'____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\nPlayer 1\'s turn'
#     output = transmit(0, 'C')
#     assert output == OK

# def test_invalid_column():
#     output = transmit(0, 'P1241') # column out of range
#     assert output == ERROR
#     output = transmit(0, 'G')
#     assert output == b'____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\nPlayer 1\'s turn'
#     output = transmit(0, 'C')
#     assert output == OK

# def test_invalid_token():
#     output = transmit(0, 'P1234') # token out of range
#     assert output == ERROR
#     output = transmit(0, 'G')
#     assert output == b'____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\nPlayer 1\'s turn'
#     output = transmit(0, 'C')
#     assert output == OK

# def test_invalid_put():
#     output = transmit(0, 'PABCD') # invalid tokens
#     assert output == ERROR
#     output = transmit(0, 'G')
#     assert output == b'____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\nPlayer 1\'s turn'
#     output = transmit(0, 'C')
#     assert output == OK

# def test_row_within_level_win():
#     output = transmit(0, 'P1231')
#     assert output == OK
#     output = transmit(0, 'G')
#     assert output == b'____\n____\n____\n____\n\n____\n____\n___1\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\nPlayer 2\'s turn'
#     output = transmit(1, 'P2102')
#     assert output == OK
#     output = transmit(0, 'G')
#     assert output == b'____\n____\n____\n____\n\n____\n____\n___1\n____\n\n____\n2___\n____\n____\n\n____\n____\n____\n____\n\nPlayer 3\'s turn'
#     output = transmit(2, 'P3023')
#     assert output == OK
#     output = transmit(0, 'G')
#     assert output == b'____\n____\n____\n____\n\n____\n____\n___1\n____\n\n____\n2___\n____\n____\n\n__3_\n____\n____\n____\n\nPlayer 1\'s turn'
#     output = transmit(0, 'P1201')
#     assert output == OK
#     output = transmit(0, 'G')
#     assert output == b'____\n____\n____\n____\n\n____\n____\n1__1\n____\n\n____\n2___\n____\n____\n\n__3_\n____\n____\n____\n\nPlayer 2\'s turn'
#     output = transmit(0, 'P1211') # client 0 tries to place token out of turn
#     assert output == ERROR
#     output = transmit(1, 'P1201') # client 1 tries to place token in occupied cell
#     assert output == ERROR
#     output = transmit(1, 'P2223') # client 1 tries to place wrong token 
#     assert output == ERROR
#     output = transmit(1, 'P0002')
#     assert output == OK
#     output = transmit(0, 'G')
#     assert output == b'2___\n____\n____\n____\n\n____\n____\n1__1\n____\n\n____\n2___\n____\n____\n\n__3_\n____\n____\n____\n\nPlayer 3\'s turn'
#     output = transmit(2, 'P3033')
#     assert output == OK
#     output = transmit(0, 'G')
#     assert output == b'2___\n____\n____\n____\n\n____\n____\n1__1\n____\n\n____\n2___\n____\n____\n\n__33\n____\n____\n____\n\nPlayer 1\'s turn'
#     output = transmit(0, 'P1211')
#     assert output == OK
#     output = transmit(0, 'G')
#     assert output == b'2___\n____\n____\n____\n\n____\n____\n11_1\n____\n\n____\n2___\n____\n____\n\n__33\n____\n____\n____\n\nPlayer 2\'s turn'
#     output = transmit(1, 'P1002')
#     assert output == OK
#     output = transmit(0, 'G')
#     assert output == b'2___\n____\n____\n____\n\n2___\n____\n11_1\n____\n\n____\n2___\n____\n____\n\n__33\n____\n____\n____\n\nPlayer 3\'s turn'
#     output = transmit(2, 'P2003')
#     assert output == OK
#     output = transmit(0, 'G')
#     assert output == b'2___\n____\n____\n____\n\n2___\n____\n11_1\n____\n\n3___\n2___\n____\n____\n\n__33\n____\n____\n____\n\nPlayer 1\'s turn'
#     output = transmit(0, 'P1221')
#     assert output == OK
#     output = transmit(0, 'G')
#     assert output == b'2___\n____\n____\n____\n\n2___\n____\n1111\n____\n\n3___\n2___\n____\n____\n\n__33\n____\n____\n____\n\nPlayer 1 wins'
#     output = transmit(0, 'P3331') # client 1 tries to place token after win
#     assert output == ERROR
#     output = transmit(1, 'P3302') # client 2 tries to place token after win
#     assert output == ERROR
#     output = transmit(2, 'P3313') # client 3 tries to place token after win
#     assert output == ERROR
#     output = transmit(0, 'G')
#     assert output == b'2___\n____\n____\n____\n\n2___\n____\n1111\n____\n\n3___\n2___\n____\n____\n\n__33\n____\n____\n____\n\nPlayer 1 wins'
#     print(output.decode())
#     output = transmit(0, 'C')
#     assert output == OK
#     output = transmit(0, 'G')
#     assert output == b'____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\nPlayer 1\'s turn'

# def test_column_within_level_win():
#     output = transmit(0, 'P0031')
#     assert output == OK
#     output = transmit(1, 'P1002')
#     assert output == OK
#     output = transmit(2, 'P2003')
#     assert output == OK
#     output = transmit(0, 'P0131')
#     assert output == OK
#     output = transmit(1, 'P1012')
#     assert output == OK
#     output = transmit(2, 'P2013')
#     assert output == OK
#     output = transmit(0, 'P0231')
#     assert output == OK
#     output = transmit(1, 'P1022')
#     assert output == OK
#     output = transmit(2, 'P2023')
#     assert output == OK
#     output = transmit(0, 'P0331')
#     assert output == OK
#     output = transmit(0, 'G')
#     assert output == b'___1\n___1\n___1\n___1\n\n222_\n____\n____\n____\n\n333_\n____\n____\n____\n\n____\n____\n____\n____\n\nPlayer 1 wins'
#     print(output.decode())
#     output = transmit(0, 'C')
#     assert output == OK

# def test_multiple_threads_or_tasks():
#     connections[0].sendall(('P1231').encode('utf-8'))
#     output = transmit(2, 'G')
#     assert output == b'____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\nPlayer 1\'s turn'
#     output = transmit(1, 'P1022') # Out of turn
#     assert output == ERROR
#     output = transmit(2, 'P2023') # Out of turn
#     assert output == ERROR
#     connections[0].sendall(('*').encode('utf-8'))
#     output = get_line(connections[0])
#     assert output == OK
#     output = transmit(1, 'G')
#     assert output == b'____\n____\n____\n____\n\n____\n____\n___1\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\nPlayer 2\'s turn'
#     output = transmit(0, 'C')
#     assert output == OK

# def test_4_sessions():
#     output = transmit(0, 'G')
#     assert output == b'____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\nPlayer 1\'s turn'
#     output = transmit(1, 'G')
#     assert output == b'____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\nPlayer 1\'s turn'
#     output = transmit(2, 'G')
#     assert output == b'____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\nPlayer 1\'s turn'
#     output = transmit(3, 'G')
#     assert output == REJECT

def test2DDiagonal_one():
    output = transmit(0,'P0001')
    assert output == OK
    output = transmit(1,'P0002')
    assert output == ERROR
    output = transmit(2,'P0003')
    assert output == ERROR

    output = transmit(0,'P0111')
    assert output == OK
    output = transmit(1,'P0002')
    assert output == ERROR
    output = transmit(2,'P0003')
    assert output == ERROR

    output = transmit(0,'P0221')
    assert output == OK
    output = transmit(1,'P0002')
    assert output == ERROR
    output = transmit(2,'P0003')
    assert output == ERROR

    output = transmit(0,'P0331')
    assert output == OK
    output = transmit(0, 'G')
    assert output == b'1___\n_1__\n__1_\n___1\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\nPlayer 1 wins'
    output = transmit(0, 'C')
    assert output == OK

def test2DDiagonal_two():
    output = transmit(0,'P0031')
    assert output == OK
    output = transmit(1,'P0032')
    assert output == ERROR
    output = transmit(2,'P0033')
    assert output == ERROR

    output = transmit(0,'P0121')
    assert output == OK
    output = transmit(1,'P0032')
    assert output == ERROR
    output = transmit(2,'P0033')
    assert output == ERROR

    output = transmit(0,'P0211')
    assert output == OK
    output = transmit(1,'P0032')
    assert output == ERROR
    output = transmit(2,'P0033')
    assert output == ERROR

    output = transmit(0,'P0301')
    assert output == OK
    output = transmit(0, 'G')
    assert output == b'___1\n__1_\n_1__\n1___\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\nPlayer 1 wins'
    output = transmit(0, 'C')
    assert output == OK

def test3DDiagonal():
    output = transmit(0,'P0001')
    assert output == OK
    output = transmit(1,'P0002')
    assert output == ERROR
    output = transmit(2,'P0003')
    assert output == ERROR

    output = transmit(0,'P1111')
    assert output == OK
    output = transmit(1,'P0002')
    assert output == ERROR
    output = transmit(2,'P0003')
    assert output == ERROR

    output = transmit(0,'P2221')
    assert output == OK
    output = transmit(1,'P0002')
    assert output == ERROR
    output = transmit(2,'P0003')
    assert output == ERROR

    output = transmit(0,'P3331')
    assert output == OK
    output = transmit(0, 'G')
    assert output == b'1___\n____\n____\n____\n\n____\n_1__\n____\n____\n\n____\n____\n__1_\n____\n\n____\n____\n____\n___1\n\nPlayer 1 wins'
    output = transmit(0, 'C')
    assert output == OK

def test3DDiagonal_two():
    output = transmit(0,'P0301')
    assert output == OK
    output = transmit(1,'P0302')
    assert output == ERROR
    output = transmit(2,'P0303')
    assert output == ERROR

    output = transmit(0,'P1211')
    assert output == OK
    output = transmit(1,'P0302')
    assert output == ERROR
    output = transmit(2,'P0303')
    assert output == ERROR

    output = transmit(0,'P2121')
    assert output == OK
    output = transmit(1,'P0302')
    assert output == ERROR
    output = transmit(2,'P0303')
    assert output == ERROR

    output = transmit(0,'P3031')
    assert output == OK
    output = transmit(0, 'G')
    assert output == b'____\n____\n____\n1___\n\n____\n____\n_1__\n____\n\n____\n__1_\n____\n____\n\n___1\n____\n____\n____\n\nPlayer 1 wins'
    output = transmit(0, 'C')
    assert output == OK