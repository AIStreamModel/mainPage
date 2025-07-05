# 引入所需模組
import socketio                     # 用於與後端 server 進行實時雙向溝通
import google.generativeai as genai  # Google Gemini API 模組
import os                          # 處理檔案與路徑
import json                        # 處理 JSON 資料
import random                      # 用於隨機選擇與機率判斷
import threading                   # 建立非同步執行緒
import time                        # 取得目前時間

# 設定 Google 認證與 API 金鑰（API 金鑰記得保密！）
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(__file__), "dark-bindery-460212-q0-bee5668840a0.json")
genai.configure(api_key="AIzaSyCraB2L_7kSW9iSX5t-Hi8IXG6-cXAuUqE")

# 載入 Gemini 模型（選用 Gemini 1.5 Pro 版本）
gemini_model = genai.GenerativeModel("gemini-1.5-pro")

# 建立一組 Gemini 對話會話（角色扮演模式），模擬觀眾風格
def create_chat_session(prompt):
    return gemini_model.start_chat(history=[
        {"role": "user", "parts": [prompt]},
        {"role": "model", "parts": ["了解 現在開始進入角色模式囉 簡短回復 口語化 不要顯示心聲 不要表現像AI 不要有表情符號 不要超過二十個字"]}
    ])

# 根據當前時間，自動給出「符合時段」的打招呼語
def get_time_based_greeting():
    current_hour = time.localtime().tm_hour
    if 0 <= current_hour < 5:
        return "挖 這個時間點開直播 主播睡不著？"
    elif 5 <= current_hour < 10:
        return "現在是早餐台嗎？"
    elif 10 <= current_hour < 12:
        return "早安 準備開工啦？"
    elif 12 <= current_hour < 14:
        return "午餐吃了沒？"
    elif 14 <= current_hour < 17:
        return "下午來偷閒一下"
    elif 17 <= current_hour < 20:
        return "下班了來看台～"
    elif 20 <= current_hour < 24:
        return "晚上的直播最有感覺"
    else:
        return "安安"

# 建立虛擬觀眾角色設定，每位觀眾有對應個性與出現機率
audience_profiles = {
    "統神": {
        "session": create_chat_session("你是擁有阿滴英文觀眾性格的觀眾AI 喜歡稱呼阿滴為播播"),
        "engagement_level": 1.0
    },
    "羅傑觀眾": {
        "session": create_chat_session("你是擁有羅傑直播觀眾的觀眾性格的觀眾AI 喜歡稱呼羅傑為播播"),
        "engagement_level": 1.0
    },
    "Toyz": {
        "session": create_chat_session("你是擁有youtuber(Toyz)觀眾性格的觀眾AI 喜歡叫椅子為主播"),
        "engagement_level": 1.0
    },
    "愛莉莎莎": {
        "session": create_chat_session("你是擁有youtuber(愛莉莎莎)觀眾性格的觀眾AI"),
        "engagement_level": 1.0
    },
    "小日刀口": {
        "session": create_chat_session("你是擁有youtuber(小日刀口)觀眾性格的觀眾AI 喜歡稱呼小日刀口為媽斯塔"),
        "engagement_level": 1.0
    },
    "國動": {
        "session": create_chat_session("你是擁有youtuber(國動)觀眾性格的觀眾AI 喜歡稱國動為帥勾"),
        "engagement_level": 1.0
    },
    "詩人": {
        "session": create_chat_session("我要你扮演詩人個性很愛向他人詢問問題充滿好奇心的觀眾AI"),
        "engagement_level": 1.0
    },
    "羅傑": {
        "session": create_chat_session("你是擁有羅傑直播觀眾的觀眾性格的觀眾AI 個性很協咖 很會開玩笑 喜歡稱呼羅傑為播播"),
        "engagement_level": 1.0
    }
}

# 英文情緒轉換為中文顯示（給 Gemini 輸出參考）
emotion_translate = {
    "Happy": "開心",
    "Sad": "難過",
    "Neutral": "冷靜",
    "Surprise": "驚訝",
    "Fear": "害怕",
    "Disgust": "厭惡",
    "Anger": "生氣",
    "Contempt": "輕蔑"
}

cached_emotion = None     # 暫存最近的情緒結果
has_greeted = False       # 判斷是否已經打過招呼（只打一次）

# 核心：產生 AI 虛擬觀眾回應
def ask_gemini_delayed(message, emotion=None):
    def respond_later(name, profile, delay):
        time.sleep(delay)
        try:
            # 若有表情資訊，會放入提示詞中
            prompt = f"(表情:{emotion}) {message}" if emotion else message
            reply = profile["session"].send_message(prompt).text
            # 將回應送回 server（前端顯示）
            sio.emit("feedback", {
                "type": "response",
                "transcript": message,
                "aiReplies": [f"[{name}]: {reply}"]
            })
            print(f"[{name}]: {reply}")
        except Exception as e:
            print(f"[{name}]: 回應失敗：{e}")

    # 每位觀眾有延遲出現時間（5~10秒起跳），觀眾間也會有 0.5 秒間隔
    delay_base = random.uniform(5, 10)
    delay_offset = 0.0

    for name, profile in audience_profiles.items():
        if random.random() < (0.6 * profile.get("engagement_level", 1.0)):
            delay = delay_base + delay_offset
            threading.Thread(target=respond_later, args=(name, profile, delay)).start()
            delay_offset += 0.5

# 建立 SocketIO 客戶端並連接 server
sio = socketio.Client()
sio.connect("http://localhost:5000")  # ✅ 已移除監聽 silence 的部分

# 當收到 server 傳來的資料時，根據類型處理
@sio.on("feedback")
def on_feedback(data):
    global cached_emotion, has_greeted

    if data.get("type") == "transcript":
        print(f"[recv] transcript: {data['text']}")

        # 第一次收到發言時，先打招呼
        if not has_greeted:
            greeting = get_time_based_greeting()
            has_greeted = True
            ask_gemini_delayed(greeting)
            time.sleep(1.5)

        # 接續處理用戶輸入的文字與情緒
        emotion = cached_emotion
        cached_emotion = None
        ask_gemini_delayed(data['text'], emotion)

    elif data.get("type") == "emotion":
        print(f"[recv] emotion: {data['emotion']}, V:{data['valence']}, A:{data['arousal']}")
        english = data['emotion']
        # 將英文情緒翻譯為中文並暫存
        cached_emotion = emotion_translate.get(english, english)
        print(f"暫存情緒：{cached_emotion}")
