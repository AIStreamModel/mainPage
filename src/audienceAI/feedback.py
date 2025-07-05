import os
import queue
import threading
import time
import pyaudio
import random
from google.cloud import speech
import google.generativeai as genai
import signal
import sys
import json
import io
import socketio

# 初始化 Socket.io
sio = socketio.Client()
sio.connect("http://localhost:5000")

# 傳送資料給前端
def send_to_server(json_data):
    sio.emit('feedback', json_data)

# 修正輸出編碼
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

# 金鑰與參數設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(BASE_DIR, "dark-bindery-460212-q0-bee5668840a0.json")
genai.configure(api_key="AIzaSyCraB2L_7kSW9iSX5t-Hi8IXG6-cXAuUqE")

RATE = 16000
CHUNK = int(RATE / 10)  # 1600

# 初始化 Gemini 模型
gemini_model = genai.GenerativeModel("gemini-1.5-pro")

# 建立觀眾角色
def create_chat_session(prompt):
    return gemini_model.start_chat(history=[
        {"role": "user", "parts": [prompt]},
        {"role": "model", "parts": ["了解 現在開始進入角色模式囉 簡短回復 口語化 不要顯示心聲 不要表現像AI 不要有表情符號 不要有()符號出現在回應 不要超過二十個字"]}
    ])

audience_profiles = {
    "統神": {"session": create_chat_session("你是阿滴英文的觀眾，叫他播播"), "engagement_level": 1.0},
    "羅傑觀眾": {"session": create_chat_session("你是羅傑直播觀眾，叫他播播"), "engagement_level": 1.0},
    "Toyz": {"session": create_chat_session("你是Toyz觀眾，叫他主播"), "engagement_level": 1.0},
    "愛莉莎莎": {"session": create_chat_session("你是愛莉莎莎的觀眾"), "engagement_level": 1.0},
    "小日刀口": {"session": create_chat_session("你是小日刀口的觀眾，叫他媽斯塔"), "engagement_level": 1.0},
    "國動": {"session": create_chat_session("你是國動的觀眾，叫他帥勾"), "engagement_level": 1.0},
    "詩人": {"session": create_chat_session("你是個好奇心強的詩人型觀眾"), "engagement_level": 1.0},
    "羅傑": {"session": create_chat_session("你是協咖型羅傑觀眾，叫他播播"), "engagement_level": 1.0}
}

# 問 Gemini 得到觀眾回應
def ask_gemini(message):
    replies = []
    for name, profile in audience_profiles.items():
        if random.random() < profile["engagement_level"]:
            try:
                reply = profile["session"].send_message(message).text
                replies.append(f"[{name}]: {reply}")
            except Exception as e:
                replies.append(f"[{name}]: ⚠️ 回應失敗：{e}")
    return "\n".join(replies) if replies else ""

# 麥克風串流
class MicrophoneStream:
    def __init__(self, rate, chunk):
        self.rate = rate
        self.chunk = chunk
        self.closed = True
        self._buff = queue.Queue()
        self._audio_interface = pyaudio.PyAudio()

    def __enter__(self):
        self._stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
            stream_callback=self._callback,
        )
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._stream.stop_stream()
        self._stream.close()
        self._audio_interface.terminate()
        self.closed = True

    def _callback(self, in_data, frame_count, time_info, status_flags):
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            data = self._buff.get()
            if data is None:
                return
            yield data

# 語音辨識主邏輯
def listen_print_loop(responses):
    last_transcript = ""
    speech_end_timer = None
    IDLE_SECONDS = 10
    SPEECH_GAP = 0.8

    def lower_engagement_all():
        for p in audience_profiles.values():
            p["engagement_level"] = max(0.2, p["engagement_level"] - 0.2)

    def reset_engagement_all():
        for p in audience_profiles.values():
            p["engagement_level"] = 1.0

    def on_speech_end():
        nonlocal last_transcript
        if last_transcript.strip() != "":
            print(f"\n[speech end] 辨識完成：{last_transcript}")
            reply = ask_gemini(last_transcript)
            result_data = {
                "type": "response",
                "transcript": last_transcript,
                "aiReplies": reply.split("\n")
            }
            print(json.dumps(result_data, ensure_ascii=False), flush=True)
            send_to_server(result_data)
            if len(last_transcript) > 8:
                reset_engagement_all()
            last_transcript = ""

    def reset_speech_end_timer():
        nonlocal speech_end_timer
        if speech_end_timer:
            speech_end_timer.cancel()
        speech_end_timer = threading.Timer(SPEECH_GAP, on_speech_end)
        speech_end_timer.start()

    def on_idle():
        print("[idle] 10秒內無語音輸入 自動觸發觀眾回應")
        lower_engagement_all()
        reply = ask_gemini("......")
        result_data = {
            "type": "response",
            "transcript": "......",
            "aiReplies": reply.split("\n")
        }
        print(json.dumps(result_data, ensure_ascii=False), flush=True)
        send_to_server(result_data)

    def reset_idle_timer():
        global idle_timer
        if idle_timer:
            idle_timer.cancel()
        idle_timer = threading.Timer(IDLE_SECONDS, on_idle)
        idle_timer.start()

    print("[listen] 開始接收辨識結果")
    try:
        for response in responses:
            if not response.results:
                continue
            result = response.results[0]
            transcript = result.alternatives[0].transcript.strip()
            if transcript != "":
                last_transcript = transcript
                reset_speech_end_timer()
                reset_idle_timer()

            if result.is_final:
                print(f"[final] {transcript}")

        if idle_timer:
            idle_timer.cancel()
        if speech_end_timer:
            speech_end_timer.cancel()

    except Exception as e:
        print(f"\n[listen] 錯誤：{e}")

# 控制是否繼續執行的旗標
running = True

# SIGTERM 結束訊號處理
def signal_handler(sig, frame):
    global running
    print('[feedback.py] 收到 SIGTERM，正在結束')
    running = False

signal.signal(signal.SIGTERM, signal_handler)

# 主辨識流程
def main():
    client = speech.SpeechClient()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="zh-TW",
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True
    )

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        request_queue = queue.Queue()

        def fill_queue():
            for content in audio_generator:
                request_queue.put(speech.StreamingRecognizeRequest(audio_content=content))

        def request_generator():
            while running:
                chunk = request_queue.get()
                if chunk is None:
                    break
                yield chunk

        threading.Thread(target=fill_queue, daemon=True).start()

        try:
            responses = client.streaming_recognize(streaming_config, request_generator())
            listen_print_loop(responses)
        except Exception as e:
            print(f"[main] API 錯誤：{e}")

# 主迴圈
if __name__ == "__main__":
    while running:
        main()
        print("🔄 重啟辨識串流中...\n")
        time.sleep(1)

    sio.disconnect()
    print("✅ 已中止辨識並關閉 socket.io")
