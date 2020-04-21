# -*- coding:utf-8 -*-
import asyncio
import json
from nothanks import Nothanks
import time


class GameController():
    def __init__(self,game):
        self.players =[]#paticipater
        self.game = game#gamemodule

    def add_player(self,name,socket):#if you can enter, return Ture or if not,return false
        result = self.game.addPlayer(name)
        if result == "You entered":
            self.players.append(Player(socket,name))
            return True

        if result == "Game start":
            self.players.append(Player(socket,name))
            self.start_game()
            
        else:
            return result 

    def start_game(self):#send start notice and info 
        print("gamestart")
        self.game.startGame()
        info = self.game.getInfo()
        for p in self.players:
            p.send_notice_start()
            p.send_infomation_game(info)
        self.turn_flow()
    
    def turn_flow(self):#controll turn
        while True:
            turn_player = self.game.nextTurn()
            self.player_action(turn_player)
            gameinfo = self.game.getInfo()
            if gameinfo["gamestatus"] == "finish":
                for p in self.players:
                    p.send_notice_end()
                    Lobby.game_end(self)
                    break
            else:
                for p in self.players:
                    p.send_infomation_game()
            
            
    def player_action(self,turn_player_name):#send requestaciton and wait reply after that do action and reply to cliant
        for p in self.players:
            if p.name == turn_player_name:
                p.request_action(self.game.getInfo())
                message=self.wait_message(p,"reply_action")
                result = self.game.action(message["payload"]["action_type"],p.name)
                p.send_reply_action(result)

    def wait_message(self,p,type_str):# wait message change to anticipated type_str
        timecon = 0
        while True:
            timecon += 1
            if p.message["type"] == type_str:
                return p.message
            if timecon > 10**6:
                print("TLE")
                break
            time.sleep(0.001)

    def get_sockets_list(self):# for Lobby.end_game()
        Lobby.game_end(self)
        return [p.socket for p in self.players]


class Lobby():#static class #all socket enter here firstly and can choice entering room
    sockets = []#private #sockets list
    rooms ={}#private # one room has one gamecontroller {"name":gcon}
    @staticmethod
    def add_game_nothanks(name):#add game room nothanks
        Lobby.rooms[name] = GameController(Nothanks())
    
    @staticmethod
    def get_rooms():#get room list
        s = ""
        for k in Lobby.rooms.keys():
            s += (k+":")
        return s

    @staticmethod
    def enter_lobby(socket):#generated socket use this methods difinitely
        Lobby.sockets.append(socket)
        socket.send(json.dumps({
            "type":"request_room_name",
            "payload":{"roomlist":Lobby.get_rooms()
            }}))

    @staticmethod
    def enter_room(roomname,playername,socket):#go to game room
        result = Lobby.rooms[roomname].add_player(playername,socket)
        if result==False:
            return "Room is full"
        else:
            Lobby.sockets.remove(socket)
            return "You entered " +roomname 

    @staticmethod
    def game_end(gcon):#ロビーに戻ってくる
        Lobby.sockets.extend(gcon.get_sockets_list())
        Lobby.sockets.pop(gcon)#ゲーム削除
        

class Player():#plyer classs
    def __init__(self,socket,name):
        self.socket = socket
        self.message = self.socket.message # this is the message from client
        self.name = name

    def request_action(self,info):
        self.message = {"type":"no_message","payload":None}
        self.socket.send(json.dumps({
            "type":"request_action",
            "payload":info
            }))
    
    def send_reply_action(self,result):
        self.socket.send(json.dumps({
            "type":"result_action",
            "payload":{"result":result}
        }))

    def send_notice_start(self):
        self.socket.send(json.dumps({
            "type":"notice_start",
            "payload":{}
            }))

    def send_infomation_game(self,info):
        self.socket.send(json.dumps({
            "type":"infomation_game",
            "payload":info
            }))
    
    def send_notice_end(self):
        self.socket.send(json.dumps({
            "type":"notice_start",
            "payload":{}
            }))
    



class Socket(asyncio.Protocol):#gconとcmserverにsendとdatareceivedを渡すクラス
    
    def __init__(self):
        self.message =""
    
    def connection_made(self, transport):
        self.transport = transport
        self.addr, self.port = self.transport.get_extra_info('peername')
        self.id = "{}:{}".format(self.addr, self.port)
        self.send("Connection is OK")
        self.message =""
        Lobby.enter_lobby(self)
        
    
    def send(self,data):#data is str
        print(data)
        b = (data + "\n").encode()
        self.transport.write(b)
    
    def data_received(self,data):
        print("data received")
        s = self.byte_to_str(data)
        for r in s:
            if len(r) == 0:
                continue
            r = json.loads(r.strip())
            self.message = r
            
        if self.message["type"] == "reply_room_name":
            result = Lobby.enter_room(self.message["payload"]["room_name"],self.message["payload"]["player_name"],self)    
            self.message =  {"type":"no_message","payload":"None"}
            self.send(json.dumps({
                "type":"result_room_name",
                "payload":{"result_message":result}
                }))
            


    def byte_to_str(self,b):
        if type(b) == "str":
            return b.split("\n")
        else:
            return b.decode().split("\n")
        

def main():
    host = "localhost" #お使いのサーバーのホスト名を入れます
    port = 1000 #クライアントで設定したPORTと同じもの指定してあげます
    Lobby.add_game_nothanks("room1")
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
