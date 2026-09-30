// session_id -> { label, messages: [{role,text}], lastOutcome }
let sessions = {};
let sessionOrder = [];
let activeSessionId = null; // null = 下一句話會開一個全新 session

const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const payloadView = document.getElementById("payload-view");
const sessionRow = document.getElementById("session-row");
const submitBtn = chatForm.querySelector("button[type=submit]");

function appendMessage(role, text) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = text;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function renderPayload(data) {
  payloadView.textContent =
    `$ ${data.command.join(" ")}\n\n` +
    `session_id: ${data.session_id}\n\n` +
    `result: ${data.reply}`;
}

function renderSessionChips() {
  sessionRow.innerHTML = "";
  sessionOrder.forEach((id) => {
    const chip = document.createElement("button");
    chip.className = "session-chip" + (id === activeSessionId ? " active" : "");
    chip.textContent = sessions[id].label;
    chip.addEventListener("click", () => {
      activeSessionId = id;
      renderActiveSession();
    });
    sessionRow.appendChild(chip);
  });
  const newChip = document.createElement("button");
  newChip.className = "session-chip new-session";
  newChip.textContent = "＋ 新 Session";
  newChip.addEventListener("click", () => {
    activeSessionId = null;
    renderActiveSession();
  });
  sessionRow.appendChild(newChip);
}

function renderActiveSession() {
  renderSessionChips();
  chatLog.innerHTML = "";
  if (activeSessionId === null) {
    appendMessage("system-note", "已開新 session——下一句話會是全新對話。");
    payloadView.textContent = "（還沒送出任何訊息）";
    return;
  }
  const s = sessions[activeSessionId];
  s.messages.forEach((m) => appendMessage(m.role, m.text));
  if (s.lastOutcome) renderPayload(s.lastOutcome);
}

async function submitMessage(message) {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: activeSessionId }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);

  const isNewSession = activeSessionId === null;
  activeSessionId = data.session_id;
  if (isNewSession) {
    sessions[activeSessionId] = { label: message.slice(0, 12) || "(新 session)", messages: [] };
    sessionOrder.push(activeSessionId);
  }
  sessions[activeSessionId].messages.push({ role: "user", text: message });
  sessions[activeSessionId].messages.push({ role: "assistant", text: data.reply });
  sessions[activeSessionId].lastOutcome = data;

  renderSessionChips();
  appendMessage("assistant", data.reply);
  renderPayload(data);
}

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;

  appendMessage("user", message);
  chatInput.value = "";
  submitBtn.disabled = true;

  try {
    await submitMessage(message);
  } catch (err) {
    appendMessage("system-note", `出錯了：${err.message}`);
  } finally {
    submitBtn.disabled = false;
  }
});

renderActiveSession();
