# _*_ coding:utf-8 _*_

import socket
import base64
import hashlib
import sys
import os
from UrlManager import UrlManager

import urllib.request

HOST = 'localhost'
PORT = 8080
connectionlist = {}

MAGIC_STRING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

HANDSHAKE_STRING = "HTTP/1.1 101 Switching Protocols\r\n" \
                   "Upgrade:websocket\r\n" \
                   "Connection: Upgrade\r\n" \
                   "Sec-WebSocket-Accept: {1}\r\n" \
                   "WebSocket-Location: ws://{2}/chat\r\n" \
                   "WebSocket-Protocol:chat\r\n\r\n"

def handshake(con):
    headers = {}
    shake = con.recv(1024)
    if not len(shake):
        return False
    header, data = shake.split('\r\n\r\n'.encode(), 1)
    for line in header.split('\r\n'.encode())[1:]:
        key, val = line.split(': '.encode(), 1)
        headers[key] = val
    if b'Sec-WebSocket-Key' not in headers:
        print('This socket is not websocket, client close.')
        con.close()
        return False
    sec_key = headers[b'Sec-WebSocket-Key']
    res_key = base64.b64encode(hashlib.sha1((sec_key.decode("utf-8") + MAGIC_STRING).encode()).digest())
    str_handshake = HANDSHAKE_STRING.replace('{1}', res_key.decode("utf-8")).replace('{2}', HOST + ':' + str(PORT))
    con.send(str_handshake.encode())
    return True


def start_server(path):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((HOST, PORT))
        server.listen(100)
        print('bind %s,ready to use' % PORT)
    except:
        print('Server is already running, quit')
        sys.exit()
    i = 0
    while True:
        connection, address = server.accept()
        username = address[0]
        connectionlist['connection' + str(i)] = connection
        if handshake(connection):
            print('handshake success')
            try:
                manager = UrlManager(connection, r'http://www.meitulu.com', '', path, True);
                manager.start()
            except:
                print('start new thread error')
                connection.close()
        i += 1

if __name__ == '__main__':
    try:
        path = os.getcwd()
        path = os.path.join(path,'jiandan')
        if os.path.exists(path):
            os.rmdir(path) 
        if not os.path.exists(path):
            os.mkdir(path)
    except:
        pass
    start_server(path)
