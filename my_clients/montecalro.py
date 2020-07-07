import socket
import json
import sys
import numpy as np
import matplotlib.pyplot as plt
import random
import csv


"""
結果
1~5の順番で必ずカードが出る＋相手ができるだけパスするなら勝率100

"""


########パラメータ#########

initcoins = 3
cards = [1,2,3,4,5]
wheres = [0,1,2,3]#0は山札中,#1は場にある状態,#2は自分が持ってる、#3は相手が持ってる

gamma = 0.9
alpha = 0.03
upsilon = 30
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
        td_gosa = None
        if len(action_types) == 1:#ここごり押し
            for qsell in self.qsells:
                if qsell.equals(Qsell(state,0)):
                    q = qsell
            act = 0
        elif random.randint(0,100) <= upsilon:#εグリーディー
            act = random.randint(0,1)
            for qsell in self.qsells:
                if qsell.equals(Qsell(state,act)):
                    q = qsell
        else:
            q = self.get_max_q_sell(state)
            act = q.act

        if self.last_qsell is not None:
            td_gosa = last_r+gamma*q.qvalue-self.last_qsell.qvalue
            self.last_qsell.qvalue = self.last_qsell.qvalue+alpha*(td_gosa) 

        self.last_qsell = q

        return act,td_gosa 


class State():
    def __init__(self,cardli,coin):
        self.cardli = cardli
        self.coin = coin
    def equals(self, state):
        if state.cardli == self.cardli and state.coin == self.coin:
            return True
        else:
            return False
    def to_dict(self,state):
        

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

def to_dict():



def create_state(statsdict,player_name):
    coin = statsdict["fieldinfo"]["fieldcoins"]
    cardli = list(np.zeros((5)))
    cardli[statsdict["fieldinfo"]["fieldcard"]-1] = 1#場に出ている
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

def plot_graph(li):
    x = range(len(li))
    y = li
    plt.plot(x, y);

def main():
    server_host = "localhost"
    server_port = 1000
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((server_host, server_port))
    #print(recvline(conn))#connection is ok
    upsilon = 30
    qtable = Qtable()
    player_name = None

    results = list()
    gosa_results = list()
    vict_sum = 0
    episode_num = 0
    player_name = "monte"
    memory = [] #montekaruroを持っておく

    print("episode0")
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
            state = create_state(message["payload"]["game_status"], player_name)
            
            #point = message["payload"]["game_status"]["playerinfo"][player_name]["point"]
            action_types = message["payload"]["action_types"]
            act = None
            q = None
            if len(action_types) == 1:#行動が一つしか
                for qsell in qtable.qsells:
                    if qsell.equals(Qsell(state,0)):
                        q = qsell
                act = 0
                memory.append(q)
            elif random.randint(0,100) <= upsilon:#εグリーディ
                act = random.randint(0,1)
                for qsell in qtable.qsells:
                    if qsell.equals(Qsell(state,act)):
                        q = qsell
            else:#q値をもとに行動選択
                q = qtable.get_max_q_sell(state)
                act = q.act


            memory.append(q)# ルートを記憶
            

            sendline(conn,json.dumps({
                "type":"reply_action",
                "payload":{"action_type":actions[act]}
            }))

        elif message["type"] == "notice_end":
            is_victry = (message["payload"]["game_status"]["rankingorder"][0] == player_name)
            #print(is_victry)
            #reaward
            reward = None
            if is_victry:
                vict_sum += 1
                reward = 10
            else:
                reward = -10
            
            gosa_sum = list()
            # q値の更新
            i = 0
            for q in memory:
                G = 0
                j = 0
                G = gamma ** (len(memory)-i)*reward
                td_gosa = (G - q.qvalue)
                gosa_sum.append(abs(td_gosa))
                q.qvalue += alpha *(td_gosa)
                i += 1
            # リセット
            memory = list()

            ### log系のしょり    
            episode_num +=1

            if episode_num % 50 == 0:
                results.append(vict_sum/50)
                vict_sum = 0
                gosa_results.append(sum(gosa_sum)/len(gosa_sum))
                gosa_sum = None
                gosa_sum = list()
            

            print("episode"+str(episode_num))
                
            if episode_num ==5000:
                #plot_graph(results)
                #plot_graph(gosa_results)
                print(gosa_results)

                

                with open('monte_results.csv', 'w') as f:
                    writer = csv.writer(f, lineterminator='\n')
                    writer.writerow(results)
                    writer.writerow(gosa_results)
                

if __name__ == '__main__':
    main()

