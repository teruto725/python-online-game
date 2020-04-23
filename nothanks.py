import random

class Nothanks():
    def __init__(self):
        self.initcoins = 25 #
        self.delcardnum =3 # num which is how 
        self.playercap = 3#limit of players num
        self.players = []#player name list
        self.fieldcard = 0# card on the field
        self.fieldcoins = 0 #coins puted on field card
        self.waiting_flg = True # whether player can enter or not

    def addPlayer(self,name):#add player
        if self.waiting_flg == False:
            return "Game was already started"
        self.players.append(Player(name,self.initcoins))
        if len(self.players) == self.playercap:
            self.waiting_flg = False
            return "Game start"
        return "You entered"

    def startGame(self):#gamestart
        if len(self.players) < 2:
            print("Error : Not enough players")
        else:
            self.tcon = TurnController(self.players)
            self.deck = Deck(self.delcardnum)#prepare
            self.fieldcard = self.deck.draw()#initial card

    def nextTurn(self):#go to next turn
        if self.deck.getInfo()["decknum"]==0:
            return "Game is end"
        else:
            nextplayer = self.tcon.getNextPlayer()#tebansusumeru       
            return nextplayer.name   

    def action(self,action,name):#player do action
        if self.tcon.getNowPlayer().name != name:
            return "Not your turn"
        if action == "pick":  
            player = self.tcon.getNowPlayer()
            player.pick(self.fieldcard,self.fieldcoins)
            self.fieldcoins = 0
            self.fieldcard = self.deck.draw()
            return "Pick is ok"
        elif action == "pass":
            player = self.tcon.getNowPlayer()
            self.fieldcoins += 1
            if (player.passTurn()== "No coin"):
                return "No coin"
            else:
                return "Pass is ok"
        else:
            return "Error of action's name"     

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
        if self.deck.getInfo()["decknum"] == 0:
            infodict["gamestatus"] = "finish"
        else :
            infodict["gamestatus"] = "ongoing"
        return infodict


class Deck():
    def __init__(self,delnum):
        self.cards = [i for i in range(3,36)]#山札は後ろから惹かれていく
        self.delcards = []

        for _ in range(3):
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

