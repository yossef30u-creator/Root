const API = "http://127.0.0.1:5050/api";
let creditsPerTask = 0;
let lastHistoryTimestamp = 0;
let isWaitingForResponse = false;

// [תוספת] משתנים גלובליים לגרפים של Chart.js
let creditChart = null;
let taskCompletionChart = null;

// [תוספת] מעקב אחר התראות שכבר הוצגו
const displayedAlerts = new Set();

// [תוספת] פונקציית עזר לעיצוב זמן
function formatTime(isoString) {
    if (!isoString) return 'N/A';
    const date = new Date(isoString);
    return date.toLocaleTimeString('he-IL', { hour: '2-digit', minute: '2-digit' });
}

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
                   // [תוספת] טיפול בהודעות מובנות של התראות
                   if (log.type === 'alert') {
                       displayAlert(log);
                   } else {
                       classifyAndRenderMessage(log);
                   }
                    lastHistoryTimestamp = log.timestamp;
                    addedNew = true;
                }
            });

            if (addedNew) {
                setTypingIndicator(false);
                scrollToBottom();
            }
        }

       // [תוספת] קריאה לפונקציות הרינדור החדשות
       renderActionStatus(data.roadmap);
       renderStatistics(data.statistics);

    } catch (e) {
        document.getElementById('status-led').classList.replace('bg-green-500', 'bg-red-500');
        console.error("Sync failed:", e);
    }
}

// [תוספת] פונקציה להצגת סטטוס פעולות
function renderActionStatus(roadmap) {
   const actionList = document.getElementById('action-list');
   if (!actionList) return;
   actionList.innerHTML = ''; // ניקוי הרשימה לפני רינדור מחדש

   roadmap.forEach(task => {
       const item = document.createElement('div');
       item.className = `action-item p-3 rounded-lg border mb-2 `; // Tailwind classes
       let statusColor = 'border-gray-600 bg-gray-700';
       let statusText = '';

       switch (task.status) {
           case 'pending':
               statusColor = 'border-blue-400 bg-blue-900/20';
               statusText = 'ממתין';
               break;
           case 'in_progress':
               statusColor = 'border-yellow-400 bg-yellow-900/20 animate-pulse';
               statusText = 'בתהליך';
               break;
           case 'completed':
               statusColor = 'border-green-400 bg-green-900/20';
               statusText = 'הושלם';
               break;
           case 'failed':
               statusColor = 'border-red-400 bg-red-900/20';
               statusText = 'נכשל';
               break;
            case 'skipped':
               statusColor = 'border-gray-400 bg-gray-700/50';
               statusText = 'דלג';
               break;
           default:
               statusColor = 'border-gray-600 bg-gray-700';
               statusText = task.status; // הצג את הסטטוס הגולמי אם לא מוכר
       }

       item.classList.add(...statusColor.split(' '));
       item.innerHTML = `
           <p class="font-bold text-white text-sm">${task.title}</p>
           <p class="text-xs text-gray-300">סטטוס: ${statusText} (<span dir="ltr">${formatTime(task.created_at)}</span>)</p>
           ${task.start_time ? `<p class="text-xs text-gray-400">התחיל: <span dir="ltr">${formatTime(task.start_time)}</span></p>` : ''}
           ${task.end_time ? `<p class="text-xs text-gray-400">סיים: <span dir="ltr">${formatTime(task.end_time)}</span></p>` : ''}
           ${task.error_message ? `<p class="text-xs text-red-300">שגיאה: ${task.error_message}</p>` : ''}
       `;
       actionList.appendChild(item);
   });
    // [תוספת] הצגת הודעה כאשר אין פעולות
   if (roadmap.length === 0) {
       actionList.innerHTML = `
           <div class="text-gray-500 text-center py-4">
               <p>אין פעולות ממתינות או מתבצעות כעת.</p>
               <p>הזן רעיון בצ'אט כדי להתחיל!</p>
           </div>
       `;
   }
}

