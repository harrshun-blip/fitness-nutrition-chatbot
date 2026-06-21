// Pulse PWA front-end logic.

const chat = document.getElementById("chat");
const welcome = document.getElementById("welcome");
const composer = document.getElementById("composer");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");
const newChatBtn = document.getElementById("newChat");

let history = [];            // [{role:"user"|"model", content:""}]
let busy = false;

// ---- Restore previous conversation (this device only) ----
try {
  const saved = JSON.parse(localStorage.getItem("pulse_history") || "[]");
  if (Array.isArray(saved) && saved.length) {
    history = saved;
    welcome.remove();
    history.forEach((t) => addBubble(t.role === "user" ? "user" : "bot", t.content));
    scrollToBottom();
  }
} catch (_) {}

// ---- Tiny markdown -> HTML (bold, code, bullet lists, paragraphs) ----
function escapeHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
function renderMarkdown(text) {
  const lines = escapeHtml(text).split("\n");
  let html = "";
  let inList = false;
  for (let raw of lines) {
    let line = raw
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/`([^`]+?)`/g, "<code>$1</code>");
    if (/^\s*[-*]\s+/.test(raw)) {
      if (!inList) { html += "<ul>"; inList = true; }
      html += "<li>" + line.replace(/^\s*[-*]\s+/, "") + "</li>";
    } else {
      if (inList) { html += "</ul>"; inList = false; }
      if (line.trim() === "") continue;
      html += "<p>" + line + "</p>";
    }
  }
  if (inList) html += "</ul>";
  return html || "<p></p>";
}

function addBubble(who, text) {
  const msg = document.createElement("div");
  msg.className = "msg " + who;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = who === "bot" ? renderMarkdown(text) : escapeHtml(text);
  msg.appendChild(bubble);
  chat.appendChild(msg);
  return bubble;
}

function addTyping() {
  const msg = document.createElement("div");
  msg.className = "msg bot";
  msg.id = "typing";
  msg.innerHTML = '<div class="bubble"><div class="typing"><span></span><span></span><span></span></div></div>';
  chat.appendChild(msg);
  scrollToBottom();
  return msg;
}

function scrollToBottom() {
  requestAnimationFrame(() => { chat.scrollTop = chat.scrollHeight; });
}

function save() {
  try { localStorage.setItem("pulse_history", JSON.stringify(history)); } catch (_) {}
}

async function send(text) {
  if (busy || !text.trim()) return;
  busy = true;
  sendBtn.disabled = true;
  if (welcome && welcome.parentNode) welcome.remove();

  addBubble("user", text);
  history.push({ role: "user", content: text });
  save();
  scrollToBottom();
  input.value = "";

  const typing = addTyping();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, history: history.slice(0, -1) }),
    });
    const data = await res.json();
    typing.remove();
    const reply = data.reply || "Sorry, I didn't get a response.";
    addBubble("bot", reply);
    history.push({ role: "model", content: reply });
    save();
  } catch (err) {
    typing.remove();
    addBubble("bot", "⚠️ I couldn't reach the server. Check your connection and try again.");
  } finally {
    busy = false;
    sendBtn.disabled = false;
    scrollToBottom();
    input.focus();
  }
}

composer.addEventListener("submit", (e) => {
  e.preventDefault();
  send(input.value);
});

// Suggestion chips
document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => send(chip.textContent));
});

// New chat
newChatBtn.addEventListener("click", () => {
  history = [];
  save();
  location.reload();
});

// ---- Register the service worker (makes it installable + offline shell) ----
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("service-worker.js").catch(() => {});
  });
}
