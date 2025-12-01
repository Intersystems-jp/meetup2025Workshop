from flask import Flask,request,g,Response
import json
import requests
import os
import datetime
import config
from sqlalchemy import create_engine,text
from sqlalchemy.exc import SQLAlchemyError

# 🐟CLIPで画像／テキストEmbeddingを作るユーティリティのインポート
import cliputil

#UPLOAD用フォルダ
#！🐟環境に合わせて変更してください🐟！
UPLOAD_FOLDER = "/home/ubuntu/meetup2025Workshop/3.RAG/flask/upload"

#オープンソースLLMのURL
#！🐟環境に合わせて変更してください🐟！
API_SERVER_URL = "http://13.115.186.166/api/chat"

app = Flask(__name__)

engine = None

def initial():
    global engine
    if engine is None:
        engine = create_engine("iris://meetup2025:meetup2025@20.78.1.189:1972/USER",echo=True, future=True)

def get_conn():
    #各リクエストで接続を取得
    if 'conn' not in g:
        g.conn = engine.connect()
    return g.conn

@app.teardown_appcontext
def close_conn(e=None):
    #リクエスト終了時に接続をクローズ
    conn = g.pop('conn', None)
    if conn is not None:
        conn.close()

# モジュール読み込み時実行
initial()

@app.route('/', methods=['GET'])
def meetup():
    name = "Hello FishDetector!"
    return name


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
    fishinfo=get_fishinfo(body["FishID"])
    headers = {"Content-Type": "application/json;charset=utf-8"}
    data = {
        "model": "hf.co/mmnga/ELYZA-Shortcut-1.0-Qwen-7B-gguf:q4_k_m",
        "messages": [
            {
                "role": "system",
                "content": """
                あなたは釣り場にちなんだ地元の魚料理をよく知るアシスタントです。
                地元名は fishinfo: 以降に記載のある釣り場の名称を使用します。依頼のあったレシピを250文字程度に要約して回答してください。
                """
            },
            ##-- content に、潮位情報、釣果情報をシステムプロンプトに必要な情報を{}内に追加してください
            #{
            #    "role": "system",
            #    "content": f"魚名は{}です。 fishinfo: {}",
            #},
            ##-- "content" にユーザが入力する情報をユーザプロンプトとして追加します。
            {
                "role": "system",
                "content": "",
            },
            {
                "role": "user",
                "content": f"{body['UserInput']}",
            }
        ],
        "stream": False,
        "options": {
            "num_gpu": 999,
            "num_ctx": 2048,
            "num_thread": 8,
            "num_predict": 256
        }
    }
    response = requests.post(API_SERVER_URL, headers=headers, json=data)

    result = response.json()
    answer=json.dumps({"Message":result["message"]["content"],"FishInfo":fishinfo},ensure_ascii=False)
    return Response(answer, content_type="application/json; charset=utf-8")