// [תוספת] פונקציה להצגת סטטיסטיקות וגרפים
function renderStatistics(statistics) {
   if (!statistics) return;

   // גרף קרדיטים
   if (document.getElementById('credit-chart')) {
       const creditCtx = document.getElementById('credit-chart').getContext('2d');
       const creditHistory = statistics.credit_balance_history || [];
       const labels = creditHistory.map(item => formatTime(item.timestamp));
       const data = creditHistory.map(item => item.balance);

       if (creditChart) {
           creditChart.data.labels = labels;
           creditChart.data.datasets[0].data = data;
           creditChart.update();
       } else {
           creditChart = new Chart(creditCtx, {
               type: 'line',
               data: {
                   labels: labels,
                   datasets: [{
                       label: 'יתרת קרדיטים',
                       data: data,
                       borderColor: '#00d2ff',
                       tension: 0.3,
                       fill: true,
                       backgroundColor: 'rgba(0, 210, 255, 0.1)',
                   }]
               },
               options: {
                   responsive: true,
                   maintainAspectRatio: false,
                   scales: {
                       x: { type: 'category', labels: labels, ticks: { color: '#bbb' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                       y: { beginAtZero: true, ticks: { color: '#bbb' }, grid: { color: 'rgba(255,255,255,0.05)' } }
                   },
                   plugins: {
                       legend: { display: false },
                       tooltip: { mode: 'index', intersect: false }
                   }
               }
           });
       }
   }

   // גרף סטטוס משימות (Pie Chart לדוגמה)
   if (document.getElementById('task-completion-chart')) {
       const taskSummary = statistics.task_summary || {};
       const taskCtx = document.getElementById('task-completion-chart').getContext('2d');
       const taskData = [
           taskSummary.completed_tasks || 0,
           taskSummary.failed_tasks || 0,
           taskSummary.pending_tasks || 0,
       ];
       const taskLabels = ['הושלם', 'נכשל', 'ממתין'];
       const taskColors = ['#10b981', '#ef4444', '#f59e0b'];

       if (taskCompletionChart) {
           taskCompletionChart.data.datasets[0].data = taskData;
           taskCompletionChart.update();
       } else {
           taskCompletionChart = new Chart(taskCtx, {
               type: 'doughnut',
               data: {
                   labels: taskLabels,
                   datasets: [{
                       data: taskData,
                       backgroundColor: taskColors,
                       borderColor: '#0a0a0f',
                       borderWidth: 2,
                   }]
               },
               options: {
                   responsive: true,
                   maintainAspectRatio: false,
                   plugins: {
                       legend: {
                           labels: { color: '#bbb' }
                       },
                       tooltip: {
                           callbacks: {
                               label: function(context) {
                                   let label = context.label || '';
                                   if (label) { label += ': '; }
                                   if (context.parsed !== null) {
                                       label += context.parsed;
                                   }
                                   return label;
                               }
                           }
                       }
                   }
               }
           });
       }
   }

    // [תוספת] הצגת נתוני LLM Usage (אפשר להוסיף גרף יותר מורכב בעתיד)
   const llmUsageContainer = document.getElementById('llm-usage-summary');
   if (llmUsageContainer && statistics.llm_usage) {
       const totalLlmCalls = statistics.llm_usage.length;
       const successfulLlmCalls = statistics.llm_usage.filter(call => call.success).length;
       const failedLlmCalls = totalLlmCalls - successfulLlmCalls;
       const totalLlmCost = statistics.llm_usage.reduce((sum, call) => sum + call.cost, 0);
       // ניתן להציג כאן טקסט סיכום פשוט או לבנות טבלה/גרף מפורט יותר
       llmUsageContainer.innerHTML = `
           <h3 class="text-md font-semibold text-cyan-400 mb-2 mt-4">שימוש במודלי שפה</h3>
           <p class="text-sm text-gray-300">קריאות LLM סה"כ: ${totalLlmCalls}</p>
           <p class="text-sm text-gray-300">הצלחות: ${successfulLlmCalls}, כשלונות: ${failedLlmCalls}</p>
           <p class="text-sm text-gray-300">עלות משוערת: $${totalLlmCost.toFixed(2)}</p>
       `;
   }
}

// [תוספת] פונקציה להצגת התראות
function displayAlert(alertObject) {
   const alertContainer = document.getElementById('alert-container');
   if (!alertContainer || displayedAlerts.has(alertObject.timestamp + alertObject.message)) return; // מונע כפילויות

   const alertElement = document.createElement('div');
   let bgColor = 'bg-blue-600';
   let borderColor = 'border-blue-400';
   let icon = 'ℹ️';

   switch (alertObject.severity) {
       case 'warning':
           bgColor = 'bg-yellow-600';
           borderColor = 'border-yellow-400';
           icon = '⚠️';
           break;
       case 'error':
       case 'critical': // טיפול גם ב-critical באותו אופן כרגע
           bgColor = 'bg-red-700';
           borderColor = 'border-red-500';
           icon = '❌';
           break;
   }

   alertElement.className = `alert-toast px-4 py-3 rounded-lg border
                             ${bgColor} ${borderColor} text-white shadow-lg
                             flex items-center justify-between gap-3 opacity-0 transform translate-y-full
                             transition-all duration-300 ease-out max-w-sm w-full`;
   alertElement.innerHTML = `
       <span class="text-2xl">${icon}</span>
       <p class="text-sm font-semibold flex-grow">${alertObject.message}</p>
       <button class="alert-dismiss-btn text-white opacity-75 hover:opacity-100 p-1 -mr-2 -my-2">
           <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
               <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
           </svg>
       </button>
   `;

   alertContainer.prepend(alertElement); // Push new alerts to the top
   displayedAlerts.add(alertObject.timestamp + alertObject.message); // הוספה לסט המעקב

   // אנימציית הופעה
   requestAnimationFrame(() => {
       alertElement.style.transform = 'translateY(0)';
       alertElement.style.opacity = '1';
   });

   // סגירה אוטומטית
   if (alertObject.severity !== 'critical') { // Critical alerts require manual dismissal
       setTimeout(() => {
           alertElement.style.transform = 'translateY(-100%)';
           alertElement.style.opacity = '0';
           alertElement.addEventListener('transitionend', () => alertElement.remove());
           displayedAlerts.delete(alertObject.timestamp + alertObject.message); // הסרה מהסט
       }, 7000);
   }

   // סגירה ידנית
   alertElement.querySelector('.alert-dismiss-btn').addEventListener('click', () => {
       alertElement.style.transform = 'translateY(-100%)';
       alertElement.style.opacity = '0';
       alertElement.addEventListener('transitionend', () => alertElement.remove());
       displayedAlerts.delete(alertObject.timestamp + alertObject.message);
   });
}


// מיון והצגת הודעות
function classifyAndRenderMessage(log) {
    const container = document.getElementById('chat-messages');
    let text = log.message;
    let type = 'bot';
    let statusClass = '';

   // [תוספת] טיפול בסוגי הודעות מובנים מהבק-אנד
   if (log.type === 'action_status') {
       type = 'system';
       statusClass = log.status_detail === 'completed' ? 'success' : (log.status_detail === 'failed' ? 'error' : '');
   } else if (log.type === 'alert') {
       // התראות מטופלות כבר על ידי displayAlert, לא נציג אותן בצ'אט ההיסטורי
       return;
   }

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&")
        .replace(/</g, "<")
        .replace(/>/g, ">")
        .replace(/"/g, """)
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