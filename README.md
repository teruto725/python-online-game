# BoardCoder
## 概要
サーバで実行されるボードゲームに、各clientがplayerとしてアクセスし、それぞれのアルゴリズムによって勝敗を競う。  
またviewerも接続可能でありGUIによる観戦が可能である。  
ゲームはLobbyに一定数存在しておりroomに参加することでゲームをプレイすることが可能である。 ルームには以下のモードが存在する。
1. normal:普通に一ゲームプレイする
1. learning:学習用のroomであり一定数のゲームを繰り返し同じ参加者でプレイする  


大まかなゲームの流れを説明する。 
1. 接続後clientはLobbyにて待機状態となる。
1. clientはLobbyに存在する任意のroomを選択し参加する。この時、viewerとして参加するかplayerとして参加するかを選択可能である。
1. 参加者が集まり次第ゲームが開始される。
1. ゲームが終了するとゲームに参加していたclientはすべてLobbyにて待機状態に戻りゲームが初期化される。
## 動作環境
- server:python 3.7  
- 通信:socket通信  


## パケット一覧  
すべてのパケットはJson形式であり、{"type":"","payload":{------}}の形をとる。documentsにシーケンス図入ってるんで参考にしてください
- {"type":"notice_connection_ok","payload":{Null}}
    - server→all client
    - serverがアクセスしてきたclientに対してアクセス成功の通知を返す
- {"type":"request_room_name_and_role","payload":"roomlist":[]}
    - server→all client
    - どの部屋にどの役割で入るかを問う
    - roomlist:ルームの名前のリスト
- {"type":"reply_room_name_and_role","payload":{"room_name":"","role":"","player_name":""}}
    - client→server
    - request_room_name_and_roleの返答パケット
    - room_name:部屋名
    - role:役割名（player or viewer)
    - playername:player名（playerの時だけ）
- {"type":"result_room_name_and_role","payload":{"result":"","reason":""}}
    - server→client
    - reply_room_name_and_roleの返答パケット
    - result:reply_room_name_and_roleの結果（accepted or declined）
    - reason: declinedされたときの理由

- {"type":"notice_start","payload":{"game_status":{}}}
    - server→allviewer server→allplayer
    - playerがそろったときに登録されているすべてのviewer,playerにゲームスタートを通知する
    - game_status:ゲームの状態を表す辞書。いかにkey一覧を示す
        - turnnum: 現在のターン数 int 初期状態は0
        - turnorder: ターンの順番 list(str) ["次のplayer名","その次のplayer名,"その次の---]
        - rankingoder: 現在の順位 list(str) ["一位のplayer名","二位のplayer名","三位の---]
        - playerinfo: player情報の辞書。keyは任意のplayer名が入る。valueにそのplayerの情報が格納された辞書がある. 
            - coins:所持コイン数 int
            - cards:所持カードのlist(int) 昇順にソートされている
            - points:現在のポイントint マイナス値もとる
        - deckinfo: deck(山札)情報の辞書、keyを以下に示す
            - decknum: deckの残り枚数 int X~0の値をとる
        - fieldinfo: フィールド（ボード上）の情報の辞書　keyを以下に示す
            - fieldcard: フィールド上に現在出ているカードの数字 int 
            - fieldcoins: カードの上に乗っているコインの枚数 int 
        - end_flg 
    - 例： {'game_status': {'turnnum': 11, 'turnorder': ['p2', 'p3', 'p1'], 'rankingorder': ['p1', 'p3', 'p2'], 'playerinfo': {'p1': {'coins': 25, 'cards': [28, 29, 30, 31], 'point': 3}, 'p2': {'coins': 25, 'cards': [16, 18, 24, 35], 'point': 68}, 'p3': {'coins': 25, 'cards': [9, 14, 33], 'point': 31}}, 'deckinfo': {'decknum': 18}, 'fieldinfo': {'fieldcard': 11, 'fieldcoins': 0}, 'gamestatus': 'ongoing'}}
- {"type":"information_game":"payload":{"game_status":{}}}
    - server→allviewer
    - ターンの初めにターンの情報を送る
    - game_status:上と同様
- {"type":"request_action","payload":{"action_types":[],"game_status":{}}}
    - server→allplayer
    - 手番が回ってきたplayerに対して送られる
    - action_types:playerがとれるアクションの選択肢 list(str)
    - game_status:上と同様
- {"type":"reply_action",{"action_type":""}}
    - player→server
    - request_actionの返信パケットでアクション内容を返す
    - action_type:選択した行動を返す。　str
- {"type":"result_action",{"result":"","reason":"","game_status":{}}}
    - server→player
    - reply_actionの返信パケットでアクション後の結果を返す
    - result: 正しくアクション出来たか(acceped or declined)
    - reason: declinedされたときのエラーメッセージ
    - game_status: 上と同様
- {"type":"notice_end","payload":{"game_status":{}}
    - server→client
    - game_status: 上と同様
- {"type":"notice_epoc","payload":{"epoc_num":}}
    - server→client
    - learningモードの時のみ送られる。エポックが終了した通知
    - epoc_num: エポック数 int

## ボードゲーム説明
### Nothanks!
正式にはゲシェンクっていうらしい。
- 勝利条件 ポイントが一番少ない人が勝ち
- ターン制ゲーム
#### ゲームの流れ
1. 3~36の数字が書かれたカードで構成された山札から3つのカード抜き、残ったカードをシャッフルし山札としてセットする（抜いたカードは見れない）
1. すべてのplayerに25コインが配られる
1. 山札から一枚めくって場におく
1. ターンプレイヤーは以下の2ついづれかの行動を選択する
    - pick: 場のカード並びに場のコインをすべて手持ちに加え新たに山札から一枚めくり場に置く（手持ちに加えたコインも初期のコインと同様にpassで使用することができる）
    - pass: カードをとらない代わりに手持ちのコインを場に一枚だす(手持ちのコインがない場合は選択不可)
2. ターンが次の人にうつる。
2. 4と5を山札からカードが引けなくなるまで繰り返す。
1. ポイントが一番少ない人の勝利

#### ポイントの計算方法
- ポイント＝所持カードの合計 - 所持コイン枚数
- ただし所持カードの一部が連番であるときは、連番部分の一番小さいカード以外はないものとして扱うことができる。
    - 例1: 所持カードが3,5,7の時、所持カードの合計は3+5+7=15
    - 例2: 所持カードが3,4,5の時、所持カードの合計は3
    - 例3: 所持カードが3,4,6,7,8,9の時、所持カードの合計は3+6=9


## demo  
1. server.pyを起動  
1. client_viewer.pyを3つ起動し適切なroomnameを選択
1. client_player.pyを3つ起動し適切なroomname並びにplayernameを入力





