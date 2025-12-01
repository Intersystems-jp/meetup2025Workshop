Class Sample.RESTCOMPLETEVER Extends %CSP.REST
{

Parameter CONTENTTYPE = "application/json";

Parameter CHARSET = "utf-8";

Parameter CONVERTINPUTSTREAM = 1;

Property key As %String(MAXLEN = "");

XData UrlMap [ XMLNamespace = "http://www.intersystems.com/urlmap" ]
{
<Routes>
<Route Url="/recipe" Method="POST" Call="recipe" Cors="true"/>
<Route Url="/recipe2" Method="POST" Call="recipe2" Cors="true"/>
<Route Url="/upload" Method="POST" Call="upload" Cors="true"/>
<Route Url="/choka" Method="POST" Call="choka" Cors="true"/>
<Route Url="/hello" Method="GET" Call="hello" Cors="true"/>
</Routes>
}

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
    set json.FishName=rset.%Get("Name")
    do json.%ToJSON()
    return $$$OK
}

/// 釣果登録
/// SpotIDは固定：tb-001
/// Body
/// {
///  "FishID":"f001",
///  "FishName":"アジ",
///  "Size":20,
///  "FishCount": 2
/// }
ClassMethod choka() As %Status
{
    #dim %request As %CSP.Request
    set body={}.%FromJSON(%request.Content)
    set sql="insert into MeetUp2025.FishingInfo (SpotID,FishID,ReportDate,Size,FishCount) VALUES(?,?,?,?,?)"
    set stmt=##class(%SQL.Statement).%New()
    set status=stmt.%Prepare(sql)
    set stmt.%SelectMode=1
    set rset=stmt.%Execute("tb-001",body.FishID,$ZDATE($H,3),body.Size,body.FishCount)
    set j={}
    set j.Message=body.FishName_"の釣果登録完了"
    do j.%ToJSON()
    return $$$OK
}

/// Ollama用
/// POSTのボディ
/// {
///  "FishID":"f001",
///  "FishName":"魚名",
///  "UserInput":"希望のレシピの内容"
/// }
/// 魚名からFishIDを入手し、その魚の過去2年間の釣果情報と釣り場の潮位情報を入手し生成AIに渡す
ClassMethod recipe() As %Status
{
    #dim %request As %CSP.Request
    set body={}.%FromJSON(%request.Content)
    // ユーザ入力の魚名から生成AIに渡す補足情報を入手する
    // bodyのJSONに "FishInfo" が追加される
    set status=..GetFishInfo(.body)
    set status=..AskLLM(1,.body,.ans)
    do ans.%ToJSON()
    return $$$OK
}

/// OpenAI用
/// POSTのボディ
/// {
///  "FishID":"f001",
///  "FishName":"魚名",
///  "UserInput":"希望のレシピの内容"
/// }
/// 魚名からFishIDを入手し、その魚の過去2年間の釣果情報と釣り場の潮位情報を入手し生成AIに渡す
ClassMethod recipe2() As %Status
{
    #dim %request As %CSP.Request
    set body={}.%FromJSON(%request.Content)
    // ユーザ入力の魚名から生成AIに渡す補足情報を入手する
    // bodyのJSONに "FishInfo" が追加される
    set status=..GetFishInfo(.body)
    set status=..AskLLM(0,.body,.ans)
    do ans.%ToJSON()
    return $$$OK
}

