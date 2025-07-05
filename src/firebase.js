// firebase.js

import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";

// ✅ Firebase 設定資訊（你提供的）
const firebaseConfig = {
  apiKey: "AIzaSyAmsv2bGNq1_-C1LqSfFy45yS5LyxkXlvw",
  authDomain: "myfirstproject-11721.firebaseapp.com",
  projectId: "myfirstproject-11721",
  storageBucket: "myfirstproject-11721.firebasestorage.app",
  messagingSenderId: "210711261300",
  appId: "1:210711261300:web:ddf3b851ba0aee7d6ba121",
  measurementId: "G-EC5R6G7GGH"
};

// ✅ 初始化 Firebase
const app = initializeApp(firebaseConfig);

// ✅ 啟用 Analytics（如果你需要）
const analytics = getAnalytics(app);

export { app, analytics };
