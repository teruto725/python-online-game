import random as rd

class Nothanks:
    self.players = []
    self.coins = 25
    self.tcon
    self.dec#デッキ
    self.fieldcard = 0
    self.fieldcoin = 0
    def add_player(name):#add player
        players.append(Player(name,coins))
        return ("add player"+players[-1].name)

    def startgame():#gamestart
        if len(players) < 2:
            return "players are not enougth"
        else:
            tcon = TurnController(players)
            self.dec = Dec()#prepare
            self.fieldcard = dec.draw()#initial card
            return "game start"

    def nextTurn():#go to next turn
        tcon.getNextPlayer()#tebansusumeru 
        if dec.draw == "no cards":
            return "game is end"
        else:
            fieldcard = dec.draw()
            return "next turn ok"
    
    def action(action):#player do action
        if action == "pick":
            player.pick(fieldcard)
            return "pick is ok"
        elif action == "pass":
            player.passTurn()
            return True

    def getInfo():#jsonでゲーム情報全部返す
        pass
    


class TurnController:
    self.count = -1
    self.players = 0:
    def __init__(self,players):
        self.players =players
    def getNextPlayer():#次の手番の人を返す
        count +=1
        return players[count%len(players)]


class Deck:
    self.cards = [i for i in range(3,36)]
    self.delcards = []
    def __init__(self):
        for _ in range(3):
            delcards.append(cards.pop(rd.uniform(0,len(cards))))
            self.cards = rd.shuffle(cards)

    def draw(self):#draw one card
        if len(cards) == 0:#number of cards is zero
            return "no cards"
        return cards.pop(-1)


class Player:
    self.name = ""
    self.coins = 0
    self.cards = 0 #hands cards
    def __init__(self,name,coins):
        self.name = name
        self.cards = coins

    def calcPoint():
        if len(cards) ==0:
            return 0
        ans = cards[0]
        for i in range(len(cards)-1):
            if cards[i+1] - cards[i] != 1:
                ans += cards[i+1]
        return ans 



    def pick(fieldcard,fieldcoin):#pick card
        cards.add(fieldcard)
        coins.add(fieldcoin)
        cards.sort()

    def passTurn():
        coins -= 1


