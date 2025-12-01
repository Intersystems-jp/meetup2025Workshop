# 🐟RAG + 生成 AI であそぼう！🐟

RAG + 生成 AI であそぼう！のコーナーでは、以下内容について、具体的にどう実装しているの？を確認できます。

![](../assets/3.RAG-Overview.jpg)

それでは早速、サンプルの Notebook を Colab で開き、一連の流れを 1 つずつ確認してみましょう！

サンプルコード：[RAGAsobo.ipynb](/3.RAG/RAGAsobo.ipynb) を
ご自身の Google ドライブにコピーしてから進めてください。

## 🎣時間に余裕がある場合：REST API を作って動かしてみる

Colab での体験の後で時間に余裕がある場合、よろしければ以下もご体験ください。

- 🎣**お勧めの方法🐟：Flask**

  Flask アプリケーションを実行しながら確認されたい方は、ローカルの環境で Flask アプリを開始しながら進められるサンプルを用意しています。具体的な手順は [Flask アプリで動かしてみる](#flask-アプリで動かしてみる) をご参照ください。

- ObjectScript の REST ディスパッチクラス

  IRIS の REST ディスパッチクラスで作成される方は、ワークショップで接続先に使用している IRIS にクラス定義を作成しながら進めていただきます。
  
  具体的な手順は [REST ディスパッチクラスで動かしてみる](#rest-ディスパッチクラスで動かしてみる) をご参照ください。


## 🎣Flask アプリで動かしてみる🐟

事前準備としてローカルの環境に、ワークショップの実行で必要な Python パッケージを仮想環境にインストールしてください。

まずは、本日のサンプル一式をダウンロード、または git clone します。

```
git clone https://github.com/Intersystems-jp/meetup2025Workshop.git
```
ダウンロードして展開したディレクトリ、または　git clone で作成されたディレクトリに移動後、以下コマンドを実行し Python の仮想環境を用意します。

```
# 任意の名前(ここではfishenv)で環境を作成する
python -m venv fishenv

# 仮想環境を有効化する
fishenv\Scripts\activate     # Windows の場合
source fishenv/bin/activate  # macOS/Linux の場合

# PIPで必要なライブラリをインストールする

# (参考)仮想環境を終了するには
deactivate
```

インストールするパッケージは、[requirements.txt](../0.Prep/requirements.txt) にあります。

現在、サンプル一式が含まれる `meetup2025Workshop` に移動しているとします。

requirements.txt のあるディレクトリに移動した後、以下実行します（0.Prep/requirements.txt にあります）。

```
cd 0.Prep
pip install -r requirements.txt
```

[3.RAG](../3.RAG/) の Flask アプリ完成版は、[fishapp-part2-compelteVer.py](../3.RAG/flask/fishapp-part2-completeVer.py) をご利用ください。

手順に沿って進める場合は、[fishapp-part2.py](../3.RAG/flask/fishapp-part2.py) を使用します。

<br><br>
では早速、具体的な内容に入りましょう！

---
[3.RAG/flask/fishapp-part2.py](../3.RAG/flask/fishapp-part2.py) に必要なコードを追記しながら進めてきます。

- [(1)Flaskアプリを動かしてみる](#1flaskアプリを動かしてみる)
- [(2)Flaskアプリで魚の画像から魚名が得られるか試してみる](#2flaskアプリで魚の画像から魚名が得られるか試してみる)
- [(3)Flaskアプリで生成 AI に渡す補足情報を追加してみる](#3flaskアプリで生成-ai-に渡す補足情報を追加してみる)

<br>
その他のファイルは以下の用途で利用します(<span style="color: orange">※が付いているファイルはワークショップでは未使用です</span>)。

ファイル名|用途
--|--
fishapp-part2-completeVer.py|ワークショップ完成形
<span style="color: orange">config.py　※</span>|OpenAIを使う場合のAPIキー登録用ファイル（ワークショップでは未使用）
fishapp-part2.py|ローカルでお試しいただく場合のファイル
cliputil.py|fishapp-part2.pyでインポートするファイル（ローカルお試し用）
---

### (1)Flaskアプリを動かしてみる

Flaskアプリは、5100番ポートで動くように記載しています。

```
if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True,port=5100)
```

ワークショップのサンプル用ディレクトリ：meetup2025Workshop 以下[3.RAG/flask](/3.RAG/flask/) に移動し、`fishapp-part2.py` を実行します。

> 実行する環境に合わせ、移動するディレクトリのパスをご変更ください。また、スクリプトファイル実行時の指定も環境に合わせ実行してください（`python3` または `python`）。

```
cd meetup2025Workshop/3.RAG/flask/
python3 fishapp-part2.py
```

以下、ブラウザで実行します。

http://localhost:5100/


**Hello FishDetector!** 　と表示されましたか？

表示されない方は、VSCode のターミナルにエラーなどが表示されていないかどうかご確認ください。

表示された方は、次に進みましょう！🐟

### (2)Flaskアプリで魚の画像から魚名が得られるか試してみる

🐟の画像から魚名を調べるため、ベクトル検索を動かしてみましょう！

[fishapp-part2.py](../3.RAG/flask/fishapp-part2.py) に画像ファイルアップロード用のPOST要求のパス：/upload　のコードが記載されています。

コードの中では、fish と名付けたフォームデータ名で画像ファイルの中身が送られると、`UPLOAD_FOLDER`で指定されたフォルダに画像ファイルが保存され、その後ベクトル検索で画像から魚名を取得し、応答 JSON を返します。

```
# ------------------------------------------
# /upload エンドポイント
# ------------------------------------------
@app.route('/upload',methods=['POST'])
def upload():
    try:
        # 書き込みテスト（事前にディレクトリ書き込み可能かチェック）
        if not os.access(UPLOAD_FOLDER, os.W_OK):
            return Response({"error": f"書き込み権限がありません: {UPLOAD_FOLDER}"}, status=403,content_type='application/json; charset=utf-8')

        #画像ファイルを指定ディレクトリにUpload
        file = request.files['fish']
        filefullpath=os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filefullpath)
    except PermissionError:
        return Response({"error": f"ファイル保存時に権限エラーが発生しました: {filefullpath}"}, status=403,content_type='application/json; charset=utf-8')

    except Exception as e:
        return Response({"error": f"ファイル保存に失敗しました: {e}"}, status=500,content_type='application/json; charset=utf-8')

    conn = get_conn()
    embed=cliputil.get_image_embeddings(filefullpath)
    sql="select top 1 FishID,Name,VECTOR_COSINE(Features, TO_VECTOR(:embed, DOUBLE, 512)) as cos from MeetUp2025.Fish ORDER BY cos desc"
    rs=conn.execute(text(sql),{"embed":embed})
    fishinfo=next(rs)

    #回答のJSONを作成
    ans= json.dumps({"FishID":fishinfo[0],"FishName":fishinfo[1]},ensure_ascii=False)
    return Response(ans, content_type='application/json; charset=utf-8')
```

現在、fishapp-part2.py 15行目の　`UPLOAD_FOLDER` には、以下のディレクトリがデフォルトで指定されています。
```
#UPLOAD用フォルダ
#！🐟環境に合わせて変更してください🐟！
UPLOAD_FOLDER = "/home/ubuntu/test/meetup2025Workshop/3.RAG/flask/upload"
```
現在ご利用中ディレクトリ([3.RAG/flask](../3.RAG/flask/))以下の upload に変更します。

> メモ：Windows の場合は、`\`　の前にエスケープが必要になります。例えば、`c:\workspace\aaa` の場合は、`c:\\workspace\\aaa` のように記入してください。

変更が完了したら保存します（Ctrl+S）。

Flask アプリから IRIS への接続には、sqlalchemy を利用しています。具体的な接続文字列や接続オブジェクトの作成については、fishapp-part2.py の initial()、get_conn() に記述しています。

```
def initial():
    global engine
    if engine is None:
        engine = create_engine("iris://meetup2025:meetup2025@20.78.1.189:1972/USER",echo=True, future=True)

def get_conn():
    #各リクエストで接続を取得
    if 'conn' not in g:
        g.conn = engine.connect()
    return g.conn
```

get_conn()関数を実行すると、接続オブジェクトが戻るように作っています。

この接続オブジェクトを利用し、画像ファイルの Embedding を取得した後、MeetUp2025.Fish の Name に対する Embedding が格納されている Features とのコサイン類似度を求め、最も類似するレコードを1件取得しています（upload()のところ）。

```
    conn = get_conn()
    #画像ファイルのEmbedding
    embed=cliputil.get_image_embeddings(filefullpath)
    #ベクトル検索
    sql="select top 1 FishID,Name,VECTOR_COSINE(Features, TO_VECTOR(:embed, DOUBLE, 512)) as cos from MeetUp2025.Fish ORDER BY cos desc"
    rs=conn.execute(text(sql),{"embed":embed})
    fishinfo=next(rs)
```

ベクトル検索の引数には画像の Embedding が必要になるため、事前に用意してある [cliputils.py](../3.RAG/flask/cliputil.py) の Embedding 用関数：get_image_embeddings() を使用しています。実行時の引数には、画像ファイルのフルパスを渡しています。

検索結果は、FishID と Name が JSON で返送される予定ですので、さっそく試してみましょう！

※ URL のポート番号は fishapp-part2.py に指定したポート番号に変更してから実行してください。

URL|Method|Header名|Headerの値
--|--|--|--
http://localhost:5100/upload|POST|Content-Type|multipart/form-data

Body には以下設定します。
Key|値
--|--
fish（小文字で指定します）|画像ファイル

以下、REST クライアントからの実行例です。**※IPアドレスは localhost に読み替えてください**

![](../assets/3.RAG-Upload-postman.jpg)

応答例：
```
{
    "FishID": "f094",
    "FishName": "ヒラスズキ"
}
```

REST クライアントをお持ちでない方は、[Chrome の拡張機能](#chrome-の拡張機能の場合)、または [curlコマンド](#curl-コマンドの場合)でお試しいただけます。

#### Chrome の拡張機能の場合
Chrome を開き、[Talend API Tester - Free Edition](https://chromewebstore.google.com/detail/talend-api-tester-free-ed/aejoelaoggembcahagimdiliamlcdmfm?hl=ja) に移動し、画面右上の [Chrome に追加] ボタンで追加できます。

画面を開いたら、後は上記指定の通り入力します（画像ファイルはローカルのファイルを選択できます）。

![](../assets/3.RAG-TalendAPI-Open.jpg)

画面を開いたらリクエストに必要な情報を入力し、Send ボタンをクリックします。**※IPアドレスは localhost に読み替えてください**

![](../assets/3.RAG-TalendAPI-Upload.jpg)


#### curl コマンドの場合

- Windows の場合

  コマンドプロンプトを開き、以下実行します。

  例は、**c:\temp\test**以下にアップロード対象ファイル（tachiuo.jpg）が存在している場合の例です。任意のディレクトリやファイル名に変更してから実行してください。

  ```
  curl.exe -X POST -F "fish=@C:\temp\test\tachiuo.jpg" http://localhost:5100/upload
  ```


- Linux 系の場合

  ターミナルを開き以下実行します。

  例は、**/home/ubuntu/IIJ/meetup2025Workshop/3.RAG** 以下にアップロード対象ファイル（tachiuo.jpg）が存在している場合の例です。任意のディレクトリやファイル名に変更してから実行してください。

  ```
  curl -X POST -F "fish=@/home/ubuntu/IIJ/meetup2025Workshop/3.RAG/tachiuo.jpg" http://localhost:5100/upload
  ```

<br><br>

ベクトル検索で得られた魚名をこの後の流れで利用します。

次はいよいよ、生成 AI へのレシピ生成依頼です。



### (3)Flaskアプリで生成 AI に渡す補足情報を追加してみる

[fishapp-part2.py](../3.RAG/flask/fishapp-part2.py) には、生成 AI にレシピ生成を依頼する関数 getrecipe() が途中まで用意されています。

```
# ------------------------------------------
# /recipe　ローカル LLMにレシピ生成を依頼
# Bodyの中身
#  {
#  "UserInput":"ここにユーザが希望するレシピの内容",
#  "FishName":"魚名"
#  "FishID":"f001"
#  }
#
# 魚名をキーに生成AIに渡す独自データをデータベースから入手
# 独自データ＝その釣り場の潮位情報と釣果データ（デモでは釣り場は固定値を置いています）
# ------------------------------------------
@app.route('/recipe',methods=['POST'])
def getrecipe():
    body = request.get_json()
    #潮位情報、釣果情報を入手するため、POST要求で入力されたJSONのFishIDを取得し、get_fishinfo()を実行します。
    fishinfo=get_fishinfo(body["FishID"])
      :
      ＜省略＞
```

今回は、[(2)Flaskアプリで魚の画像から魚名が得られるか試してみる](#2flaskアプリで魚の画像から魚名が得られるか試してみる) の流れで特定した魚名、魚ID から、生成 AI にレシピ生成を依頼するときに追加する釣り場オリジナル情報として、データベースから釣り場の潮位情報と釣果情報を入手予定です。

釣り場の潮位情報、釣果情報は、[fishapp-part2.py](../3.RAG/flask/fishapp-part2.py) の関数 get_fishinfo(fishid) で取得できるようにしています（引数：FishID、戻り値：文字列）。

生成AIに渡すプロンプトの部分が歯抜け状態になっていますので、得られた情報をシステムプロンプトとユーザプロンプトの `content` に設定し、実行し、釣った地元にあったレシピが返送されるか確認してみてください。

回答例は [fishapp-completeVer.py](../3.RAG/flask/fishapp-completeVer.py)にあります。

パス|ヘッダ名|値|Body指定例
--|--|--|--
/recipe|Content-Type|application/json;charset=utf-8|{<br>"FishID": "f010",<br>"FishName": "タチウオ",<br>"UserInput": "地元レシピを教えてください"<br>}

> 💡木更津沖でよく釣れるさかな

FishID|FishName
--|--
f001|マアジ
f002|サバ
f005|カレイ
f007|鯛
f025|スズキ

<br>

実行例（REST クライアント）：
![](../assets/3.RAG-Recipe-Result.jpg)

<br>

curl コマンドでの実行例は以下の通りです。

- Windows の場合

  コマンドプロンプトを以下実行します。
  ```
  curl.exe -X POST "http://localhost:5100/recipe" -H "Content-Type: application/json" -d "{\"FishID\":\"f010\",\"FishName\":\"タチウオ\",\"UserInput\":\"地元レシピを教えてください\"}"
  ```

- Linux の場合

  ```
  curl -X POST "http://localhost:5100/recipe" \
  -H "Content-Type: application/json" \
  -d '{"FishID":"f010","FishName":"タチウオ","UserInput":"地元レシピを教えてください"}'
  ```


🎣釣り人をサポートするアプリの骨格が完成です🎣お疲れ様でした🐟


<br>
<br>

## REST ディスパッチクラスで動かしてみる

以下の手順は、ObjectScript で REST ディスパッチクラスを作成し、動作を確認する手順です。

> (1)を飛ばして(0)→(2) の順に進めていただいても大丈夫です。

- [(0) 事前準備](#0-事前準備)

  ワークショップの環境へは、VSCode を利用して接続いただきます。
  
  Linux へ接続するために使用する SSH エクステンションと、IRIS へ接続するために必要な ObjectScript エクステンションをインストールし、それぞれの接続設定を行い、接続します。

- [(1) curl コマンドを使って生成 AI に質問](#1-curl-コマンドを使って生成-ai-に質問)

    生成 AI に渡すプロンプトの作成練習をします。
    
    プログラムから実行する前に curl コマンドを利用して回答が返ってくることを確認します。

- [(2) REST アプリを作って生成 AI に質問](#2-rest-アプリを作って生成-ai-に質問)

    (1) で試したプロンプトを今度はプログラムから実行できるようにしていきます。


### 💡最初にお読みください💡ワークショップの環境について

ワークショップでは、Linux（Ubuntu 22.04）に VSCode の SSH エクステンションを使用して接続いただき、各自の作業ディレクトリを作成してから操作いただきます。

Ubuntu22.04 には、デフォルトでインストールされている Python3.10 と、InterSystems IRIS 2025.1.1 がインストールされています。

複数人で 1台の Ubuntu にアクセスするため、<span style="color: blue">**Python パッケージについては既にデフォルトロケーション（/home/meetup2025/.local/lib/python3.10/site-packages）にインストールしていますので、各自でインストールいただく必要はありません。**</span>

![](../assets/3.RAG-WorkShopEnv.jpg)

### (0) 事前準備

VSCode を開き、ワークショップで使用する 2 つのエクステンションをインストールします。

#### Remote-SSH

![](../assets/3.RAG-ssh-extention.jpg)

インストール後、SSH用構成ファイル（config）に以下のアクセス情報を設定します。

接続先 IP アドレス|ubuntu ユーザ名|ubuntu パスワード|pem
--|--|--|--
20.78.1.189|meetup2025|meetup2025|dcjmeetup20252key.pem

`pem`を以下ディレクトリにコピーしておきます。

> ファイルは共有Drive直下にあります。ご利用時場所をご説明しますのでお声がけください。

**c:\Users\ログイン名\\.ssh\dcjmeetup20252key.pem**


コピー後、SSH エクステンションの構成ファイルに接続情報を設定します。

図解は以下の通りです。

![](../assets/3.RAG-ssh-config.jpg)

例）
```
Host dcjmeetup2025
    HostName 20.78.1.189
    User meetup2025
    IdentityFile C:\Users\ログイン名\.ssh\dcjmeetup20252key.pem
```
設定が完了したら、接続します。

VSCode左下の緑のアイコンクリック > Connect to Host... をクリックし設定した接続名をクリックします（例の説明名は、dcjmeetup2025）。

![](../assets/3.RAG-ssh-connect.jpg)

接続が完了したら、ターミナルを起動し、ワークショップ用作業ディレクトリを作成します。

名前が被らないように確認しながら**お名前のディレクトリ**を作成します。

VSCode のメニューから「Terminal」→「New Terminal」を選択し以下実行します。

例）**ディレクトリ名はお名前などを利用して被らない名前で作成してください**

メモ：ログイン後のカレントディレクトリは以下の通りです。
```
$ pwd
/home/meetup2025
```
`/home/meetup2025` 以下に作業用ディレクトリを作成します。
```
mkdir IIJ
```

この後の作業は作成したディレクトリに移動してから行います。

VSCodeのメニュー：File から作成したディレクトリに移動しましょう。

**[File] → [Open Folder...] > [作成したディレクトリ]** を選択します。

移動後に、サンプル一式をコピーします（公開しているリポジトリの中身一式と同じです）。

```
cp -rf /home/meetup2025/meetup2025Workshop .
```

VSCode の エクスプローラー画面に **[meetup2025Workshop]** ディレクトリがコピーされたら準備完了です。


<br>

#### ObjectScript エクステンションのインストール

VSCode から IRIS に接続するためには、ObjectScript エクステンションが必要となりますのでインストールと接続設定を行います。

インストール方法の図解： [「VSCodeを使ってみよう！：1、ObjectScript用エクステンションのインストール」](https://jp.community.intersystems.com/node/482976#1) をご覧いただきながらインストールしてください。

インストールが完了したら、IRIS に接続します。

[「VSCodeを使ってみよう！：2、サーバへ接続する
」](https://jp.community.intersystems.com/node/482976#2) をご覧いただきながら設定してください。

**なお、設定の単位は `WorkSpace` を選択してください**

![](../assets/3.RAG-VSCode-AddServerToWorkspace.jpg)

host|port|scheme|username|IRIS ユーザ名|IRIS パスワード
--|--|--|--|--|--
20.78.1.189|80|http|meetup2025|meetup2025|meetup2025


づづいて、接続テストを行います。

#### ターミナルで IRIS へのログインテスト

VSCode でターミナルを開きます（開いている場合はそのターミナルを使用してください）。

VSCode メニューの **「Terminal」→ 「New Terminal」**

IRIS にログインします。
```
iris session iris
```
ユーザ名、パスワードを聞かれるので、以下入力します。

ユーザ名|パスワード
--|--
meetup2025|meetup2025

実行例は以下の通りです。
```
$ iris session iris

ノード: dcjmeetup2025-2 インスタンス: IRIS

ユーザ名:meetup2025
パスワード:**********
USER>
```
IRIS ログイン後のプロンプトに表示されているのはネームスペース名で（USER>）、USER ネームスペースに接続していることを示しています。

この環境を SQL shell に変更することができます。

`:s` を入力します。 
```
USER>:s 
SQL Command Line Shell
----------------------------------------------------

The command prefix is currently set to: <<nothing>>.
Enter <command>, 'q' to quit, '?' for help.
[SQL]USER>>quit

USER>
```
元のネームスペースのプロンプトに戻るには、`quit` を入力します。

SQL shell は、デフォルトではシングルステートメントモードになっていますので、SQL を複数行に分けて入力したい場合は、SQL shell に画面切り替え後 Enter を入力します。

また、複数行モードで SQL 文を実行するときは go を入力してください。

実行例）
```
USER>:s
SQL Command Line Shell
----------------------------------------------------

The command prefix is currently set to: <<nothing>>.
Enter <command>, 'q' to quit, '?' for help.
[SQL]USER>>  << entering multiline statement mode, 'GO' to execute >>
        1>>select * from Meetup2025.FishingInfo
        2>>where ID<20
        3>>go
1.      select * from Meetup2025.FishingInfo
        where ID<20

| SpotID | FishID | ReportDate | Size | FishCount |
| -- | -- | -- | -- | -- |
| tb-001 | f011 | 67471 | 10 | 4 |
  ～省略～
| tb-001 | f001 | 66783 | 15 | 1 |

19 Rows(s) Affected
statement prepare time(s)/globals/cmds/disk: 0.1231s/35,114/173,513/34ms
          execute time(s)/globals/cmds/disk: 0.1002s/43,193/239,251/18ms
                                query class: %sqlcq.USER.cls52, %sqlcq.USER.cls52.H506r0Km96V
---------------------------------------------------------------------------
[SQL]USER>>quit

USER>
```
IRIS から通常のターミナルに戻る場合は、`halt` または `h` を入力します。

#### 管理ポータルを起動する。

管理ポータルは、VSCode の接続文字列をクリックし、表示されるメニューの [Open ManagementPortal](http://127.0.0.1:52773/csp/sys/UtilHome.csp) から起動できます。

図解は以下の通りです。
![](../assets/3.RAG-ManagementPortal.jpg)

今回よく利用する SQL メニューの開き方は以下の通りです。

**[システムエクスプローラ] > [SQL]**

![](../assets/3.RAG-MP-SQL.jpg)

ネームスペースは **USER** を使用します。異なる名称が表示されている時は、USER に切り替えてからご利用ください。

<br>
以上で🐟事前準備完了です！

<br>

### (1) curl コマンドを使って生成 AI に質問

本日使用する生成 AI へのエンドポイントは以下の通りです。

http://当日案内のあるIPアドレス/api/chat

早速、curl コマンドで「こんにちは」を入力して生成 AI からの回答を確認してみましょう。

VSCode の ターミナルをまだ開いていなかったら開いてください（Terminal → New Terminal）。

以下の curl コマンドをコピーして、ターミナルに貼り付け実行してみてください。

**<span style="color: blue">※ IPアドレスは、会場で案内のある IP に置き換えて実行してください。</span>**

```
curl http://13.115.186.166/api/chat -d '{
  "model": "hf.co/mmnga/ELYZA-Shortcut-1.0-Qwen-7B-gguf:q4_k_m",
  "messages": [
    { "role": "user", "content": "こんにちは" }
  ],
  "stream":false,
  "options": {
    "num_gpu": 999,
    "num_ctx": 2048,
    "num_thread": 8,
    "num_predict": 256
  }
}'
```

結果が返ってきましたか？

以下、curl コマンドの引数に渡していた JSON の中身についてご紹介します。

プロパティ|値|用途
--|--|--
model|hf.co/mmnga/ELYZA-Shortcut-1.0-Qwen-7B-gguf:q4_k_m|ワークショップで使用しているオープンソース LLM のモデル名です。<br>[日本語特化の大季語言語AI「ELIZA（イライザ）」](https://service.elyza.ai/)のオープンソースモデルを使用しています
messeages|JSON配列|生成AIに渡す質問（プロンプト）をJSON配列で指定します。
role|user または、system|プロンプトの役割を示しています。
content|テキスト|プロンプトの中身（role が user の場合は、質問内容、role が system の場合には、生成 AI に期待する役割を指定します。）
stream|false|回答文をチャットのように 1 文字ずつ返送したいときは true、全文一気に返送の時したいときは false
options|{<br>"num_gpu": 999,<br>"num_ctx": 2048,<br>"num_thread": 8,<br>"num_predict": 256<br>}|ワークショップで使用する環境設定値（変更せずそのままご利用ください）

<br>
次は、role が system のプロンプトを追加してみます。

今回は、釣った魚を使ったレシピ生成を依頼予定なので

<span style="color: green">「あなたは釣り場にちなんだ地元のレシピをよく知るアシスタントです。依頼のあった魚のレシピを回答してください。」</span>

などのような文言をシステムプロンプトに追加してみます。

```
  "messages": [
    { "role": "system", "content": "あなたは釣り場にちなんだ地元の魚料理をよく知るアシスタントです。依頼のあった魚のレシピを回答してください。" },
    { "role": "user", "content": "木更津沖堤防で釣ったアジの美味しい食べ方を教えてください" }
  ],
```
curl コマンド全体は、以下の通りです（IPアドレスを会場で案内のあったものに変更してから実行してください）。

```
curl http://13.115.186.166/api/chat -d '{
  "model": "hf.co/mmnga/ELYZA-Shortcut-1.0-Qwen-7B-gguf:q4_k_m",
  "messages": [
    { "role": "system", "content": "あなたは釣り場にちなんだ地元の魚料理をよく知るアシスタントです。依頼のあった魚のレシピを200文字以内に要約して回答してください。" },
    { "role": "user", "content": "木更津沖堤防で釣ったアジの美味しい食べ方を教えてください" }
  ],
  "stream":false,
    "options": {
    "num_gpu": 999,
    "num_ctx": 2048,
    "num_thread": 8,
    "num_predict": 256
  }
}'
```

🐟レシピ🐟は返りましたか？

現時点のレシピですが、一般的なレシピの回答になっていると思います。

この後の流れでは、**釣った場所などの情報をデータベースから取得してアプリ内で追加し**、釣り人ビギナーの助けになるレシピ生成を目指します！🎣


### (2) REST アプリを作って生成 AI に質問

今回用意している釣り場オリジナル情報を最初に確認してみましょう！

釣り場のサンプルデータとして、木更津沖堤防（id=tb-001）と横浜本牧海づり施設（id=tb-004）の情報が含まれています（ダミーデータです）。

[管理ポータルの SQL メニュー](http://20.78.1.189/csp/sys/exp/%25CSP.UI.Portal.SQL.Home.zen?$NAMESPACE=USER)、または、SQL shell でデータを確認してみましょう。

- 管理ポータルの開き方は、[管理ポータルを起動する](#管理ポータルを起動する) をご覧ください。

- SQL shell の操作方法は、[ターミナルで IRIS へのログインテスト](#ターミナルで-iris-へのログインテスト) をご覧ください。


テーブル名|内容
--|--
MeetUp2025.BayInfo|潮位情報
MeetUp2025.FishingInfo|釣果情報

2025-12-03 10時の前後 3 時間潮位情報を確認してみましょう。

```
SELECT 
SpotID, SpotName, DatetimeJst, TideHeightCmRelative, TideState, TideCycle
FROM MeetUp2025.BayInfo
Where DatetimeJst BETWEEN DATEADD(hour,-3,'2025-12-03 13:00:00') AND DATEADD(hour,3,'2025-12-03 13:00:00')
```

2025-12-03 13時から前後 1 ヵ月、過去 2 年間の木更津沖堤防（tb-001）で釣れたスズキ（f025）の釣果情報を確認します。
```
SELECT 
SpotID, FishID, ReportDate, Size, FishCount
FROM MeetUp2025.FishingInfo
WHERE SpotID='tb-001' AND FishID='f025' AND (ReportDate >= DATEADD(yyyy,-2,'2025-12-03 13:00:00') AND (DATEPART(mm,ReportDate) BETWEEN DATEPART(mm,'2025-12-03 13:00:00')-1 AND DATEPART(mm,'2025-12-03 13:00:00')+1))
```

なお、FishIDと魚名の一覧は以下の通りです（FishID の昇順15件）。

FishID|Name
--|--
f001|マアジ
f002|サバ
f003|カマス
f004|イワシ
f005|カレイ
f006|サンマ
f007|鯛
f008|サケ
f009|ブリ
f010|タチウオ
f014|アイナメ
f015|ウナギ
f016|ウミタナゴ
f019|カサゴ
f025|スズキ

メモ：釣果データはダミーデータのため、指定する🐟によっては十分な量のデータがない場合もあります。

この後作成する REST アプリでは、2つのテーブルから釣り場にちなんだ情報を取得し、システムプロンプトに補足情報として追加し、生成 AI に質問する予定です。

---
ここからは、[3.RAG/ObjectScript/](../3.RAG/ObjectScript/) に お名前のパッケージ名用フォルダをご用意いただいた後、サンプルファイルをコピーし、必要なコードを追記しながら進めてきます。

サンプルは [Sample.REST](../3.RAG/ObjectScript/Sample/REST.cls) にあります。

完成版は [Sample.RESTCOMPLETEVER](../3.RAG/ObjectScript/Sample/RESTCOMPLETEVER.cls)にあります。

- [(1)RESTディスパッチクラスを動かしてみる](#1restディスパッチクラスを動かしてみる)
- [(2)RESTディスパッチクラスで魚の画像から魚名が得られるか試してみる](#2restディスパッチクラスで魚の画像から魚名が得られるか試してみる)
- [(3)RESTディスパッチクラスで生成 AI に渡す補足情報を追加してみる](#3restディスパッチクラスで生成-ai-に渡す補足情報を追加してみる)

#### (1)RESTディスパッチクラスを動かしてみる

RESTディスパッチクラスを作成します。クラス定義を作成する前に、パッケージ名用のディレクトリを作成します。

ワークショップでは、お名前をパッケージ名に使用します。

> 例：IIJ、Iijima など、他の方と被らない名称を設定します。パッケージ名、クラス名は大小文字を区別します。

[3.RAG/ObjectScript](../3.RAG/ObjectScript/) 以下にお名前のディレクトリを作成してください。

作成したディレクトリに Sample ディレクトリ以下にある [REST.cls](../3.RAG/ObjectScript/Sample/REST.cls) ファイルをコピーします。

コピー後、クラス名を修正してください。

現在 `Sample.REST` と記載されているので、`Sample` を作成されたディレクトリ名に変更します。

例）IIJ というディレクトリを作った場合の 1 行目の `Class定義文` は以下の通りです。
```
Class IIJ.REST Extends %CSP.REST
```

Ctrl+S でクラス定義を保存しコンパイルを実施します。

※もしコンパイルがうまくいかないときは、VSCode が IRIS に接続できているか接続情報を再度ご確認ください。ご参考：[ObjectScript エクステンションのインストール](#objectscript-エクステンションのインストール)

続いて、管理ポータルでRESTディスパッチクラスを動かすための「ウェブ・アプリケーションパス」を定義します。

このパスは任意の名称で作成できますが、ワークショップでは、`/csp/xxx` のように、`/csp` から始まるパス名を作成してください。

管理ポータルを起動します。（ご参考：[管理ポータルを起動する。](#管理ポータルを起動する)）

[システム管理] > [セキュリティ] > [アプリケーション] > [ウェブ・アプリケーション] に移動し、「新しいウェブ・アプリケーションを作成」ボタンをクリックします。

![](../assets/3.RAG-WebAppNew.jpg)

新しいパスを作成します。ここでも、/csp/お名前 で作成してください。

例）/csp/iij

設定内容は以下の通りです（例の **iij** は**全てお名前に置き換えて**設定してください
）。

名前|ネームスペース|ディスパッチ・クラス|許可された認証方法
--|--|--|--
/csp/**iij** <br>※/csp/**以下をお名前に変更します**|USER（デフォルト）|**IIJ**.REST <br>※**パッケージ名を設定された名称に変更します**|**認証なし**のみチェックします。

![](../assets/3.RAG-WebApp-New-Settings.jpg)

一旦画面内の保存ボタンをクリックします。

次に、「アプリケーション・ロール」タブをクリックし、ウェブ・アプリケーション実行時のみ、%All ロール追加するように設定します。

![](../assets/3.RAG-WebApp-AppRoleAdd.jpg)

早速テストしてみましょう！

http://20.78.1.189/csp/iij/hello

ブラウザで上記 URL を実行して `{"RetMessage":"あいうえお"}` と表示されれば設定完了です（/csp/**ここ**　は設定したパス名に変更して実行してください）。


表示された方は、次に進みましょう！🐟

#### (2)RESTディスパッチクラスで魚の画像から魚名が得られるか試してみる

🐟の画像から魚名を調べるため、ベクトル検索を動かしてみましょう！

[Sample.REST](../3.RAG/ObjectScript/Sample/REST.cls) に画像ファイルアップロード用のPOST要求のパス：/upload　のコードが記載されています（メソッド名：upload()）。

コードの中では、fish と名付けたフォームデータ名で画像ファイルの中身が送られると、`basepath`で指定されたフォルダに画像ファイルが保存され、その後ベクトル検索で画像から魚名を取得し、応答 JSON を返します。

この `basepath` は、[3.RAG/ObjectScript/upload](../3.RAG/ObjectScript/upload/) に用意があります。

IRIS の REST ディスパッチクラスからアップロードファイルを配置できるように、Permission を変更します。

[3.RAG/ObjectScript/upload](../3.RAG/ObjectScript/upload/) を右クリックし「Copy Path」でフルパスをコピーし、Ubuntu のターミナルで以下実行してください。

例：upload のフルパス `/home/meetup2025/IIJ/3.RAG/ObjectScript/upload`　(作成した作業用ディレクトリに変更してください)

```
chmod 777 uploadのフルパス
```

upload()メソッドは以下の通りです。
```
/// 魚の画像はfishで送る
ClassMethod upload() As %Status
{
    #dim %request As %CSP.Request
    /* === basepath を変更します ===
        🐟環境に合わせて変更してください！
        basepath は ワークショップ用に作成されたディレクトリ以下の任意にディレクトリを指定します。
        フルパスで指定してください。
    =========================== */
    set basepath="/src/images/"
    set basepath=##class(%File).NormalizeDirectory(basepath)

    set upstream=$get(%request.MimeData("fish", 1))
    set fname=%request.MimeData("fish",1).FileName
    set fo=##class(%Stream.FileBinary).%New()
    do fo.LinkToFile(basepath_fname)
    do fo.CopyFrom(upstream)
    set status=fo.%Save()
    if $$$ISERR(status) {
        // ファイル保存失敗
        return status
    }
    //画像のEmbedding
    set embed=##class(MeetUp2025.Event).GetEmbedding("I",basepath_fname)
    //ベクトル検索
    set sql="select top 1 FishID,Name,VECTOR_COSINE(Features, TO_VECTOR(?, DOUBLE, 512)) as cos from MeetUp2025.Fish ORDER BY cos desc"    set stmt=##class(%SQL.Statement).%New()
    set status=stmt.%Prepare(sql)
    set rset=stmt.%Execute(embed)
    do rset.%Next()

    //　JSON作成
    set json={}
    set json.FishID=rset.%Get("FishID")
    set json.FishName=rset.%Get("FishName")
    do json.%ToJSON()
    return $$$OK
}
```

現在、upload() メソッドの `basepath` には、以下のディレクトリがデフォルトで指定されています。
```
set basepath="/src/images/"
```
先ほど確認した upload ディレクトリのフルパスに変更し、Ctrl＋S で保存＋コンパイルを実行します。

ベクトル検索の記述は、[Sample.REST](../3.RAG/ObjectScript/Sample/REST.cls) の45行目に記載しています。

```
    //画像のEmbedding
    set embed=##class(MeetUp2025.Event).GetEmbedding("I",basepath_fname)
    //ベクトル検索
    set sql="select top 1 FishID,Name,VECTOR_COSINE(Features, TO_VECTOR(?, DOUBLE, 512)) as cos from MeetUp2025.Fish ORDER BY cos desc"    set stmt=##class(%SQL.Statement).%New()
    set status=stmt.%Prepare(sql)
    set rset=stmt.%Execute(embed)
    do rset.%Next()
```
類似検索で一番似ているものを 1 件だけ取得しています。

SQL の引数には画像の Embedding が必要になるため、Embedding 用の SQL 関数：MeetUp2025.GetEmbedding() を事前に用意し、実行時に画像ファイルを第 2 引数に渡しています（第 1 引数は画像ファイルの場合は "I" を指定）。

> MeetUp2025.GetEmbedding() 関数のコードについて詳しくは、[MeetUp2025.Event クラス](../0.Prep/MeeUp2025/Event.cls) 59行目以降をご参照ください（またはワークショップでご質問ください！）。

検索結果は、以下のように FishID と Name が JSON で返送される予定ですので、さっそく試してみましょう！
```
    //　JSON作成
    set json={}
    set json.FishID=rset.%Get("FishID")
    set json.FishName=rset.%Get("Name")
    do json.%ToJSON()
```


URL|Method|Header名|Headerの値
--|--|--|--
http://20.78.1.189/csp/iij/upload<br>※/csp/**ここ** は作成したパスに変更します|POST|Content-Type|multipart/form-data

Body には以下設定します。
Key|値
--|--
fish（小文字で指定します）|画像ファイル

以下、REST クライアントからの実行例です。

![](../assets/3.RAG-Upload-postman-RESTDispatch.jpg)

応答例：
```
{
    "FishID": "f004",
    "FishName": "イワシ"
}
```

REST クライアントをお持ちでない方は、[Chrome の拡張機能](#chrome-の拡張機能の場合objectscript)、または [curlコマンド](#curl-コマンドの場合objectscript)を利用してお試しいただけます。

##### Chrome の拡張機能の場合（ObjectScript）

Chrome を開き、[Talend API Tester - Free Edition](https://chromewebstore.google.com/detail/talend-api-tester-free-ed/aejoelaoggembcahagimdiliamlcdmfm?hl=ja) に移動し、画面右上の [Chrome に追加] ボタンで追加できます。

画面を開いたら、後は上記指定の通り入力します（画像ファイルはローカルのファイルを選択できます）。

![](../assets/3.RAG-TalendAPI-Open.jpg)

画面を開いたらリクエストに必要な情報を入力し、Send ボタンをクリックします。

![](../assets/3.RAG-TalendAPI-Upload-RESTDispatch.jpg)


##### curl コマンドの場合（ObjectScript）

curl コマンドでの実行例は以下の通りです。

- Windows の場合

  コマンドプロンプトを開き、以下実行します。

  例は、**c:\temp\test**以下にアップロード対象ファイル（tachiuo.jpg）が存在している場合の例です。任意のディレクトリやファイル名に変更してから実行してください。

  ```
  curl.exe -X POST -F "fish=@C:\temp\test\tachiuo.jpg" http://20.78.1.189/csp/作成したパス名/upload
  ```


- Linux 系の場合

  ターミナルを開き以下実行します。

  例は、**/home/ubuntu/IIJ/meetup2025Workshop/3.RAG** 以下にアップロード対象ファイル（tachiuo.jpg）が存在している場合の例です。任意のディレクトリやファイル名に変更してから実行してください。

  ```
  curl -X POST -F "fish=@/home/ubuntu/IIJ/meetup2025Workshop/3.RAG/tachiuo.jpg" http://20.78.1.189/csp/作成したパス名/upload
  ```


<br><br>
ベクトル検索で得られた魚名をこの後の流れで利用します。

次はいよいよ、生成 AI へのレシピ生成依頼です。


#### (3)RESTディスパッチクラスで生成 AI に渡す補足情報を追加してみる

[Sample.REST](../3.RAG/ObjectScript/Sample/REST.cls) には、生成 AI にレシピ生成を依頼する際に指定する /recipe 呼び出されるメソッド recipe() が用意されています。

最初に GetFishInfo() メソッドを呼び出し、釣った魚にちなんだ釣果情報、潮位情報を取得しています。

ターミナルでテスト実行できます。IRIS にログインして以下実行します。
```
iris session iris
```
ターミナルでは REST クライアントから入力予定のJSONが必要になるので作成後、メソッ
ドを実行します。

実行後元のJSONに釣果情報、潮位情報が追加されます。

```
USER>set json={}

USER>set json.FishID="f004"

USER>set json.FishName="イワシ"

USER>set json.UserInfo="簡単に作れる地元料理を知りたいです"

USER>set st=##class(Sample.REST).GetFishInfo(.json)

USER>zwrite json
json={"FishID":"f004","FishName":"イワシ","UserInfo":"簡単に作れる地元料理を知りたいです","FishInfo":"2025-10-27 11:00:00 釣り場：木更津沖堤防の状況は、上げ潮、長潮、潮位は67cm　本日の前後1か月の過去2年間の釣果情報は、★サンプルデータ範囲外のためダミーデータを返送★ 最大数:115、最小数:1、最大長cm:87、最小長cm:8"}  ; <DYNAMIC OBJECT,refs=1>

USER>h
```
生成 AI に渡す補足情報を入手したら、後はプロンプトに追加して POST 要求を実行するだけです。

プロンプトを作成しているところは、AskLLM()メソッドの以下の記述の部分です。

2回目に登場する `set prompt.role="user"` 以降に、魚名、釣り場の潮位情報、釣果情報などプロンプトに設定します。

```
ClassMethod AskLLM(flg As %Boolean = 1, body As %DynamicAbstractObject, ByRef ans As %DynamicAbstractObject) As %DynamicAbstractObject
{
    #dim ex As %Exception.AbstractException
    set status=$$$OK
    set ans={}
    set ans.Message=""
    try {
        //送信メッセージの準備
        set sendjson={}
        set sendjson.messages=[]
        set prompt={}
        set prompt.role="system"
        set prompt.content="あなたは釣り場にちなんだ地元の魚料理をよく知るアシスタントです。地元名は fishinfo: 以降に記載のある釣り場の名称を使用します。依頼のあったレシピを250文字程度に要約して回答してください。"
        do sendjson.messages.%Push(prompt)
        set prompt={}
        set prompt.role="system"
        /* === prompt.content を変更します ===
        　prompt.content に魚の名称と釣果情報、潮位情報を追加してください。
          システムプロンプトに「fishinfo: 以降に」釣果情報や潮位情報が来てほしいので
          目的の文字列を作成い prompt.contet　に設定します。
          ＜文字列例＞
          "魚名は"_body.FishName_"。fishinfo:"_body.FishInfo
        ================================*/
        set prompt.content=""

        do sendjson.messages.%Push(prompt)
        set prompt={}
        set prompt.role="user"
        set prompt.content=body.UserInput
        do sendjson.messages.%Push(prompt)
        //request
        set req=##class(%Net.HttpRequest).%New()
        set req.ContentType="application/json"
        set req.ContentCharset="utf-8"

        /*LLM毎の準備*/
        // Ollama
        /* === req.Server を変更します ===
            🐟環境に合わせて変更してください！
            LLMのIPアドレスはワークショップ当日に公開します。
            実行前に必ず変更してください！
        =========================== */        
        if flg=1 {
            set req.Server="13.115.186.166"
            set req.Location="/api/chat"
            //モデルの指定
            set sendjson.model="hf.co/mmnga/ELYZA-Shortcut-1.0-Qwen-7B-gguf:q4_k_m"
            do sendjson.%Set("stream",0,"boolean")
            set options={}
            set options."num_gpu"=999
            set options."num_ctx"=2048
            set options."num_thread"=8
            set options."num_predict"=256
            do sendjson.%Set("options",options.%ToJSON())
        }
 ```

今回は、[(2)RESTディスパッチクラスで魚の画像から魚名が得られるか試してみる](#2restディスパッチクラスで魚の画像から魚名が得られるか試してみる) の流れで特定した魚名、魚ID から、生成 AI にレシピ生成を依頼するときに追加する釣り場オリジナル情報として、データベースから釣り場の潮位情報と釣果情報を入手予定です。

釣り場の潮位情報、釣果情報は、[Sample.REST](../3.RAG/ObjectScript/Sample/REST.cls) のメソッド GetFishInfo() で取得できることを確認しています。

生成 AI に渡すプロンプトの部分が歯抜け状態になっていますので、得られた情報をシステムプロンプトとユーザプロンプトの `prompt.content` に設定し、実行し、釣った地元にあったレシピが返送されるか確認してみてください。

また、実行前に必ず生成 AI の接続に使用するIPアドレスを修正してください。

([Sample.REST](../3.RAG/ObjectScript/Sample/REST.cls) の228行目　の req.Serverの値）
```
        if flg=1 {
            set req.Server="13.115.186.166"
```

回答例は [Sample.RESTCOMPLETEVER](../3.RAG/ObjectScript/Sample/RESTCOMPLETEVER.cls) 200 行目にあります。


<br>
準備ができたら実行してみましょう！

> 💡木更津沖でよく釣れるさかな

FishID|FishName
--|--
f001|マアジ
f002|サバ
f005|カレイ
f007|鯛
f025|スズキ

<br>

パス|ヘッダ名|値|Body指定例
--|--|--|--
http://20.78.1.189/csp/iij/upload<br>※/csp/**ここ** は作成したパスに変更します|Content-Type|application/json;charset=utf-8|{<br>"FishID": "f002",<br>"FishName": "サバ",<br>"UserInput": "体があたたまる地元料理"<br>}


実行例：
![](../assets/3.RAG-Recipe-Result-RESTDispatch.jpg)


curl コマンドを利用する場合は以下の通りです。

- Windows の場合

  コマンドプロンプトを以下実行します。
  ```
  curl.exe -X POST "http://20.78.1.189/csp/iij/recipe" -H "Content-Type: application/json" -d "{\"FishID\":\"f002\",\"FishName\":\"サバ\",\"UserInput\":\"地元レシピを教えてください\"}"
  ```

- Linux の場合

  ```
  curl -X POST "http://20.78.1.189/csp/iij/recipe" \
    -H "Content-Type: application/json" \
    -d '{"FishID":"f002","FishName":"サバ","UserInput":"地元レシピを教えてください"}'
  ```

<br>

🎣釣り人をサポートするアプリの骨格が完成です🎣お疲れ様でした🐟
