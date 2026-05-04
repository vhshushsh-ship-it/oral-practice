import React, { useState, useRef } from "react";
import axios from "axios";

function App() {
  const [recording, setRecording] = useState(false);
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    mediaRecorder.current = new MediaRecorder(stream);
    audioChunks.current = [];

    mediaRecorder.current.ondataavailable = e => {
      audioChunks.current.push(e.data);
    };

    mediaRecorder.current.onstop = async () => {
      const blob = new Blob(audioChunks.current, { type: "audio/wav" });

      const formData = new FormData();
      formData.append("audio", blob);

      const res = await axios.post("http://localhost:8000/chat", formData);

      console.log("用户：", res.data.text);
      console.log("AI：", res.data.reply);

      speak(res.data.reply);
    };

    mediaRecorder.current.start();
    setRecording(true);
  };

  const stopRecording = () => {
    mediaRecorder.current.stop();
    setRecording(false);
  };

  // ===== 浏览器真人语音 =====
  const speak = (text) => {
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = "en-US";
    speechSynthesis.speak(utter);
  };

  return (
    <div style={{ textAlign: "center", marginTop: 100 }}>
      <h1>🎤 AI口语练习</h1>

      <button
        onMouseDown={startRecording}
        onMouseUp={stopRecording}
        style={{
          padding: "20px",
          fontSize: "18px",
          background: recording ? "red" : "green",
          color: "white",
          borderRadius: "10px"
        }}
      >
        {recording ? "🎙️ 说话中..." : "按住说话"}
      </button>
    </div>
  );
}

export default App;