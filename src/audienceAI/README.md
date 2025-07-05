# feedback.py
Real-Time Audience AI Feedback System
real-time speech recognition and AI response system that listens to live audio input from a microphone, transcribes it into text using Google Cloud Speech-to-Text, and generates short, casual replies from multiple simulated "audience personalities" powered by Gemini 1.5 (Google Generative AI).
It is designed to simulate an interactive livestream audience that responds naturally to the speaker's voice input.

Workflow Summary{
1.Microphone Input
Captures live audio using pyaudio and buffers it in chunks for streaming recognition.
2.Speech Recognition
Uses Google Cloud Speech-to-Text to transcribe Mandarin (zh-TW) speech into live text.
3.Gemini AI Interaction
Each "audience member" has a unique behavior prompt (e.g., like a Roger viewer, or Toyz fan).
When speech ends or the user is idle, the transcript is sent to Gemini 1.5 sessions to generate short replies.
4.Engagement Simulation
Each audience member has an engagement_level (probability of responding). This value can go down after idling, creating natural variation in responsiveness.
5.Emit to Server
The collected AI responses are sent to a backend server via Socket.IO (feedback event) to be displayed in the frontend (e.g., a fake chatroom).
}

How to run: python feedback.py
