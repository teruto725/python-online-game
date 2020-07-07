import socket
import json
import sys
import random

"""
論理的な行動をするクライアント
"""

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
    #print(s)
    b = (s + "\n").encode()
    conn.send(b)

def main():
    server_host = "localhost"
    server_port = 1000
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((server_host, server_port))
    print(recvline(conn))#connection is ok
    player_name = "crever"
    while True:
        message  = json.loads(recvline(conn))
        #print(message)
        if message["type"] == "request_room_name_and_role":
            print("enter room name")
            room_name = input()
            sendline(conn,json.dumps({
                "type":"reply_room_name_and_role",
                "payload":{"room_name":room_name,"player_name":player_name,"role":"player"}
                }))
        elif message["type"] == "request_action":
            #print("action choice: pick or pass")
            action_types = message["payload"]["action_types"]
            action = None
            state  = message["payload"]["game_status"]
            good_card = state["fieldinfo"]["fieldcard"]-1
            if len(action_types) == 1:
                action = action_types[0]
            
            elif random.random() <0.1:
                action = action_types[random.randint(0,1)]
            
            elif state["fieldinfo"]["fieldcard"] <= state["fieldinfo"]["fieldcoins"]:
                action = "pick"
        
            elif good_card in state["playerinfo"][player_name]["cards"]:#-1のカードを持ってたら
                action = "pick"
            else:
                action = "pass"

            sendline(conn,json.dumps({
                "type":"reply_action",
                "payload":{"action_type":action}
            }))
            

if __name__ == '__main__':
    main()
