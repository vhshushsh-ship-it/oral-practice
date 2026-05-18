// ========== 前端工具函数 utils.js ==========

// 扬声器图标 SVG
const SPEAKER_ICON = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>`;

// 收藏书签图标 SVG
const BOOKMARK_ICON = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>`;

// 过滤文本中的表情符号
        function removeEmojis(text) {
            // 匹配所有常见emoji的正则表达式（覆盖绝大部分表情符号）
            const emojiRegex = /[\u{1F600}-\u{1F6FF}\u{1F300}-\u{1F5FF}\u{1F900}-\u{1F9FF}\u{1F1E0}-\u{1F1FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{FE00}-\u{FE0F}]/gu;
            // 移除表情符号并去除首尾空格
            return text.replace(emojiRegex, '').trim();
        }

// speakText 函数（先过滤表情再朗读）
        function speakText(text) {
            if (!text) return;
            const cleanText = removeEmojis(text);
            if (!cleanText) return;

            window.speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(cleanText);
            utterance.lang = "en-US";
            const rateSelect = document.getElementById("speechRateSelect");
            utterance.rate = rateSelect ? parseFloat(rateSelect.value) : 1.0;

            // 单次微任务让 cancel 生效后立即播放，消除轮询延迟
            setTimeout(() => {
                window.speechSynthesis.speak(utterance);
            }, 0);
        }

// 倒计时格式化
        function formatTime(seconds) {
            const m = Math.floor(seconds / 60).toString().padStart(2, '0');
            const s = (seconds % 60).toString().padStart(2, '0');
            return `${m}:${s}`;
        }


// 启动录音UI
        function startRecordingUI() {
            cancelRecordingFlag = false;
            recordBtn.style.display = "none";
            stopBtn.style.display = "inline-block";
            cancelBtn.style.display = "inline-block";
            waveform.style.display = "flex";
            recordTimer.style.display = "inline";
            recordingSeconds = 0;
            recordTimer.textContent = "00:00";
            // 启动倒计时
            recordingTimer = setInterval(() => {
                recordingSeconds++;
                recordTimer.textContent = formatTime(recordingSeconds);
            }, 1000);
        }


// 停止录音UI
        function stopRecordingUI() {
            if (recordingTimer) clearInterval(recordingTimer);
            waveform.style.display = "none";
            recordTimer.style.display = "none";
            stopBtn.style.display = "none";
            cancelBtn.style.display = "none";
            recordBtn.style.display = "inline-block";
            recordingSeconds = 0;
        }

        // 新增：取消录音

// resample 音频重采样
        function resample(audioData, fromSampleRate, toSampleRate) {
            const ratio = fromSampleRate / toSampleRate;
            const newLength = Math.round(audioData.length / ratio);
            const result = new Float32Array(newLength);
            for (let i = 0; i < newLength; i++) {
                const index = i * ratio;
                const floor = Math.floor(index);
                const ceil = Math.ceil(index);
                const t = index - floor;
                result[i] = ceil >= audioData.length ? audioData[floor] : audioData[floor] * (1 - t) + audioData[ceil] * t;
            }
            return result;
        }

// createWavBlob WAV编码
        function createWavBlob(audioData, sampleRate) {
            const targetSampleRate = 16000;
            const ratio = sampleRate / targetSampleRate;
            const newLength = Math.round(audioData.length / ratio);
            const resampled = new Float32Array(newLength);
            for (let i = 0; i < newLength; i++) {
                const idx = i * ratio;
                const floor = Math.floor(idx);
                const ceil = Math.min(Math.ceil(idx), audioData.length - 1);
                const t = idx - floor;
                resampled[i] = audioData[floor] * (1 - t) + audioData[ceil] * t;
            }
            const pcmData = new Int16Array(resampled.length);
            for (let i = 0; i < resampled.length; i++) {
                const sample = Math.max(-1, Math.min(1, resampled[i]));
                pcmData[i] = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
            }
            const buffer = new ArrayBuffer(44 + pcmData.length * 2);
            const view = new DataView(buffer);
            view.setUint8(0, 0x52); view.setUint8(1, 0x49); view.setUint8(2, 0x46); view.setUint8(3, 0x46);
            view.setUint32(4, 36 + pcmData.length * 2, true);
            view.setUint8(8, 0x57); view.setUint8(9, 0x41); view.setUint8(10, 0x56); view.setUint8(11, 0x45);
            view.setUint8(12, 0x66); view.setUint8(13, 0x6D); view.setUint8(14, 0x74); view.setUint8(15, 0x20);
            view.setUint32(16, 16, true);
            view.setUint16(20, 1, true);
            view.setUint16(22, 1, true);
            view.setUint32(24, targetSampleRate, true);
            view.setUint32(28, targetSampleRate * 2, true);
            view.setUint16(32, 2, true);
            view.setUint16(34, 16, true);
            view.setUint8(36, 0x64); view.setUint8(37, 0x61); view.setUint8(38, 0x74); view.setUint8(39, 0x61);
            view.setUint32(40, pcmData.length * 2, true);
            for (let i = 0; i < pcmData.length; i++) {
                view.setInt16(44 + i * 2, pcmData[i], true);
            }
            return new Blob([view], { type: 'audio/wav' });
        }