ClassMethod GetFishInfo(ByRef body As %DynamicArray) As %Status
{
    #dim ex As %Exception.AbstractException
    set status=$$$OK
    try {
        set stmt=##class(%SQL.Statement).%New()
        set fishid=body.FishID

        // 釣り場の情報を取得（木更津沖堤防固定情報：SpotID='tb-001'）
        set sql2="SELECT SpotName||'の状況は、'||TideState||'、'|| TideCycle||'、潮位は'||TideHeightCmRelative||'cm' as result ,SpotID,DatetimeJst"
        set sql2=sql2_" FROM MeetUp2025.BayInfo WHERE SpotID='tb-001' AND DatetimeJst BETWEEN DATEADD(hour,-1,?) AND ?"
        // 現在のローカルタイムスタンプ
        set ts=##class(%UTC).NowLocal()
        set stmt.%SelectMode=1  //ODBCモード
        $$$ThrowOnError(stmt.%Prepare(sql2))
        set rset=stmt.%Execute(ts,ts)
        do rset.%Next()
        set result=rset.%Get("result")
        //サンプルデータ範囲外の場合の対応（潮位データは2026/9/9まで）
        if result="" {
            set spotinfo=rset.DatetimeJst_" ★サンプルデータ範囲外のためダミーデータを返送★ 釣り場：木更津沖堤防 下げ潮、若潮、潮位は28.5cm"  
        }
        else {
            set spotinfo=rset.DatetimeJst_" 釣り場："_result
        }

        // 過去の釣り情報（木更津沖堤防固定情報：SpotID='tb-001'）
        // 過去2年、指定日付の月前後1か月の釣り情報
        set sql3="SELECT '最大数:'||MAX(FishCount)||'、最小数:'||MIN(FishCount)||'、最大長cm:'||MAX(Size)||'、最小長cm:'||MIN(Size) as result"
        set sql3=sql3_" FROM MeetUp2025.FishingInfo WHERE FishID=? AND SpotID='tb-001' AND (ReportDate >= DATEADD(yyyy,-2,?) AND (DATEPART(mm,ReportDate) BETWEEN DATEPART(mm,?)-1 AND DATEPART(mm,?)+1))"
        $$$ThrowOnError(stmt.%Prepare(sql3))
        set now=$ZDATE($Horolog,3)
        set rset=stmt.%Execute(fishid,now,now,now)
        do rset.%Next()
        set fishinginfo=rset.%Get("result")
        set body.FishInfo=$Get(spotinfo)

        if $GET(fishinginfo)'="" {
            set body.FishInfo=$Get(spotinfo)_"　本日の前後1か月の過去2年間の釣果情報は、"_$Get(fishinginfo)
        }
        else {
            //サンプルデータ範囲外の場合ダミーをセット     
            set body.FishInfo=$Get(spotinfo)_"　本日の前後1か月の過去2年間の釣果情報は、★サンプルデータ範囲外のためダミーデータを返送★ 最大数:115、最小数:1、最大長cm:87、最小長cm:8"
        }
    }
    catch ex {
        set status=ex.AsStatus()
    }
    return status
}

ClassMethod hello() As %Status
{
    set json={}
    set json.RetMessage="あいうえお"
    do json.%ToJSON()
    return $$$OK
}

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
        set prompt.content="魚名は"_body.FishName_"。fishinfo:"_body.FishInfo
        do sendjson.messages.%Push(prompt)
        set prompt={}
        /* === prompt.contet にUserInputの内容を設定します*/
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
            set sendjson.options=options
        }
        // OpenAI
        if flg'=1 {
            set req.Server="api.openai.com"
            set req.Location="/v1/chat/completions"
            //モデルの指定
            set sendjson.model="gpt-4o"
            set key=..setAPIKey()
            //https通信用指定
            set req.SSLConfiguration="webapi"
            set req.Https=1
            //APIキーのセット
            do req.SetHeader("Authorization","Bearer "_key)
        }
        //body
        do sendjson.%ToJSON(req.EntityBody)
        //w req.EntityBody.Read(),!
        //w w req.EntityBody.Rewind()

        $$$ThrowOnError(req.Post())
        set response=req.HttpResponse
        if response.StatusCode'=200&(response.StatusCode'=202) {
            set errmessage=response.Data.Read()
            set status=$system.Status.Error(5001,errmessage)
            return status
        }

        set resjson={}.%FromJSON(response.Data)
        /* LLM毎回答が異なる*/
        //Ollama
        if flg=1 {
            set ans.Message=resjson.message.content
        }
        //OpenAI
        if flg'=1 {
            set ans.Message=resjson.choices."0".message.content   
        }
        set ans.FishInfo=body.FishInfo
    }
    catch ex {
        set status=ex.AsStatus()
    }
    return status
}

/// /src/wsgi/config.pyに記載しているOpenAIのAPIキーを入手して戻す
ClassMethod setAPIKey() As %String(MAXLEN="")
{
    set sys=##class(%SYS.Python).Import("sys")
    do sys.path.append("/src/wsgi")
    set config=##class(%SYS.Python).Import("config")
    return config.key
}

ClassMethod setdata(body As %DynamicAbstractObject) As %DynamicAbstractObject
{
        set sendjson={}
        set sendjson.messages=[]
        set prompt={}
        set prompt.role="system"
        set prompt.content="あなたは釣りのスペシャリストで釣り場の地元料理をよく知っています。本日釣った魚名、体長、ユーザの状況、過去の釣果情報を参考情報として30分程度で作れる地元レシピを教えてください。"
        do sendjson.messages.%Push(prompt)
        set prompt={}
        set prompt.role="user"
        set prompt.contet="魚名は"_body.FishName_"。"_body.FishInfo
        do sendjson.messages.%Push(prompt)
        set prompt={}
        set prompt.role="user"
        set prompt.content=body.UserInput
        do sendjson.messages.%Push(prompt)
        //request
        set req=##class(%Net.HttpRequest).%New()
        set req.ContentType="application/json"
        set req.ContentCharset="utf-8"
        //body
        do sendjson.%ToJSON(req.EntityBody)
        do sendjson.%ToJSON()
        return sendjson
}

}
