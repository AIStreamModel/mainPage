import os
import sys
import google.generativeai as genai

# 設定 Gemini API 金鑰
genai.configure(api_key="AIzaSyB8TulKhTl8U9iAghPlC0vR7WpzcY3t0IQ")
gemini_model = genai.GenerativeModel("gemini-1.5-pro")

# 贅詞分析函式
def analyze_filler_words_with_gemini(text):
    prompt = f"""
你是一位中文寫作教練。請幫我分析以下這段口語內容是否出現過多的贅詞（例如：就是、然後、那個、其實、我覺得、你知道、欸...等）。
請幫我判斷以下中文內容中的贅詞是否有必要出現。
判斷每個贅詞是否必要「是否幫助語氣自然」或「是否屬於拖時間、沒幫助理解」。
假如是必要則總出現的贅詞與次數不需要+1。

請回覆以下格式：
比例:??%
=====================================================
1. 出現的贅詞與次數（例如：「就是」出現3次、「然後」出現2次）
2. 總字數與贅詞比例
3. 說明

---內容開始---
{text}
---內容結束---
"""
    response = gemini_model.generate_content(prompt)
    return response.text.strip()

# 主程式
if __name__ == "__main__":
    input_path = "text.txt" if len(sys.argv) == 1 else sys.argv[1]

    if not os.path.exists(input_path):
        print(f"[錯誤] 找不到檔案：{input_path}")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        print("[警告] 檔案為空，略過分析。")
        sys.exit(0)

    print(f"\n[分析開始] 檔案：{input_path}")
    result = analyze_filler_words_with_gemini(content)
    print("\n[贅詞分析結果]")
    print(result)