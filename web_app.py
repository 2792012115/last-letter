"""
AI "最后一封信" - Web 版
启动: python web_app.py
然后打开浏览器访问 http://localhost:5000
"""

from flask import Flask, render_template_string, request, jsonify, session
from letter_engine import (
    RELATIONSHIP_PRESETS,
    LetterSession,
    get_questions,
    generate_letter,
    format_letter_for_display,
)
import os
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# ============================================================
# HTML 模板 (单文件, 零依赖)
# ============================================================
HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>如果明天不在了 ✉️</title>
<style>
    :root {
        --bg: #faf8f5;
        --card: #ffffff;
        --text: #2c2416;
        --muted: #8b7355;
        --accent: #c4956a;
        --accent2: #8b5e3c;
        --border: #e8ddd0;
        --shadow: 0 2px 24px rgba(44, 36, 22, 0.06);
    }
    * { margin:0; padding:0; box-sizing:border-box; }
    body {
        font-family: "Noto Serif TC", "Source Han Serif TC", "Songti TC", serif;
        background: var(--bg);
        color: var(--text);
        min-height: 100vh;
        line-height: 1.8;
    }
    .container { max-width: 640px; margin: 0 auto; padding: 24px 20px 60px; }

    /* 头部 */
    .header {
        text-align: center;
        padding: 48px 0 36px;
    }
    .header .icon { font-size: 48px; display: block; margin-bottom: 12px; }
    .header h1 { font-size: 24px; font-weight: 400; letter-spacing: 2px; color: var(--accent2); }
    .header p { font-size: 14px; color: var(--muted); margin-top: 8px; }

    /* 卡片 */
    .card {
        background: var(--card);
        border-radius: 16px;
        padding: 32px;
        margin-bottom: 20px;
        box-shadow: var(--shadow);
        border: 1px solid var(--border);
    }
    .card h2 { font-size: 18px; font-weight: 400; margin-bottom: 20px; color: var(--accent2); }

    /* 关系选择 */
    .rel-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
    }
    .rel-btn {
        display: flex; align-items: center; gap: 10px;
        padding: 16px 14px;
        border: 1.5px solid var(--border);
        border-radius: 12px;
        background: var(--card);
        cursor: pointer;
        font-size: 15px;
        font-family: inherit;
        color: var(--text);
        transition: all 0.2s;
        text-align: left;
    }
    .rel-btn:hover { border-color: var(--accent); background: #fdf8f4; }
    .rel-btn.active { border-color: var(--accent2); background: #faf3eb; box-shadow: 0 0 0 2px rgba(139,94,60,0.1); }
    .rel-btn .rel-icon { font-size: 24px; }

    /* 输入 */
    input[type="text"], textarea {
        width: 100%;
        padding: 14px 16px;
        border: 1.5px solid var(--border);
        border-radius: 12px;
        font-size: 15px;
        font-family: inherit;
        background: #fdfbf8;
        color: var(--text);
        transition: border-color 0.2s;
        resize: vertical;
    }
    input:focus, textarea:focus { outline: none; border-color: var(--accent2); }
    textarea { min-height: 100px; }

    .btn {
        display: inline-flex; align-items: center; justify-content: center; gap: 8px;
        padding: 14px 32px;
        border: none;
        border-radius: 12px;
        font-size: 16px;
        font-family: inherit;
        cursor: pointer;
        transition: all 0.2s;
        font-weight: 500;
    }
    .btn-primary {
        background: linear-gradient(135deg, #c4956a, #b07d52);
        color: #fff;
        width: 100%;
        box-shadow: 0 4px 14px rgba(180,120,60,0.3);
    }
    .btn-primary:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(180,120,60,0.4); }
    .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
    .btn-secondary {
        background: var(--card);
        color: var(--accent2);
        border: 1.5px solid var(--border);
    }
    .btn-secondary:hover { border-color: var(--accent); }

    /* 提问区 */
    .question-block {
        margin-bottom: 28px;
    }
    .question-block .q-num {
        font-size: 12px;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 6px;
    }
    .question-block .q-text {
        font-size: 16px;
        margin-bottom: 12px;
        padding: 12px 16px;
        background: #fdf8f4;
        border-radius: 10px;
        border-left: 3px solid var(--accent);
    }

    /* 生成中动画 */
    .loading {
        text-align: center;
        padding: 40px 0;
    }
    .loading .dots { display: flex; justify-content: center; gap: 8px; margin-bottom: 16px; }
    .loading .dots span {
        width: 10px; height: 10px;
        border-radius: 50%;
        background: var(--accent);
        animation: bounce 1.4s infinite ease-in-out;
    }
    .loading .dots span:nth-child(1) { animation-delay: 0s; }
    .loading .dots span:nth-child(2) { animation-delay: 0.2s; }
    .loading .dots span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
        40% { transform: scale(1); opacity: 1; }
    }

    /* 信件展示 */
    .letter-paper {
        background: #fefdf9;
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 40px 32px;
        margin: 20px 0;
        line-height: 2.2;
        font-size: 16px;
        white-space: pre-wrap;
        position: relative;
    }
    .letter-paper::before {
        content: '';
        position: absolute; top: 0; left: 40px;
        width: 1px; height: 100%;
        background: rgba(139,94,60,0.08);
    }
    .keywords { display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0; }
    .keywords span {
        padding: 6px 14px;
        background: #fdf8f4;
        border: 1px solid var(--border);
        border-radius: 20px;
        font-size: 13px;
        color: var(--accent2);
    }

    .watermark {
        text-align: center;
        font-size: 12px;
        color: var(--muted);
        margin-top: 24px;
        padding-top: 16px;
        border-top: 1px dashed var(--border);
    }

    /* 响应式 */
    @media (max-width: 480px) {
        .rel-grid { grid-template-columns: 1fr; }
        .card { padding: 20px; }
        .letter-paper { padding: 24px 18px; font-size: 15px; }
    }

    .hidden { display: none !important; }
    .step-indicator {
        display: flex; align-items: center; gap: 8px;
        margin-bottom: 24px; font-size: 13px; color: var(--muted);
    }
    .step-indicator .step { display: flex; align-items: center; gap: 6px; }
    .step-indicator .step-num {
        width: 24px; height: 24px;
        border-radius: 50%;
        background: var(--border);
        display: flex; align-items: center; justify-content: center;
        font-size: 12px; color: var(--muted);
    }
    .step-indicator .step.active .step-num { background: var(--accent2); color: #fff; }
    .step-indicator .step.completed .step-num { background: #8fbc8f; color: #fff; }
    .step-indicator .arrow { color: var(--border); }
</style>
</head>
<body>
<div class="container">

    <!-- ========== 头部 ========== -->
    <div class="header">
        <span class="icon">✉️</span>
        <h1>如果明天不在了</h1>
        <p>你想对谁说些什么？</p>
    </div>

    <!-- ========== STEP 1: 选关系 ========== -->
    <div id="step1" class="card">
        <div class="step-indicator">
            <span class="step active"><span class="step-num">1</span> 选择对象</span>
            <span class="arrow">→</span>
            <span class="step"><span class="step-num">2</span> 回答问题</span>
            <span class="arrow">→</span>
            <span class="step"><span class="step-num">3</span> 收信</span>
        </div>
        <h2>这封信写给谁？</h2>
        <div class="rel-grid" id="relGrid"></div>
        <div style="margin-top:16px;">
            <input type="text" id="customName" placeholder="TA 的名字/称呼（可选）" style="margin-top:8px;">
        </div>
        <button class="btn btn-primary" onclick="goToQuestions()" style="margin-top:20px;">
            开始写信 ✍️
        </button>
    </div>

    <!-- ========== STEP 2: 回答问题 ========== -->
    <div id="step2" class="card hidden">
        <div class="step-indicator">
            <span class="step completed"><span class="step-num">✓</span> 选择对象</span>
            <span class="arrow">→</span>
            <span class="step active"><span class="step-num">2</span> 回答问题</span>
            <span class="arrow">→</span>
            <span class="step"><span class="step-num">3</span> 收信</span>
        </div>
        <h2 id="step2Title"></h2>
        <div id="questionsContainer"></div>
        <button class="btn btn-primary" onclick="submitAnswers()" style="margin-top:12px;">
            写好了，生成我的信 💌
        </button>
    </div>

    <!-- ========== STEP 3: 生成中 ========== -->
    <div id="step3-loading" class="card hidden">
        <div class="loading">
            <div class="dots"><span></span><span></span><span></span></div>
            <p style="color: var(--muted);">正在为你书写...</p>
        </div>
    </div>

    <!-- ========== STEP 3: 结果展示 ========== -->
    <div id="step3-result" class="card hidden">
        <div class="step-indicator">
            <span class="step completed"><span class="step-num">✓</span> 选择对象</span>
            <span class="arrow">→</span>
            <span class="step completed"><span class="step-num">✓</span> 回答问题</span>
            <span class="arrow">→</span>
            <span class="step active"><span class="step-num">3</span> 收信</span>
        </div>
        <h2>📜 你的信</h2>
        <div class="letter-paper" id="letterContent"></div>
        <div class="keywords" id="keywordsContainer"></div>
        <div class="watermark">
            「如果明天不在了」— 把没说出口的话，留给该听的人
        </div>
        <div style="display:flex; gap:12px; margin-top:24px;">
            <button class="btn btn-secondary" onclick="resetApp()" style="flex:1;">再写一封</button>
            <button class="btn btn-primary" onclick="shareLetter()" style="flex:1;">📋 复制分享</button>
        </div>
    </div>

</div>

<script>
// ============================================================
// 全局状态
// ============================================================
const RELATIONSHIPS = {{ relationships | tojson }};
let selectedRel = null;
let currentQuestions = [];

// ============================================================
// 初始化
// ============================================================
function init() {
    const grid = document.getElementById('relGrid');
    Object.entries(RELATIONSHIPS).forEach(([key, preset]) => {
        const btn = document.createElement('button');
        btn.className = 'rel-btn';
        btn.innerHTML = `<span class="rel-icon">${preset.icon}</span>${preset.label}`;
        btn.onclick = () => selectRel(key, btn);
        btn.dataset.key = key;
        grid.appendChild(btn);
    });
}

function selectRel(key, btn) {
    document.querySelectorAll('.rel-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    selectedRel = key;
}

// ============================================================
// 进入提问
// ============================================================
function goToQuestions() {
    if (!selectedRel) {
        // 如果没有选中，查找当前 active
        const activeBtn = document.querySelector('.rel-btn.active');
        if (activeBtn) selectedRel = activeBtn.dataset.key;
        else {
            // 默认选中第一个
            const firstBtn = document.querySelector('.rel-btn');
            if (firstBtn) {
                firstBtn.classList.add('active');
                selectedRel = firstBtn.dataset.key;
            } else {
                alert('请先选择收信对象');
                return;
            }
        }
    }

    const preset = RELATIONSHIPS[selectedRel];
    if (!preset) { alert('请选择收信对象'); return; }

    document.getElementById('step1').classList.add('hidden');
    document.getElementById('step2').classList.remove('hidden');
    document.getElementById('step2Title').textContent = `${preset.icon} ${preset.label}`;

    // 渲染问题
    currentQuestions = preset.questions;
    const container = document.getElementById('questionsContainer');
    container.innerHTML = '';
    preset.questions.forEach((q, i) => {
        container.innerHTML += `
            <div class="question-block">
                <div class="q-num">第 ${i+1}/${preset.questions.length} 问</div>
                <div class="q-text">💭 ${q}</div>
                <textarea id="answer${i}" placeholder="写下你的回答..."></textarea>
            </div>
        `;
    });

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ============================================================
// 提交答案 → 生成
// ============================================================
async function submitAnswers() {
    const answers = [];
    for (let i = 0; i < currentQuestions.length; i++) {
        const el = document.getElementById(`answer${i}`);
        const ans = el.value.trim() || '（这个问题我暂时不知道怎么回答）';
        answers.push(ans);
    }

    const recipientName = document.getElementById('customName').value.trim() || selectedRel;

    document.getElementById('step2').classList.add('hidden');
    document.getElementById('step3-loading').classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });

    try {
        const resp = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                relationship: selectedRel,
                recipient_name: recipientName,
                answers: answers,
                questions: currentQuestions,
            }),
        });

        const data = await resp.json();

        if (data.error) {
            alert('生成失败: ' + data.error);
            resetApp();
            return;
        }

        document.getElementById('step3-loading').classList.add('hidden');
        document.getElementById('step3-result').classList.remove('hidden');
        document.getElementById('letterContent').textContent = data.letter;

        // 关键词
        const kwContainer = document.getElementById('keywordsContainer');
        kwContainer.innerHTML = '';
        if (data.keywords && data.keywords.length > 0) {
            data.keywords.forEach(kw => {
                kwContainer.innerHTML += `<span>${kw}</span>`;
            });
        }

        window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (e) {
        alert('网络错误: ' + e.message);
        resetApp();
    }
}

