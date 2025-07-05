# 表情偵測並傳送給 bot_response
import torch
from pathlib import Path
from torch import nn
from emonet.models import EmoNet
import cv2
import numpy as np
import socketio

sio = socketio.Client()
sio.connect("http://localhost:5000")

n_expression = 8
device = "cuda" if torch.cuda.is_available() else "cpu"
image_size = 256
emotion_classes = {0:"Neutral", 1:"Happy", 2:"Sad", 3:"Surprise", 4:"Fear", 5:"Disgust", 6:"Anger", 7:"Contempt"}

state_dict_path = Path(__file__).parent / 'pretrained' / f'emonet_{n_expression}.pth'
print(f'Loading model from {state_dict_path}')
state_dict = torch.load(str(state_dict_path), map_location=device)
state_dict = {k.replace('module.',''):v for k,v in state_dict.items()}

net = EmoNet(n_expression=n_expression).to(device)
net.load_state_dict(state_dict, strict=False)
net.eval()

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image_rgb = cv2.resize(image_rgb, (image_size, image_size))
    image_tensor = torch.Tensor(image_rgb).permute(2,0,1).to(device) / 255.0

    with torch.no_grad():
        output = net(image_tensor.unsqueeze(0))
        pred_idx = torch.argmax(nn.functional.softmax(output["expression"], dim=1)).cpu().item()
        val = output["valence"].clamp(-1.0, 1.0).cpu().item()
        aro = output["arousal"].clamp(-1.0, 1.0).cpu().item()

    label = f"{emotion_classes[pred_idx]}  V:{val:.2f} A:{aro:.2f}"
    cv2.putText(frame, label, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
    cv2.imshow("Real-Time Emotion Detection", frame)

    emotion_data = {
        "type": "emotion",
        "emotion": emotion_classes[pred_idx],
        "valence": val,
        "arousal": aro
    }
    sio.emit("feedback", emotion_data)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
