import random

class Nothanks():
    def __init__(self):
        self.initcoins = 3 #
        self.delcardnum =0 # num which is how 
        self.playercap = 2#limit of players num
        self.players = []#player name list
        self.fieldcard = 0# card on the field
        self.fieldcoins = 0 #coins puted on field card
        self.waiting_flg = True # whether player can enter or not
        self.end_flg = False
    def addPlayer(self,name):#add player
        if self.waiting_flg == False:
            return "Game was already started"
        self.players.append(Player(name,self.initcoins))
        if len(self.players) == self.playercap:
            self.waiting_flg = False
            return "Game start"
        return "You entered"

    def startGame(self):#gamestart ( init all parameters)
        if len(self.players) < 2:
            print("Error : Not enough players")
        else:
            self.end_flg = False
            for i in range(len(self.players)):
                self.players[i] = Player(self.players[i].name,self.initcoins)
            self.tcon = TurnController(self.players)
            self.deck = Deck(self.delcardnum)#prepare
            self.fieldcard = self.deck.draw()#initial card

    def nextTurn(self):#go to next turn
        nextplayer = self.tcon.getNextPlayer()#tebansusumeru       
        return nextplayer.name   

    def getActionTypes(self,player):
        for p in self.players:
            if p.name == player:
                if p.coins == 0:
                    return ["pick"]
                else:
                    return ["pick","pass"]
    
    def action(self,action,name):#player do action
        if self.tcon.getNowPlayer().name != name:
            return "Not your turn"
        if action == "pick":  
            player = self.tcon.getNowPlayer()
            player.pick(self.fieldcard,self.fieldcoins)
            self.fieldcoins = 0
            result = self.deck.draw()
            if str(result) == "No cards":
                self.end_flg = True
                self.fieldcard = None
            else :
                self.fieldcard = result
            return "Ok"
        elif action == "pass":
            player = self.tcon.getNowPlayer()
            self.fieldcoins += 1
            if (player.passTurn()== "No coin"):
                return "You can't pass because of no coin"
            else:
                return "Ok"
        else:
            return "Action_type is wrong"     

    def getInfo(self):#辞書型でゲーム情報返す 
        infodict ={}
        infodict["turnnum"] = self.tcon.getTurn()
        infodict["turnorder"] = [player.name for player in self.tcon.getTurnOrder()]
        infodict["rankingorder"] = [player.name for player in sorted(self.players)]
        infodict["playerinfo"] = {}
        for player in self.players:
            infodict["playerinfo"][player.name] = player.getInfo()
        infodict["deckinfo"] = self.deck.getInfo()
        infodict["fieldinfo"] = {"fieldcard":self.fieldcard,"fieldcoins":self.fieldcoins}
        infodict["end_flg"] = str(self.end_flg)
        return infodict


class Deck():
    def __init__(self,delnum):
        self.cards = [i for i in range(1,6)]#山札は後ろから惹かれていく
        self.delcards = []
        
        for _ in range(delnum):
            self.delcards.append(self.cards.pop(int(random.uniform(0,len(self.cards)))))
        random.shuffle(self.cards)
        
    def draw(self):#draw one card
        if len(self.cards) == 0:#number of cards is zero
            return "No cards"
        return self.cards.pop(-1)

    def getInfo(self):
        deckinfo ={}
        deckinfo["decknum"] = len(self.cards)
        return deckinfo


class TurnController():
    def __init__(self,players):
        self.turn = -1#ずれているので注意getTurnを利用すること
        self.players = players
    
    def getNextPlayer(self):#次の手番の人を返す
        self.turn +=1
        return self.players[self.turn%len(self.players)]
    
    def getNowPlayer(self):
        return self.players[self.turn%len(self.players)]
    
    def getTurnOrder(self):
        order = self.players[self.turn%len(self.players):]
        if self.turn%len(self.players) != 0:
            order.extend(self.players[0:self.turn%len(self.players)])
        return order
    
    def getTurn(self):
        return self.turn +1


class Player():
    def __init__(self,name,coins):
        self.name = name
        self.coins = coins
        self.cards = [] #hands cards

    def __lt__(self,other):
        return self.calcPoint()<other.calcPoint()

    def calcPoint(self):
        if len(self.cards) ==0:
            return 0-self.coins
        ans = self.cards[0]
        for i in range(len(self.cards)-1):
            if self.cards[i+1] - self.cards[i] != 1:
                ans += self.cards[i+1]
        return ans-self.coins 

    def pick(self,fieldcard,fieldcoins):#pick card
        self.cards.append(fieldcard)
        self.coins += fieldcoins
        self.cards.sort()


    def passTurn(self):
        if self.coins == 0:
            return "No coin"
        else:
            self.coins -= 1
            return "OK"

    def getInfo(self):
        playerinfo = {}
        playerinfo["coins"]=self.coins
        playerinfo["cards"]=self.cards
        playerinfo["point"]=self.calcPoint()
        return playerinfo

