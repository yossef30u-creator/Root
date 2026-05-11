const API = "http://127.0.0.1:5050/api";
let creditsPerTask = 0;
let lastHistoryTimestamp = 0;
let isWaitingForResponse = false;

// הגדרות עיצוב קוד ל-Markdown
marked.setOptions({
    highlight: function(code, lang) {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, { language }).value;
    },
    breaks: true
});

// סנכרון עם השרת
async function sync() {
    try {
        const r = await fetch(`${API}/state`);
        const data = await r.json();
        
        document.getElementById('credit-balance').innerText = (data.user_credits || 0).toLocaleString();

        const sel = document.getElementById('model-selector');
        if (sel.options.length === 0 && data.pricing) {
            Object.entries(data.pricing).forEach(([id, info]) => {
                sel.add(new Option(info.label.split('(')[0].trim(), id));
            });
            sel.value = data.selected_model || Object.keys(data.pricing)[0];
        }
        
        if (data.history && data.history.length > 0) {
            let addedNew = false;
            data.history.forEach(log => {
                if (log.timestamp > lastHistoryTimestamp) {
                    classifyAndRenderMessage(log);
                    lastHistoryTimestamp = log.timestamp;
                    addedNew = true;
                }
            });

            if (addedNew) {
                setTypingIndicator(false);
                scrollToBottom();
            }
        }
    } catch (e) {
        document.getElementById('status-led').classList.replace('bg-green-500', 'bg-red-500');
    }
}

// מיון והצגת הודעות
function classifyAndRenderMessage(log) {
    const container = document.getElementById('chat-messages');
    let text = log.message;
    let type = 'bot'; 
    let statusClass = '';

    if (text.startsWith("המשתמש הזין רעיון:") || text.startsWith("User:")) {
        type = 'user';
        text = text.replace("המשתמש הזין רעיון: ", "").replace("User: ", "");
    } 
    else if (text.includes("שגיאה") || text.includes("נכשל") || text.includes("Error") || text.includes("❌")) {
        type = 'system';
        statusClass = 'error';
    }
    else if (text.includes("הושלם") || text.includes("נכתב בהצלחה") || text.includes("✅") || text.includes("Cr)")) {
        type = 'system';
        statusClass = 'success';
    }
    else if (text.includes("מתחיל ביצוע") || text.includes("מנתח רעיון") || text.includes("סוכן")) {
        type = 'system';
    }

    const row = document.createElement('div');
    row.className = `msg-row ${type}`;

    if (type === 'system') {
        row.innerHTML = `<div class="bubble-system ${statusClass}">${text}</div>`;
    } else {
        const parsedContent = type === 'bot' ? marked.parse(text) : escapeHtml(text);
        row.innerHTML = `<div class="bubble bubble-${type} ${type === 'bot' ? 'prose' : ''}">${parsedContent}</div>`;
    }

    container.appendChild(row);
}

// מניעת הזרקת קוד לא רצוי
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;")
        .replace(/\n/g, "<br>");
}

// גלילה חכמה למטה
function scrollToBottom() {
    const container = document.getElementById('chat-messages');
    container.scrollTop = container.scrollHeight;
}

// מחוון "מקליד..."
function setTypingIndicator(show) {
    isWaitingForResponse = show;
    document.getElementById('typing-indicator').classList.toggle('hidden', !show);
    if (show) scrollToBottom();
}

// שליחת הודעה חדשה לשרת
async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message || isWaitingForResponse) return;

    classifyAndRenderMessage({ timestamp: Date.now() / 1000, message: `User: ${message}` });
    input.value = '';
    input.style.height = '40px';
    scrollToBottom();
    setTypingIndicator(true);

    try {
        await fetch(`${API}/action`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({type: 'GENERATE_ROADMAP', payload: {idea: message}})
        });
    } catch (e) {
        setTypingIndicator(false);
        classifyAndRenderMessage({ timestamp: Date.now() / 1000, message: `❌ שגיאת תקשורת עם הליבה.` });
    }
}

// שינוי מודל שפה
async function updateModel() {
    const model = document.getElementById('model-selector').value;
    await fetch(`${API}/settings`, { 
        method: 'POST', 
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify({model}) 
    });
    sync();
}

// --- חיבור אירועים ל-DOM ---

// התאמת גובה תיבת הטקסט
const tx = document.getElementById('chat-input');
tx.addEventListener("input", function() {
    this.style.height = "40px";
    this.style.height = (this.scrollHeight) + "px";
});

// שליחה בלחיצה על Enter
tx.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// חיבור הכפתורים לאירועים
document.getElementById('send-button').addEventListener('click', sendMessage);
document.getElementById('model-selector').addEventListener('change', updateModel);

// אתחול ראשוני והגדרת Loop הסנכרון
sync();
setInterval(sync, 1500);
