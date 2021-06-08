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
    server_port = 2004
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((server_host, server_port))
    print(recvline(conn))#connection is ok
    logs = list()
    room_name = "null"
    while True:
        
        message  = json.loads(recvline(conn))
        print(message)
        if message["type"] == "request_room_name_and_role":
            print("enter room name")
            room_name = input()
            sendline(conn,json.dumps({
                "type":"reply_room_name_and_role",
                "payload":{"room_name":room_name,"role":"viewer"}
                }))
            
        elif message["type"] == "information_game" or message["type"] == "notice_player_action" or message["type"] == "notice_draw_card":
            logs.append(message)
            print(message)
        elif message["type"] == "notice_end":
            print("notice_nnd")
            print(len(logs))
            with open('log.txt', 'w') as f:
                for log in logs:
                    f.write("%s\n" % log)

if __name__ == '__main__':
    main()
