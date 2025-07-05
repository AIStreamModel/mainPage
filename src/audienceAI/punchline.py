import os
import google.generativeai as genai

# 設定 Gemini API 金鑰
genai.configure(api_key="AIzaSyCraB2L_7kSW9iSX5t-Hi8IXG6-cXAuUqE")
gemini_model = genai.GenerativeModel("gemini-1.5-pro")

def analyze_punchlines(text):
    prompt = f"""
以下是一段脫口秀文本。請幫我從中找出所有 punchline（讓觀眾笑的那一句），並針對每一句 punchline 簡要說明為什麼會讓人發笑。
說出有幾個punchline
請回覆格式如下：
1. 總共偵測到:??
2. 每一句 punchline + 原因

---文本開始---
{text}
---文本結束---
"""
    response = gemini_model.generate_content(prompt)
    return response.text.strip()

def main():
    input_path = "text.txt"

    if not os.path.exists(input_path):
        print(f"[錯誤] 找不到檔案：{input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        print("[警告] 檔案為空，略過分析。")
        return

    print("[開始進行 punchline 分析...]\n")
    result = analyze_punchlines(content)
    print(result)

if __name__ == "__main__":
    main()
