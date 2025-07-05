import torch
from transformers import BertTokenizer, BertForSequenceClassification

# 模型路徑
MODEL_PATH = r"C:\Users\j3000\Desktop\AIStreamer\project\ai-livestream\src\score_system-main\脫口秀model_classification"

# 自動偵測 GPU 或 CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 載入 tokenizer 和 model 並移至裝置
tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
model = BertForSequenceClassification.from_pretrained(MODEL_PATH)
model.to(device)
model.eval()

def predict_score(text):
    # Tokenize 並將張量移到正確的裝置上
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    logits = outputs.logits
    pred_label = torch.argmax(logits, dim=1).item()
    score = pred_label + 1  # 轉回 1~100 分
    return score

if __name__ == "__main__":
    sample_text = "所以我今年花了一段時間我寫了一段我個人認為他全台灣沒有人在乎的一個主題也因此沒有人會生氣所以接下來在20分鐘我想要跟各位分享的主題叫做台海戰爭怎麼樣有人覺得自己在乎台海戰爭的嗎覺得自己在乎台海戰爭的可以麻煩舉個手讓我認識一下嗎覺得自己在乎台海戰在我看到那邊一位兩位OK太好了我沒有各位數的觀眾覺得自己在乎台海戰爭剛剛這邊舉手在哪邊可以再再舉一次OK好我問一個問題已經跟你講好了2027年中國可能會打過來請問你做了什麼準備我先自手我寫了一段就這樣"
    score = predict_score(sample_text)
    print(f"預測笑點分數：{score}")