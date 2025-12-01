import os
import json
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModel, AutoTokenizer
import concurrent.futures

HF_MODEL_PATH = 'line-corporation/clip-japanese-base'
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def load():
    global tokenizer, processor, model
    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_PATH, trust_remote_code=True,legacy=True)
    processor = AutoImageProcessor.from_pretrained(HF_MODEL_PATH, trust_remote_code=True)
    model = AutoModel.from_pretrained(HF_MODEL_PATH, trust_remote_code=True).to(DEVICE)
    return model,tokenizer,processor

#---
#画像を一定時間以内に開く。タイムアウト時は例外を返す
#---
def open_image_safely(path, timeout=5):
    def _open_image():
        return Image.open(path)

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_open_image)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            return f"error:画像の読み込みが {timeout} 秒を超えました: {path}"
        except FileNotFoundError:
            return f"error:ファイルが見つかりません: {path}"
        except PermissionError:
            return f"error:ファイルにアクセスできません（権限エラー）: {path}"
        except Exception as e:
            return f"error:画像を開く際に予期せぬエラーが発生しました: {e}"
#----
#画像ファイルのEmbedding
#----
def get_image_embeddings(filefullpath):
    #画像ファイルオープン
    my_image = open_image_safely(filefullpath, timeout=3)
    # 文字列（エラーメッセージ）の場合のみ判定
    if isinstance(my_image, str) and my_image.startswith("error:"):
        return my_image

    # 画像のベクトル取得
    image = processor(images=my_image , return_tensors="pt")
    embedding = model.get_image_features(**image).float()
    # convert the embeddings to numpy array
    imagevector=embedding.cpu().detach().numpy()
    embeddingval=str(imagevector[0].tolist())[1:-1]
    return embeddingval



#----
#テキストのEmbedding
#----
def get_clip_text_embeddings(text):
    # トークナイズ（BatchEncoding -> dictに明示変換 & デバイス転送）
    enc = tokenizer(
        text,                      # バッチ化しておくと形が安定
        padding=True,
        truncation=True,
    )
    enc = {k: v.to(DEVICE) for k, v in enc.items()}  # DEVICEへ

    model.eval()
    with torch.no_grad():
        feats = model.get_text_features(**enc).float()  # [1, D]

    textvector = feats[0].cpu().numpy()
    embeddingval = str(textvector.tolist())[1:-1]
    return embeddingval

#----
#テキストのEmbedding（ファイル出力用）
#----
def get_clip_text_embeddings2(text):
    # トークナイズ（BatchEncoding -> dictに明示変換 & デバイス転送）
    enc = tokenizer(
        text,                      # バッチ化しておくと形が安定
        padding=True,
        truncation=True,
    )
    enc = {k: v.to(DEVICE) for k, v in enc.items()}  # DEVICEへ

    model.eval()
    with torch.no_grad():
        feats = model.get_text_features(**enc).float()  # [1, D]

    textvector = feats[0].cpu().numpy()
    embedding = textvector.tolist()
    return embedding
#----
#テキストファイル作成
#----
def create_load_file():
    with open("/src/fish_documents.jsonl", "r", encoding="utf-8") as f:
        fish_docs = [json.loads(line) for line in f]
    #print(fish_docs)
    clip_text_embeddings = []
    for doc in fish_docs:
        clip_text_embeddings.append(get_clip_text_embeddings2(doc["fishname"]))

    clip_text_vectors = [
        {"fishid":doc["fishid"],"fishname": doc["fishname"], "embedding":embedding}
        for doc, embedding in zip(fish_docs, clip_text_embeddings)
    ]

    with open("/src/fish_clip_vectors.jsonl", "w", encoding="utf-8") as f:
        for item in clip_text_vectors:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    load()
else:
    load()