# -*- coding:utf-8 -*-
import asyncio
import json
from nothanks import Nothanks
import time
import threading

class Lobby():#static class #all socket enter here firstly and can choice entering room
    sockets = []#private #sockets list
    rooms ={}#private # one room has one gamecontroller {"name":gcon}
    @staticmethod
    def add_game_nothanks_normal(name):#add game room nothanks
        gcon = GameController(Nothanks(),"normal")
        gcon.start()
        Lobby.rooms[name] = gcon
    
    @staticmethod
    def add_game_nothanks_learning(name,epoc_num):
        gcon = GameController(Nothanks(),"learning",epoc_num)
        gcon.start()
        Lobby.rooms[name] = gcon

    @staticmethod
    def get_rooms():#get room list
        li = []
        for k in Lobby.rooms.keys():
            li.append(k)
        return li

    @staticmethod
    def enter_lobby(socket):#generated socket use this methods difinitely
        Lobby.sockets.append(socket)
        socket.send(json.dumps({
            "type":"request_room_name_and_role",
            "payload":{"roomlist":Lobby.get_rooms()}
            }))

    @staticmethod
    def enter_room_as_viewer(roomname,socket):
        if roomname not in Lobby.rooms.keys():
            socket.send(json.dumps({
                    "type":"_room_name_and_role",
                    "payload":{"result_message":"Room of the name is not exist"}
            }))
        else:
            result = Lobby.rooms[roomname].add_viewer(Viewer(socket))
            socket.send(json.dumps({
                        "type":"_room_name_and_role",
                        "payload":{"result_message":result}
                        }))

    @staticmethod
    def enter_room_as_player(roomname,playername,socket):#go to game room
        if roomname not in Lobby.rooms.keys():
            socket.send(json.dumps({
                    "type":"_room_name_and_role",
                    "payload":{"result_message":"Room of the name is not exist"}
            }))
        else:
            result = Lobby.rooms[roomname].add_player(playername,socket)
            if result==False:
                socket.send(json.dumps({
                        "type":"result_room_name_and_role",
                        "payload":{"result":"declined","reason":"Room is already full"}
                        }))
            else:
                Lobby.sockets.remove(socket)
                socket.send(json.dumps({
                    "type":"result_room_name_and_role",
                    "payload":{"result":"accepted"}
                }))

    @staticmethod
    def game_end(gcon):#ロビーに戻ってくる
        for s in gcon.get_sockets_list():
            Lobby.enter_lobby(s)
        
        for k,v in Lobby.rooms.items():#遊んでた部屋の削除
            if v == gcon:
                Lobby.rooms.pop(k)
                if gcon.mode == "normal":
                    Lobby.add_game_nothanks_normal(k)
                if gcon.mode == "learning":
                    Lobby.add_game_nothanks_learning(k,gcon.epoc_num)


class GameController(threading.Thread):
    def __init__(self,game,mode,epoc_num=None):
        self.players =[]#paticipater
        self.viewers =[]
        self.game = game#gamemodule
        self.mode = mode
        self.epoc_num = epoc_num
        super(GameController, self).__init__()
    

    def add_player(self,name,socket):#if you can enter, return Ture or if not,return false
        result = self.game.addPlayer(name)
        if result == "You entered":
            self.players.append(Player(socket,name))
            return True
        if result == "Game start":
            self.players.append(Player(socket,name))
        else:#game was already started
            return result 

    def add_viewer(self,viewer):
        self.viewers.append(viewer)
        return "Add ok"
    #override
    def run(self):# wait since players come after that start game
        while True:
            if len(self.players) == self.game.playercap:
                if self.mode == "learning":
                    for epoc in range(1,self.epoc_num+1):
                        for p in self.players:
                            p.send_notice_epoc(epoc)
                        self.start_game()
                    break
                if self.mode == "normal":
                    self.start_game()
                    break
        Lobby.game_end(self)

    def start_game(self):#send start notice and info 
        print("gamestart")
        self.game.startGame()
        for p in self.players:
            p.send_notice_start(self.game.getInfo())
        for v in self.viewers:
            v.send_notice_start(self.game.getInfo())
        self.turn_flow()

    def turn_flow(self):#controll turn
        while True:
            for v in self.viewers:
                v.send_infomation_game(self.game.getInfo())
            turn_player = self.game.nextTurn()
            self.player_action(turn_player)
            gameinfo = self.game.getInfo()
            if gameinfo["end_flg"] == "True":
                for p in self.players:
                    p.send_notice_end(gameinfo) 
                for v in self.viewers:
                    v.send_notice_end(gameinfo)
                break

    def player_action(self,turn_player_name):#send requestaciton and wait reply after that do action and reply to cliant
        for p in self.players:
            if p.name == turn_player_name:
                p.send_request_action(self.game.getActionTypes(turn_player_name),self.game.getInfo())
                message=self.wait_message(p,"reply_action")
                action_result = self.game.action(message["payload"]["action_type"],p.name)
                result = "accepted"
                reason = ""
                if action_result != "Ok":
                    result = "declined"
                    reason = action_result
                p.send_result_action(result,reason,self.game.getInfo())

    def wait_message(self,p,type_str):# wait message change to anticipated type_str
        timecon = 0
        while True:
            timecon += 1
            message = p.socket.pop_message()
            if message["type"] == type_str:
                return message
            if timecon > 10**4:
                print("TLE")
                break
            time.sleep(0.001)

    def get_sockets_list(self):# for Lobby.end_game()
        slist =  [p.socket for p in self.players]
        slist.extend([v.socket for v in self.viewers])
        return slist
