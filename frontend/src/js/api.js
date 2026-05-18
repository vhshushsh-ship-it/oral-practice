// ========== 后端API请求封装 api.js ==========

const API_BASE = "http://127.0.0.1:8000";

// ====================== 句子翻译 API ======================
// 中文→英文翻译
        async function translateSentence() {
            const text = translateInput.value.trim();
            if (!text) {
                alert("请输入中文句子");
                return;
            }
            translateResult.textContent = "翻译中...";
            copyTranslateBtn.style.display = "none";
            try {
                // 仅修改这一行：从/translate改为/translate_to_en
                const res = await fetch(`${API_BASE}/translate_to_en`, {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: `text=${encodeURIComponent(text)}`
                });
                const data = await res.json();
                if (data.translation) {
                    translateResult.textContent = data.translation;
                    copyTranslateBtn.style.display = "inline-block";
                } else {
                    translateResult.textContent = "翻译失败，请重试";
                }
            } catch (err) {
                console.error("翻译失败:", err);
                translateResult.textContent = "翻译失败，请检查网络连接";
            }
        }

// ====================== 场景聊天 API ======================
// 加载场景聊天记录
        async function loadSceneHistory() {
            try {
                const historyStr = localStorage.getItem(`chat_history_${currentScene}`);
                const history = historyStr ? JSON.parse(historyStr) : [];
                chatBox.innerHTML = "";
                translateBox.innerHTML = "";
                conversationHistory = [...history];
                for (let item of history) {
                    if (item.role === "user") {
                        addMessage(item.content, true);
                    } else if (item.role === "assistant") {
                        addMessage(item.content, false);
                    }
                }
            } catch (err) {
                console.error("加载历史记录失败:", err);
            }
        }

// 保存场景聊天记录
        async function saveSceneHistory() {
            try {
                localStorage.setItem(`chat_history_${currentScene}`, JSON.stringify(conversationHistory));
            } catch (err) {
                console.error("保存历史记录失败:", err);
            }
        }

// 初始化场景
        async function initScene() {
            const sceneChoice = sceneSelect.value;
            try {
                const res = await fetch(`${API_BASE}/init`, {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: `scene_choice=${sceneChoice}`
                });
                const data = await res.json();
                currentScene = data.scene;
                await loadSceneHistory();
                if (conversationHistory.length === 0) {
                    const welcomeText = data.initial_message;
                    conversationHistory.push({ "role": "assistant", "content": welcomeText });
                    addMessage(welcomeText, false);
                    speakText(welcomeText);
                }
            } catch (err) {
                console.error("初始化场景失败:", err);
                addMessage("Sorry, the scene failed to load. Please refresh.", false);
            }
        }

// ====================== 翻译接口 ======================
        async function addTranslation(text, isUser) {
            try {
                const res = await fetch(`${API_BASE}/translate`, {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: `text=${encodeURIComponent(text)}`
                });
                const data = await res.json();
                const translateDiv = document.createElement("div");
                translateDiv.className = "translate-item";
                translateDiv.innerHTML = `
                    <div class="source">${isUser ? "You: " : "AI: "}${text}</div>
                    <div class="target">${data.translation}</div>
                `;
                translateBox.appendChild(translateDiv);
                translateBox.scrollTop = translateBox.scrollHeight;
            } catch (err) {
                console.error("翻译失败:", err);
            }
        }


