(1) [Google Drive](https://drive.google.com/) 上を右クリック > その他 > Google Colaboratory
 
(2) タイトルを Untitled0.ipynb から、好きなものに変更します (naka.ipynbなど)
  
(3) 簡単な以下の 1行 Pythonコードを書いてみましょう
```
print('hello')
```
 
(4) 左の再生ボタンを押すと、実行結果がその場で出力されます。

(5) 上記のコードを選択し、下辺にマウスをあわせて、「＋コード」を選択することで、新しいコードが書けます。<br>以下の Pythonコード 3行書いて、再生ボタンを押してみましょう。
```
a = 123
b = 55
print(a+b)
```

(6) 続いて、Colab から IRIS に SQL で接続しましょう。今回ご用意した IRIS 環境は以下の通りです。<br>
|項目名|値|
|---|---|
|IPアドレス|20.78.1.189|
|Port番号|1972|
|ネームスペース|USER|
|ユーザ名|meetup2025|
|パスワード|meetup2025|
 
(7) Python コードで以下のようにして接続できます。
```
!pip install sqlalchemy-iris
from sqlalchemy import create_engine,text
engine = create_engine("iris://meetup2025:meetup2025@20.78.1.189:1972/USER")

conn = engine.connect()
result = conn.execute(text("select * from naka.test"))
results = list(result)

print()
print("Done! ----> ", results)
conn.close()
```

(8) 同じクエリを、IRIS 標準の WEB UI の管理ページである「管理ポータル」で確認してみましょう。接続ユーザ名とパスワードは上記を参照してください。

http://20.78.1.189/csp/sys/UtilHome.csp

システムエクスプローラ > SQL > 左上の「ネームスペース **%SYS**」をクリックして、USER を選択 > 以下のSQLをテキストエリアに書いて実行ボタン
```
select * from naka.test
```

-------
※以下おまけです。

Colab から　IRIS のグローバルデータを直接参照したり、クラスメソッドを実行することも、以下のように簡単にできます。ご興味あるかたお試しくださいませ。
```
!pip install https://github.com/intersystems-community/iris-driver-distribution/raw/refs/heads/main/DB-API/intersystems_irispython-3.2.0-py3-none-any.whl
print()

# 接続
import iris
conn = iris.connect("20.78.1.189:1972/USER", "meetup2025", "meetup2025")
i = iris.createIRIS(conn)

# set data = ^naka(1)
data = i.get('naka', '1')
print('^naka(1) : ', data)

# set ver = ##class(%SYSTEM.Version).Format()
ver = i.classMethodValue('%SYSTEM.Version','Format')
print('Version  : ', ver)
```

