

# 脫口秀笑點分析模型 (1~100 分預測)

本專案使用訓練好的 BERT 模型，分析中文脫口秀文本的「笑點程度」，預測一段文字在 1～100 範圍內的幽默分數。

---

## ✅ 使用模型進行預測

### 1. 環境需求

- Python 3.8+
- torch
- transformers
- 可選：有 NVIDIA GPU 可加速推論速度

安裝必要套件：

```bash
pip install torch transformers
```

---

### 2. 模型路徑結構

請確認模型已儲存在以下資料夾中：

```
C:\Users\user\OneDrive\桌面\專題企畫\脫口秀model_classification
│
├── config.json
├── pytorch_model.bin
├── tokenizer_config.json
├── vocab.txt
└── special_tokens_map.json
```

---

### 3. 推論程式（`predict.py`）

```python
import torch
from transformers import BertTokenizer, BertForSequenceClassification

# 模型路徑
MODEL_PATH = r"C:\Users\user\OneDrive\桌面\專題企畫\脫口秀model_classification"

# 自動偵測 GPU 或 CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 載入 tokenizer 和 model 並移至裝置
tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
model = BertForSequenceClassification.from_pretrained(MODEL_PATH)
model.to(device)
model.eval()

def predict_score(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    pred_label = torch.argmax(logits, dim=1).item()
    score = pred_label + 1  # 分數範圍為 1~100
    return score

if __name__ == "__main__":
    sample_text = "所以我今年花了一段時間我寫了一段我個人認為他全台灣沒有人在乎的一個主題..."
    score = predict_score(sample_text)
    print(f"預測笑點分數：{score}")
```

---

### 4. 模型輸出說明

- 模型輸出一個整數分數 `1~100`，代表段子預測的笑點強度。
- 分數越高代表越「有趣」、「引人發笑」。

---

### 5. 加速建議

若電腦有 NVIDIA GPU，程式會自動使用 CUDA 執行，大幅提升推論速度。

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
```

---

### 6. 預測範例輸出

```
預測笑點分數：67
```

---

### 7. 聯絡資訊

專案作者：  
專題主題：脫口秀笑點預測 AI  
如需協助請聯絡...
