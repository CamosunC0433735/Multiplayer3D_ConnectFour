#!/usr/bin/python3
import socket
import struct
import threading
HOST = '127.0.0.1'
PORT = 12345
NUM_CLIENTS = 2

locks = []
for i in range( NUM_CLIENTS):
    locks.append(threading.Semaphore())
    locks[-1].acquire()
    msg = b'Please begin\n'

def get_line(current_socket):
    buffer = b''
    while True:
        data = current_socket.recv(1)
        if data ==b'':
            raise Exception('Socket disconnected')
        if data == b'\n':
            return buffer
        buffer = buffer + data

def contactClient(sock, client_id):
    global msg
    sc, sockname = sock.accept()
    with sc:
        while True:
            locks[client_id].acquire()
            sc.sendall(msg)
            msg = get_line(sc) + b'\n'
            locks[(client_id + 1) % NUM_CLIENTS].release()


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((HOST, PORT))
sock.listen(NUM_CLIENTS)
num_clients = 0
while num_clients != NUM_CLIENTS:
    threading.Thread(target = contactClient, args = (sock, num_clients, )).start()
    num_clients = num_clients + 1
locks[0].release()