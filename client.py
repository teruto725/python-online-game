import socket
import json
import sys


def recvline(conn):#文字列受け取り
    """
    receive data from socket until newline
    """
    buf = b''
    while True:
        c = conn.recv(1)
        if c == b"\n":
            break
        buf += c
    return buf.decode()

def sendline(conn, s):#文字列送信
    """
    send data with newline
    """
    print(s)
    b = (s + "\n").encode()
    conn.send(b)

def main():
    server_host = "localhost"
    server_port = 1000
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((server_host, server_port))
    print(recvline(conn))#connection is ok
    while True:
        
        message  = json.loads(recvline(conn))
        print(message)
        if message["type"] == "request_room_name":
            print("enter room name")
            room_name = input()
            print("enter player name")
            player_name = input()
            sendline(conn,json.dumps({
                "type":"reply_room_name",
                "payload":{"room_name":room_name,"player_name":player_name}
                }))
        elif message["type"] == "request_action":
            print("action choice: pick or pass")
            action = "pick"
            sendline(conn,json.dumps({
                "type":"reply_action",
                "payload":{"action_type":action}
            }))
            

if __name__ == '__main__':
    main()
