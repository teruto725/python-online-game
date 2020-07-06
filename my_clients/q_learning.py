import socket
import json
import sys
import numpy as np



########パラメータ#########
initcoins = 3
cards = [1,2,3,4,5]
wheres = [0,1,2,3]#0は山札中,#1は場にある状態,#2は自分が持ってる、#3は相手が持ってる

gamma = 0.9
alpha = 0.3

actions = ["pick","pass"]


class Qtable():
    def __init__(self):
        self.qsells = list()
        li = list(np.zeros((5)))
        for i in wheres:
            for j in wheres:
                for k in wheres:
                    for l in wheres:
                        for m in wheres:
                            for coin in range(0,initcoins*2+1):
                                state = State( [i,j,k,l,m], coin)
                                self.qsells.append(Qsell(state,0))
                                self.qsells.append(Qsell(state,1))
        self.last_qsell = None

    def get_max_q_sell(self, state):
        q1 = None
        q2 = None
        for qsell in self.qsells:
            if qsell.equals(Qsell(state,0)):
                q1 = qsell
            elif qsell.equals(Qsell(state,1)):
                q2 = qsell
            if q1 != None and q2 != None:
                if q1.qvalue>q2.qvalue:
                    return q1
                else:
                    return q2
        print("get_max_error")


    def learn(self, state, last_r, action_types):
        q = None
        act = None
        if len(action_types) == 1:#ここごり押し
            for qsell in self.qsells:
                if qsell.equals(Qsell(state,0)):
                    q = qsell
            act = 0
        elif 
        else:
            q = self.get_max_q_sell(state)
            act = q.act
        if self.last_qsell is not None:
            self.last_qsell.qvalue = self.last_qsell.qvalue+alpha*(last_r+gamma*q.qvalue-self.last_qsell.qvalue)       
        self.last_qsell = q
        return act


class State():
    def __init__(self,cardli,coin):
        self.cardli = cardli
        self.coin = coin
    def equals(self, state):
        if state.cardli == self.cardli and state.coin == self.coin:
            return True
        else:
            return False
    

class Qsell():
    def __init__(self,state,act):
        self.state = state
        self.act = act
        self.qvalue = 0
    

    def equals(self, qsell):
        if qsell.state.equals(self.state) and self.act == qsell.act :
            return True
        else:
            return False

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

def create_state(statsdict,player_name):
    coin = statsdict["fieldinfo"]["fieldcoins"]
    cardli = list(np.zeros((5)))
    cardli[statsdict["fieldinfo"]["fieldcard"]] = 1#場に出ている
    mycards = statsdict["playerinfo"][player_name]["cards"]
    for card in mycards:
        cardli[card-1] = 2

    for key in statsdict["playerinfo"].keys():
        if key == player_name:
            mycards = statsdict["playerinfo"][key]["cards"]
            for card in mycards:
                cardli[card-1] = 2#自分のカード
        else:
            enecards = statsdict["playerinfo"][key]["cards"]
            for card in enecards:
                cardli[card-1] = 3#敵のカード

    return State(cardli,coin)



def main():
    server_host = "localhost"
    server_port = 1000
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((server_host, server_port))
    #print(recvline(conn))#connection is ok

    qtable = Qtable()
    player_name = None
    last_point = initcoins

    results = list()
    vict_sum = 0
    count = 0
    print("episode0")
    while True:
        message  = json.loads(recvline(conn))
        #print(message)
        if message["type"] == "request_room_name_and_role":
            print("enter room name")
            room_name = input()
            print("enter player name")
            player_name = input()
            sendline(conn,json.dumps({
                "type":"reply_room_name_and_role",
                "payload":{"room_name":room_name,"player_name":player_name,"role":"player"}
                }))
        elif message["type"] == "request_action":
            #print("action choice: pick or pass")
            state = create_state(message["payload"]["game_status"], player_name)
            
            
            point = message["payload"]["game_status"]["playerinfo"][player_name]["point"]
            r = point-last_point
            last_point = point
            act = qtable.learn( state, r, message["payload"]["action_types"])
            
            sendline(conn,json.dumps({
                "type":"reply_action",
                "payload":{"action_type":actions[act]}
            }))

        elif message["type"] == "notice_end":
            is_victry = (message["payload"]["game_status"]["rankingorder"][0] == player_name)
            #print(is_victry)
            count +=1
            if is_victry:
                vict_sum += 1
            if count % 50 == 0:
                results.append(vict_sum/50)
                vict_sum = 0
            print("episode"+str(count))
            if count == 10000:
                print(results)
                


if __name__ == '__main__':
    main()