class Player():#plyer classs
    def __init__(self,socket,name):
        self.socket = socket
        self.name = name

    def send_request_action(self,action_types,info):
        self.message = {"type":"no_message","payload":None}
        self.socket.send(json.dumps({
            "type":"request_action",
            "payload":{"action_types":action_types,"game_status":info}
            }))
    
    def send_result_action(self,result,reason,info):
        self.socket.send(json.dumps({
            "type":"result_action",
            "payload":{"result":result,"reason":reason,"game_status":info}
        }))

    def send_notice_start(self,info):
        self.socket.send(json.dumps({
            "type":"notice_start",
            "payload":{"game_status":info}
            }))

    def send_infomation_game(self,info):
        self.socket.send(json.dumps({
            "type":"infomation_game",
            "payload":{"game_status":info}
            }))
    
    def send_notice_end(self,info):
        self.socket.send(json.dumps({
            "type":"notice_end",
            "payload":{"game_status":info}
            }))

    def send_notice_epoc(self,epoc):
        self.socket.send(json.dumps({
            "type":"notice_epoc",
            "payload":{"epoc_num":epoc}
            }))

class Viewer():
    def __init__(self,socket):
        self.socket = socket
    
    def send_notice_start(self,info):
        self.socket.send(json.dumps({
            "type":"notice_start",
            "payload":{"game_status":info}
            }))
    def send_infomation_game(self,info):
        self.socket.send(json.dumps({
            "type":"information_game",
            "payload":{"game_status":info}
            }))
    def send_notice_end(self,info):
        self.socket.send(json.dumps({
            "type":"notice_end",
            "payload":{"game_status":info}
            }))

class Socket(asyncio.Protocol):#gconとcmserverにsendとdatareceivedを渡すクラス
    def __init__(self):
        self.message =""
    
    def connection_made(self, transport):
        self.transport = transport
        self.addr, self.port = self.transport.get_extra_info('peername')
        self.id = "{}:{}".format(self.addr, self.port)
        self.send(json.dumps({
            "type":"notice_connection_ok",
            "payload":{}
            }))
        self.message =""
        Lobby.enter_lobby(self)
        
    def send(self,data):#data is str
        #print(data)
        b = (data + "\n").encode()
        self.transport.write(b)
    
    def pop_message(self):
        m  = self.message
        self.message={"type":"no_message","payload":None} 
        return m

    def data_received(self,data):
        #print("data received")
        s = self.byte_to_str(data)
        for r in s:
            if len(r) == 0:
                continue
            r = json.loads(r.strip())
            self.message = r
        #print(self.message)
        if self.message["type"] == "reply_room_name_and_role":
            if self.message["payload"]["role"] == "viewer":
                Lobby.enter_room_as_viewer(self.message["payload"]["room_name"],self)
            if self.message["payload"]["role"] == "player":
                Lobby.enter_room_as_player(self.message["payload"]["room_name"],self.message["payload"]["player_name"],self)
            self.message = {"type":"no_message","payload":None}
 
    def byte_to_str(self,b):
        if type(b) == "str":
            return b.split("\n")
        else:
            return b.decode().split("\n")
        

def main():
    host = "localhost" #お使いのサーバーのホスト名を入れます
    port = 1000 #クライアントで設定したPORTと同じもの指定してあげます
    
    Lobby.add_game_nothanks_normal("normal")#一回ゲームするだけのルーム
    Lobby.add_game_nothanks_learning("learning",10000)#指定回数ゲームする学習用のルーム
    '''
    好きなroom追加してね
    '''
    ev_loop = asyncio.get_event_loop()
    factory = ev_loop.create_server(Socket, host, port)
    server = ev_loop.run_until_complete(factory)

    try:
        ev_loop.run_forever()
    finally:
        server.close()
        ev_loop.run_until_complete(server.wait_closed())
        ev_loop.close()


if __name__ == '__main__':
    main()
