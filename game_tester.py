import nothanks as nt
import random 
import time
game = nt.Nothanks()
plist = ["p1","p2","p3"]
for name in plist:
    game.addPlayer(name)
game.startGame()
while True:
    nextplayer = game.nextTurn()

    gameinfo=game.getInfo()
    print(" ")
    print("-------ターン"+str(gameinfo["turnnum"])+"---------")
    print(str(gameinfo["fieldinfo"]))
    print(nextplayer+"のターン:pass or pick")
    action = input()
    game.action(action,nextplayer)
    gameinfo = game.getInfo()
    
    if gameinfo["gamestatus"] == "finish":
        print("endgame")
        print(gameinfo["rankingorder"])
        break
    else:
        print("------player情報-----------")
        print(gameinfo)
        '''
        for name in plist:
            pinfo = gameinfo["playerinfo"][name]
            print(name+str(pinfo))
        '''