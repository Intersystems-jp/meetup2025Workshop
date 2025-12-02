# 第3回開発者コミュニティミートアップ ワークショップ

このリポジトリには、2025年12月3日開催 InterSystems 開発者コミュニティミートアップワークショップ用のガイドやコード例などが含まれています。



フォルダ|含まれる内容
--|--|
[0.Prep (事前準備) ](./0.Prep/)|ローカルの環境で試していただくための事前準備内容が含まれています。<br><span style="color: green">**※ワークショップ当日は使用しません。</span>**<br>ご自身の環境で試される場合は、[ローカルで動かすための事前準備について](#ローカルで動かすための事前準備について)、をご参照ください。|
[1.VectorSearch](./1.VectorSearch/)|IRIS のベクトル検索であそぼう！で使用するサンプルコードが含まれています。<br> 参考ウェビナー：[IRISのベクトル検索を使って テキストから画像を検索してみよう](https://youtu.be/l2NuPYxgIgI?list=PLzSN_5VbNaxA8mOezO6Vcm126GXw_89oN)|
[2.VectorAsobo](./2.VectorAsobo/)|ベクトルであそぼう！で使用するサンプルコードが含まれています。<br>参考ウェビナー：[ベクトルであそぼう！](https://youtu.be/c285zESVmRQ?list=PLzSN_5VbNaxA8mOezO6Vcm126GXw_89oN)|
[3.RAG](./3.RAG/)|RAG+生成AIであそぼう！で使用するサンプルコードが含まれています。<br>参考ウェビナー：[RAG+生成AIであそぼう！](https://youtu.be/8_dx8BpvOic?list=PLzSN_5VbNaxA8mOezO6Vcm126GXw_89oN)|
[4.Advanced](./4.Advanced/)|お時間ある方に、🎣釣り人ビギナーサポートAI<span style="color: green">**エージェント**</span> 体験用のコードをご用意しています。|

## ワークショップを始める時に設定いただきたいこと

以下の準備をお願いします。
- [[1] googleアカウントの準備（Colabを使用します）](#1-googleアカウントの準備colabを使用します)
- [[2] VSCodeのインストール](#2-vscodeのインストール3rag-で-objectscript-で進める場合にのみ使用します)

    **※ VSCode のインストールについては、[3.RAG](./3.RAG/) の流れを ObjectScript で進めたい場合にのみ、準備をお願いします。**

- [[3] 共有のGoogleDriveのショートカットの作成](#3-共有のgoogledriveのショートカットの作成)
- [[4] サンプルの Notebook を Colab で開くまでの手順](#4-サンプルの-notebook-を-colab-で開くまでの手順)

詳細は以下の通りです。

### [1] googleアカウントの準備（Colabを使用します）

ワークショップでは、[Colab](https://colab.research.google.com/) にサンプル Notebook をアップロードした後、必要な作業を進めていきます。


### [2] VSCodeのインストール（[3.RAG](./3.RAG/) で ObjectScript で進める場合にのみ使用します）

VSCodeをご持参いただくパソコンにインストールしてください。

インストール後、ワークショップ内で以下 2 つのエクステンションをインストールします。

- ObjectScript エクステンション

- SSH エクステンション

エクステンションのインストール詳細は、[3.RAG/README の(0)事前準備](/3.RAG/README.md#0-事前準備) をご参照ください。


### [3] 共有のGoogleDriveのショートカットの作成

[1.VectorSearch]()と[2.VectorAsobo](/2.VectorAsobo/) の流れで使用します。

ワークショップ用 GoogleDriveの共有ディレクトリへのショートカットをご自身のGoogleDriveの任意ディレクトリに作成してください。

手順は以下の通りです。

1. 自分のGoogle Driveにショートカットを設定する専用のディレクトリを作成します。

    例）MeetUp2025Share

2. [共有ドライブのリンク](https://drive.google.com/drive/folders/1l10xKfyF5ehmb1H1JTevPwG14wKfGsoY?usp=sharing)をブラウザで開きます（Googleアカウントでログインしているブラウザで開きます）。

3. 2をブラウザで開いた状態で1で作成したディレクトリにショートカットを追加します。

    ![](/assets/GoogleDrive-Shortcut-1.jpg)

    ショートカットが完成すると以下のように表示されます。
    ![](/assets/GoogleDrive-Shortcut-2.jpg)

### [4] サンプルの Notebook を Colab で開くまでの手順

#### (1) リポジトリのダウンロード

一旦、このリポジトリをローカルの環境にダウンロードしします。

Git をインストールされている方は、任意のディレクトリで以下実行します。
```
git clone https://github.com/Intersystems-jp/meetup2025Workshop.git
```

Git をインストールされていない方は、ブラウザで[リポジトリ](https://github.com/Intersystems-jp/meetup2025Workshop)を開き、ダウンロードします。

![](/assets/Git-Download.jpg)

ダウンロード後、Zipを展開します。

#### (2) Google Drive に Notebook をコピーする

[Google Drive](https://drive.google.com/drive/my-drive) を開き、任意のディレクトリに移動し、対象ファイルをアップロードします。

![](/assets/GoogleDrive-upload.jpg)

アップロードした notebook をダブルクリックし、Colab で開きます。

![](/assets/GoogleDrive-OpenNotebook.jpg)


<br>
以上でワークショップを進めるための準備は完了です！

## ローカルで動かすための事前準備について

ワークショップ後、ご自身の環境などで体験を継続される場合の準備をご説明します。

### (1)テーブルの準備

テーブル定義一式をインポートします。

使用するファイル：[MeetUp2025-tables.xml](/0.Prep/MeetUp2025-tables.xml)

インポートは管理ポータル、または VSCode から行えます。

> VSCode でインポートする方法について詳細は、[VSCode：管理ポータルやスタジオにある「XMLファイルのインポート／エクスポート 」が追加されました](https://jp.community.intersystems.com/node/549906)をご参照ください。

ここでは管理ポータルからの使用方法をご紹介します。

ネームスペースは %SYS 以外、任意の場所をご選択ください。図例では USER を使用しています。

**管理ポータル > [システムエクスプローラ] > [クラス]** を開き、画面左側のドロップダウンリストからインポート対象ネームスペースを選択し、「インポート」ボタンをクリックします。

![](/assets/H-MP-Import.jpg)

インポートが完了すると以下のように表示されます。

![](/assets/H-MP-Import-result.jpg)

クラスのメニューでインポートしていますが、同時にテーブル定義として管理ポータルの SQL画面から参照できます。 

インポートされるテーブル、クラスは以下の通りです。

テーブル名(クラス)|用途|
--|--|
MeetUp2025.SampleImage|`recruit-jp/japanese-image-classification-evaluation-dataset` の画像のベクトルが含まれるテーブル|
MeeUp2025.Fish|魚の画像から魚名を得るためのベクトル検索用テーブル|
MeetUp2025.FishImage|魚の画像のベクトルが含まれるテーブル|
MeetUp2025.BayInfo|RAG+生成AIの中で使用する潮位データなどが含まれるテーブル(釣り場2拠点のダミーデータが含まれています)|
MeetUp2025.FishingInfo|RAG+生成AIの中で使用する釣果データの過去データ(釣り場2拠点のダミーデータが含まれています)|
MeetUp2025.Event|RAG+生成AIの中で使用する CLIP モデルのロードと Embedding 処理を IRIS の常駐プロセスで実行するように記載しているクラス|


### (2)データの準備

管理ポータルを利用して、データのエクスポートファイルをインポートします。

使用するファイル：[meeup2025Workshop-data-export.gof](/0.Prep/meeup2025Workshop-data-export.gof)

ネームスペースは テーブル定義をインポートした場所をご選択ください。図例では USER を使用しています。

**管理ポータル > [システムエクスプローラ] > [グローバル]** を開き、画面左側のドロップダウンリストからインポート対象ネームスペースを選択し、「インポート」ボタンをクリックします。

![](/assets/H-MP-Import-Global.jpg)

インポートが完了すると以下のように表示されます。

![](/assets/H-MP-Import-Global-result.jpg)

ここまでの流れで、テーブルとデータのインポートが完了です。

**管理ポータル > [システムエクスプローラ] > [SQL]** 画面でSQLを実行し、結果が返ればインポート成功です。

例）
```
SELECT ImgId, ImgEmbedding
FROM MeetUp2025.SampleImage
```

![](/assets/H-MP-SQLtest.jpg)

メモ：画面左のテーブル名をクエリ実行欄にドラッグ＆ドロップすると、以下の SELECT 文が自動で入力されます。
```
SELECT 
カラム1,カラム2,・・・
FROM 選択したテーブル名
```


### (3)Pythonパッケージのインポート

CLIP モデルで Embedding を行うために必要な Python パッケージをインポートします。

※ 事前に Pyhton のインストールが必要です。

使用するファイル：[requirements.txt](/0.Prep/requirements.txt)

リポジトリ直下（Zip展開後ディレクトリ）に移動している場合は、以下のように実行します。

```
pip install -r ./0.Prep/requirements.txt
```

### (4)ObjectScript でベクトル検索を試すための準備

**※ 一部クラス定義を修正しますので、VSCode から IRIS に接続した状態でお試しください。**

[3.RAG/ObjectScript](/3.RAG/ObjectScript/) の流れをローカルの環境でお試しいただく場合の準備をご説明します。

REST ディスパッチクラスのサンプル：[Sample.RESTCOMPLETEVER.cls](/3.RAG/ObjectScript/Sample/RESTCOMPLETEVER.cls) で定義している `/upload` が指定されたとき、メソッド：`upload()` が実行されます。

実行中、CLIP モデルを利用した画像ファイルの Embedding が行われます。

Embedding 用関数は `MeetUp2025.Event` クラスの中で定義しています。

実際の Embedding 処理は Python で記述していて [cliputil.py](/0.Prep/src/cliputil.py) をインポートし実行しています。

`MeetUp2025.Event` クラスでインポートしている箇所は以下の通りです。

```
    //cliputil.pyインポート
    set sys=##class(%SYS.Python).Import("sys")
    do sys.path.append("/usr/irissys/mgr/user/0.Prep/src")
```
`do sys.path.append("/usr/irissys/mgr/user/0.Prep/src")` の引数には、ワークショップ環境に合わせたパスが設定されていますので、ローカルに配置した [cliputil.py](/0.Prep/src/cliputil.py) のフルパスに変更します。


手順は以下の通りです。

#### 1. [cliputil.py](/0.Prep/src/cliputil.py)のフルパスを取得

VSCode を利用している場合は、[cliputil.py](/0.Prep/src/cliputil.py)を右クリック→Copy Path で確認できます。

#### 2. MeetUp2025.Event クラスを編集

メモ：[(1)テーブルの準備](#1テーブルの準備) で一緒にインポートしているクラスです。

IRIS サーバ側にインポートされていますので、VSCode のワークスペースで編集できるように、Export を行います。

InterSystems アイコンをクリックし、`Classes > MeetUp2025 > Event.cls` を右クリックし、Export を選択するとワークスペースの `src/MeetUp2025` 以下に `Event.cls` がエクスポートされます。

![](/assets/3.RAG-VSCode-Export.jpg)

`MeetUp2025.Event`を開き、15行目を参照し、引数に指定しているパスを変更します。

```
    do sys.path.append("/usr/irissys/mgr/user/0.Prep/src")
```
※ cliputil.py が配置されているディレクトリを指定します。

修正が完了したら、Ctrl+Sで保存＋コンパイルします。

#### 3. イベントの作成と終了

魚の画像を Upload し魚名を得る処理を動かす前に、イベントを作成します。

イベントの利用目的は、CLIP モデルのロードを維持したプロセスを常駐化するために利用しています。

> 機材によりますが、CLIP モデルのロードに時間がかかる場合がありますので、モデルのロードと Embedding が行える常駐プロセスを用意しています。

イベントの開始方法は以下の通りです。（イベントが終了するまでプロンプトは返りません。）

ターミナルを開く、または iris session iris で IRIS にログインした後、以下メソッドを実行します。
```
do ##class(MeetUp2025.Event).createEvent()
```
モデルのロードには少し時間がかかります。ロードが終了すると以下実行例のように `CLIP-Load完了：xxx` と表示されますのでしばらくお待ちください。また**ターミナルプロンプトは、EndEvent()メソッド実行まで戻りませんのでそのままの状態でご利用ください。**

実行例）
```
USER>do ##class(MeetUp2025.Event).createEvent()
CLIP-Load完了：15.034278

```
イベントを終了する場合は、別ターミナルから以下実行します。
```
do ##class(MeetUp2025.Event).EndEvent()
```

> イベントクラスについての参考記事：[監視用常駐プロセスを作成する方法](https://jp.community.intersystems.com/node/584051)

以上で事前準備は完了です。

残りは、[3.RAG の「restディスパッチクラスを動かしてみる」](/3.RAG/README.md#1restディスパッチクラスを動かしてみる) をご覧いただいながら進めてください！

🎉Happy coding！🎉