# ------------------------------------------
# /recipe2 OpenAIにレシピ生成を依頼する
# Bodyの中身
#  {
#  "UserInput":"ここにユーザが希望するレシピの内容",
#  "FishName":"魚名"
#  "FishID":"f001"
# }
#
# 魚名をキーに生成AIに渡す独自データをデータベースから入手
# 独自データ＝その釣り場の潮位情報と釣果データ（デモでは釣り場は固定値を置いています）
# ------------------------------------------
@app.route('/recipe2',methods=['POST'])
def getrecipe2():
    body = request.get_json()
    fishinfo=get_fishinfo(body["FishID"])

    API_SERVER_URL="https://api.openai.com/v1/chat/completions"
    headers={
        "Content-Type":"application/json;charset=utf-8",
        "Authorization": f"Bearer {config.key}"
    }
    data = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": """
                あなたは釣り場にちなんだ地元の魚料理をよく知るアシスタントです。
                地元名は fishinfo: 以降に記載のある釣り場の名称を使用します。依頼のあったレシピを250文字程度に要約して回答してください。
                """
            },
            {
                "role": "system",
                "content": f"魚名は{body['FishName']}です。{fishinfo}",
            },
            {
                "role": "user",
                "content": f"{body['UserInput']}",
            }
        ]
    }

    response = requests.post(API_SERVER_URL, headers=headers, json=data)
    result = response.json()
    answer=json.dumps({"Message":result["choices"][0]["message"]["content"],"FishInfo":fishinfo},ensure_ascii=False)
    return Response(answer, content_type="application/json; charset=utf-8")



#------------------------------------------
# 魚名から特定の釣り場の情報（潮位情報）と過去の釣果データを入手
# 引数：魚名
# 戻り値：特定された釣り場の情報（潮位情報）と過去の釣果データの文字列
# デモでは釣り場は木更津沖堤防：SpotID='tb-001' の固定データとしています
#------------------------------------------
def get_fishinfo(fishid): 
    fishinginfo=None
    bayinfo=None
    conn = get_conn()
    #釣り場情報を入手（釣り場情報今は固定）
    JST = datetime.timezone(datetime.timedelta(hours=9))
    now = str(datetime.datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S"))

    sql2="SELECT SpotName||'の状況は、'||TideState||'、'|| TideCycle||'、潮位は'||TideHeightCmRelative||'cm' as result ,SpotID,CAST(DatetimeJst AS TIMESTAMP)"\
     " FROM MeetUp2025.BayInfo WHERE SpotID='tb-001' AND (DatetimeJst BETWEEN DATEADD(hour,-1,:nowdt) AND :nowdt)"
    rs=conn.execute(text(sql2),{"nowdt":now}).fetchall()

    bayinfo=rs[0]

    if bayinfo is None:
        #サンプルデータが2026/9/9までしか登録がないのでそれ以降はダミーを設定して返す
        spotinfo="★サンプルデータ範囲外のためダミーデータを返送★ 釣り場：木更津沖堤防 下げ潮、若潮、潮位は28.5cm"
    
    else :
        spotinfo=bayinfo[0] + "　釣り場：" + bayinfo[1]

    #釣果情報入手
    sql3="SELECT '最大数:'||MAX(FishCount)||'、最小数:'||MIN(FishCount)||'、最大長cm:'||MAX(Size)||'、最小長cm:'||MIN(Size) as result"\
     " FROM MeetUp2025.FishingInfo WHERE FishID=:fishid AND SpotID='tb-001' AND (ReportDate >= DATEADD(yyyy,-2,:nowdt) AND (DATEPART(mm,ReportDate) BETWEEN DATEPART(mm,:nowdt)-1 AND DATEPART(mm,:nowdt)+1))"
    rs=conn.execute(text(sql3),{"fishid":fishid,"nowdt":now}).fetchall()
    fishinginfo=rs[0]

    if fishinginfo is None:
        #サンプルデータが実行日付に合わない場合のダミーデータ
        fishinginfo="★サンプルデータ範囲外のためダミーデータを返送★ 最大数:115、最小数:1、最大長cm:87、最小長cm:8"
        answer=f"{spotinfo}　本日の前後1か月の過去2年間の釣果情報は、{fishinginfo}"
    
    else :
        answer=f"{spotinfo}　本日の前後1か月の過去2年間の釣果情報は、{fishinginfo[0]}"

    #文字列を戻す
    return answer



#------------------------------------------
# /choka エンドポイント
# ここではSpotIDはtb-001とする（木更津沖防波堤）
# Bodyの中身
#  {
#  "FishID":"f001" 
#  "FishName":"魚名",
#  "Size":魚のサイズ,
#  "FishCount": 釣れた魚の数
#  }
#------------------------------------------
@app.route('/choka',methods=['POST'])
def choka():
    try:
        conn = get_conn()
        body = request.get_json()
        fishid = body.get("FishID")
        if not fishid:
            raise ValueError("FishID がリクエストに含まれていません。")
        spotid='tb-001'
        JST = datetime.timezone(datetime.timedelta(hours=9))
        repordate = str(datetime.datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S"))
        #釣果情報登録
        sql="insert into MeetUp2025.FishingInfo (SpotID,FishID,ReportDate,Size,FishCount) VALUES(:spotid,:fishid,:repodate,:size,:fishcount)"
        para={"spotid":spotid,"fishid":fishid,"repodate":repordate,"size":body["Size"],"fishcount":body["FishCount"]}
        rset=conn.execute(text(sql),para)
        conn.commit()
        result={"Message":f"{body["FishName"]}の釣果登録完了"}

    except Exception as e:
        result = {"Message": f"エラー発生: {str(e)}"} 
    
    return Response(json.dumps(result, ensure_ascii=False), content_type="application/json; charset=utf-8")

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True,port=5100)