// ============================================================
// 分享 / 重置
// ============================================================
function shareLetter() {
    const letter = document.getElementById('letterContent').textContent;
    const watermark = '\n\n— 来自「如果明天不在了」';
    navigator.clipboard.writeText(letter + watermark).then(() => {
        alert('已复制到剪贴板！去发给TA吧 💌');
    }).catch(() => {
        alert('复制失败，请手动选中文字复制');
    });
}

function resetApp() {
    document.getElementById('step1').classList.remove('hidden');
    document.getElementById('step2').classList.add('hidden');
    document.getElementById('step3-loading').classList.add('hidden');
    document.getElementById('step3-result').classList.add('hidden');
    document.getElementById('customName').value = '';
    document.querySelectorAll('.rel-btn').forEach(b => b.classList.remove('active'));
    selectedRel = null;
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// 启动
init();
</script>
</body>
</html>
"""


# ============================================================
# 路由
# ============================================================
@app.route("/")
def index():
    return render_template_string(
        HTML_TEMPLATE,
        relationships={
            k: {"icon": v["icon"], "label": v["label"], "questions": v["questions"]}
            for k, v in RELATIONSHIP_PRESETS.items()
        },
    )


@app.route("/api/relationships")
def api_relationships():
    """返回关系预设列表（供小程序调用）"""
    return jsonify({
        k: {"icon": v["icon"], "label": v["label"]}
        for k, v in RELATIONSHIP_PRESETS.items()
    })


@app.route("/api/questions", methods=["POST"])
def api_questions():
    """根据关系返回引导问题（供小程序调用）"""
    data = request.get_json()
    relationship = data.get("relationship", "自定义")
    questions = get_questions(relationship)
    return jsonify({"questions": questions})


@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json()
    session_obj = LetterSession(
        relationship=data["relationship"],
        recipient_name=data.get("recipient_name", ""),
        answers=data["answers"],
        questions=data["questions"],
    )
    try:
        letter, keywords = generate_letter(session_obj)
        return jsonify({"letter": letter, "keywords": keywords})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    print("\n  ✉️  AI '最后一封信' 已启动")
    print(f"  打开浏览器访问: http://localhost:{port}\n")
    app.run(debug=debug, host="0.0.0.0", port=port)
