import os
import queue
import threading
import time
import pyaudio
import wave
import torch
import torch.nn.functional as F
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor
from google.cloud import speech
import soundfile as sf
import google.generativeai as genai
import threading

# 設定 API 金鑰（Google Cloud 語音識別）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(BASE_DIR, "dark-bindery-460212-q0-bee5668840a0.json")

# 設定 Gemini API 金鑰（你要填入這裡）
genai.configure(api_key="AIzaSyCraB2L_7kSW9iSX5t-Hi8IXG6-cXAuUqE")
gemini_model = genai.GenerativeModel("gemini-1.5-pro")

# 參數
RATE = 16000
CHUNK = int(RATE / 10)
TEXT_FILE = "text.txt"
ANALYSIS_INTERVAL = 60

# 載入情緒模型
emotion_model_name = "superb/wav2vec2-base-superb-er"
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(emotion_model_name)
emotion_model = Wav2Vec2ForSequenceClassification.from_pretrained(emotion_model_name)
emotion_model.eval()

# 產生文字敘述
def generate_emotion_description(prob):
    # prompt = f"請用自然且千變萬化的中文寫一句話描述他並參考他的情緒機率{prob}。句子不能重複。"
    prompt = f"請用自然且千變萬化的中文寫一句話描述語氣他並參考他的情緒機率{prob}。句子不能重複。不要用具體的形容詞。請用抽象的形容詞。"
    response = gemini_model.generate_content(prompt)
    return response.text.strip()

# 情緒辨識
def emotion_recognition(wav_path):
    speech, sr = sf.read(wav_path)
    if sr != RATE:
        raise ValueError(f"音檔採樣率錯誤，應為 {RATE}，但得到 {sr}")
    inputs = feature_extractor(speech, sampling_rate=RATE, return_tensors="pt", padding=True)
    with torch.no_grad():
        logits = emotion_model(**inputs).logits
        probs = F.softmax(logits, dim=-1)
    labels = emotion_model.config.id2label
    probs_dict = {labels[i]: float(probs[0][i]) for i in range(len(labels))}
    predicted_emotion = labels[torch.argmax(probs, dim=-1).item()]
    return predicted_emotion, probs_dict

# 麥克風錄音
class MicrophoneStream:
    def __init__(self, rate, chunk):
        self.rate = rate
        self.chunk = chunk
        self.closed = True
        self._buff = queue.Queue()
        self._audio_interface = pyaudio.PyAudio()
        self.frames = []

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
        self.frames.append(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            data = self._buff.get()
            if data is None:
                return
            yield data

# 儲存音訊
def save_wav(frames, filename):
    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# 語音轉文字 + 情緒 + 敘述生成
def listen_print_loop(responses, mic_stream):
    # 在開始時清空 text.txt 並啟動第一次分析計時器
    open(TEXT_FILE, "w", encoding="utf-8").close()
    analyze_text_file()
    
    last_transcript = ""
    speech_end_timer = None
    SPEECH_GAP = 0.8

    def on_speech_end():
        nonlocal last_transcript
        if last_transcript.strip() != "":
            print(f"\n[speech end] {last_transcript}")
            # sio.emit('feedback', {"type": "emotion_text", "emotion": emotion, "text": response})
            last_transcript = ""

    def reset_speech_end_timer():
        nonlocal speech_end_timer
        if speech_end_timer:
            speech_end_timer.cancel()
        speech_end_timer = threading.Timer(SPEECH_GAP, on_speech_end)
        speech_end_timer.start()

    print("[listen] 接收中...")
    for response in responses:
        if not response.results:
            continue
        result = response.results[0]
        transcript = result.alternatives[0].transcript.strip()
        if transcript:
            last_transcript = transcript
            # reset_speech_end_timer()
            if result.is_final:
                print(f"[final] {transcript}")
                with open(TEXT_FILE, "a", encoding="utf-8") as f:
                    f.write(transcript + "\n")

                wav_filename = "temp_speech.wav"
                save_wav(mic_stream.frames, wav_filename)
                mic_stream.frames.clear()

                emotion, probs = emotion_recognition(wav_filename)
                print(f"[emotion] {emotion}")
                print(f"[probabilities] {probs}")

                response = generate_emotion_description(probs)
                print(f"[情緒敘述] {response}")

    if speech_end_timer:
        speech_end_timer.cancel()
        
def analyze_text_file():
    print("\n[分析觸發] 正在呼叫 redundancy.py 處理 text.txt...")
    os.system(f'python redundancy.py "{TEXT_FILE}"')
    print("\n[分析觸發] 正在呼叫 punch.py 處理 text.txt...")
    os.system(f'python punchline.py "{TEXT_FILE}"')
    # 清空 text.txt
    open(TEXT_FILE, "w", encoding="utf-8").close()

    # 下一輪再啟動一分鐘後執行
    threading.Timer(ANALYSIS_INTERVAL, analyze_text_file).start()

# 主程式
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

    while True:
        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            request_queue = queue.Queue()

            def fill_queue():
                for content in audio_generator:
                    request_queue.put(speech.StreamingRecognizeRequest(audio_content=content))

            def request_generator():
                while True:
                    chunk = request_queue.get()
                    if chunk is None:
                        break
                    yield chunk

            threading.Thread(target=fill_queue, daemon=True).start()

            try:
                responses = client.streaming_recognize(streaming_config, request_generator())
                listen_print_loop(responses, stream)
            except Exception as e:
                print(f"[main error] {e}")

if __name__ == "__main__":
    main()