// ====================== 单词查询 API ======================
        async function searchWord() {
            const word = wordInput.value.trim().toLowerCase();
            if (!word) {
                wordResult.innerHTML = "<p style='color:var(--accent);'>请输入英文单词</p>";
                return;
            }
            wordResult.innerHTML = "<p style='text-align:center; color:var(--ink-muted);'>AI查询中...</p>";
            try {
                const res = await fetch(`${API_BASE}/word/query?word=${encodeURIComponent(word)}`, {
                    method: "POST"
                });
                if (!res.ok) throw new Error(`请求失败，状态码：${res.status}`);
                const data = await res.json();
                if (data.error) {
                    wordResult.innerHTML = `<p style='color:var(--accent); text-align:center;'>${data.error}</p>`;
                    return;
                }
                const wordName = data.word || word;
                const phonetic = data.phonetic || "无音标";
                const meanings = data.meanings || [];
                let html = `
                    <h3 class="word-title">${wordName}</h3>
                    <div class="word-phonetic" data-word="${wordName}"><span class="speak-btn">${SPEAKER_ICON}</span> ${phonetic}</div>
                    <button class="add-word-btn" id="addWordBtn">加入单词笔记</button>
                `;
                if (meanings.length > 0) {
                    html += `<div class="word-meanings"><h4>释义与例句</h4>`;
                    meanings.forEach((item, idx) => {
                        let exampleHtml = "";
                        if (item.example) {
                            const exampleParts = item.example.split("|");
                            const exampleEn = exampleParts[0] || "";
                            exampleHtml = `
                                <div class="example-container">
                                    <div class="example-en">
                                        例句：${exampleEn}
                                        <span class="play-sentence speak-btn" data-text="${exampleEn}" style="margin-left:8px;">${SPEAKER_ICON}</span>
                                    </div>
                                    <div class="example-zh">翻译：${exampleParts[1] || ""}</div>
                                </div>
                            `;
                        }
                        html += `
                            <div class="meaning-item">
                                <div class="part-of-speech">${idx+1}. ${item.part_of_speech}</div>
                                <div class="definition">释义：${item.definition}</div>
                                ${exampleHtml}
                            </div>
                        `;
                    });
                    html += `</div>`;
                } else {
                    html += `<p style='color:var(--ink-muted); text-align:center;'>暂无释义</p>`;
                }
                wordResult.innerHTML = html;
                document.querySelectorAll(".play-sentence").forEach(btn => {
                    btn.addEventListener("click", function(e) {
                        e.stopPropagation();
                        const sentenceText = this.dataset.text;
                        speakText(sentenceText);
                    });
                });
                document.querySelector(".word-phonetic").onclick = () => speakText(wordName);
                document.getElementById("addWordBtn").addEventListener("click", () => {
                    addWordToNotes(data);
                });
            } catch (err) {
                console.error("单词查询错误：", err);
                wordResult.innerHTML = `<p style='color:var(--accent); text-align:center;'>查询失败，请检查后端服务</p>`;
            }
        }



// ====================== 句子收藏 API ======================
// 加载收藏的句子
        async function loadSentenceCollection() {
            const localSentences = JSON.parse(localStorage.getItem("my-sentence-collection") || "[]");
            sentenceCollection = localSentences;

            // 新增：补全旧数据的翻译（无translation字段的句子）
            let hasUpdate = false;
            for (let i = 0; i < sentenceCollection.length; i++) {
                const item = sentenceCollection[i];
                // 跳过已有翻译的句子
                if (item.translation) continue;
                
                // 调用接口获取翻译
                try {
                    const res = await fetch(`${API_BASE}/translate`, {
                        method: "POST",
                        headers: { "Content-Type": "application/x-www-form-urlencoded" },
                        body: `text=${encodeURIComponent(item.text)}`
                    });
                    const data = await res.json();
                    sentenceCollection[i].translation = data.translation;
                    hasUpdate = true;
                } catch (err) {
                    console.error(`句子「${item.text}」翻译失败:`, err);
                    sentenceCollection[i].translation = "翻译获取失败";
                }
            }

            // 有更新则保存到本地
            if (hasUpdate) {
                localStorage.setItem("my-sentence-collection", JSON.stringify(sentenceCollection));
            }

            // 渲染列表
            renderSentenceCollection();
        }

        // 渲染句子收藏列表

// 添加句子到收藏
        async function addSentenceToCollection(text) {
            if (!text.trim()) return;
            // 去重
            const exists = sentenceCollection.some(item => item.text === text);
            if (exists) {
                alert("该句子已收藏！");
                return;
            }

            // 新增：调用后端翻译接口获取中文翻译
            let translation = "";
            try {
                const res = await fetch(`${API_BASE}/translate`, {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: `text=${encodeURIComponent(text)}`
                });
                const data = await res.json();
                translation = data.translation;
            } catch (err) {
                console.error("句子翻译失败:", err);
                translation = "翻译获取失败";
            }
            
            // 新增：把翻译结果一起存入数据
            sentenceCollection.push({ 
                text, 
                translation, // 新增翻译字段
                createTime: Date.now() 
            });
            localStorage.setItem("my-sentence-collection", JSON.stringify(sentenceCollection));
            alert("句子收藏成功！");
            // 收藏后刷新列表渲染
            renderSentenceCollection();
        }

