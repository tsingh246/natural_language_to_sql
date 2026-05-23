const connectForm = document.querySelector("#connectForm");
const chatForm = document.querySelector("#chatForm");
const messages = document.querySelector("#messages");
const questionInput = document.querySelector("#questionInput");
const sendButton = document.querySelector("#sendButton");
const clearButton = document.querySelector("#clearButton");
const connectionStatus = document.querySelector("#connectionStatus");
const chatMeta = document.querySelector("#chatMeta");

let socket;
let connected = false;

function setStatus(text, isConnected = false) {
  connected = isConnected;
  connectionStatus.textContent = text;
  chatMeta.textContent = isConnected ? text : "Connect a database to begin.";
  questionInput.disabled = !isConnected;
  sendButton.disabled = !isConnected;
}

function addMessage(role, content, details = {}) {
  const article = document.createElement("article");
  article.className = `message ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = content;

  if (details.query || details.result) {
    const block = document.createElement("details");
    block.className = "details";

    const summary = document.createElement("summary");
    summary.textContent = "SQL details";
    block.append(summary);

    if (details.query) {
      const query = document.createElement("pre");
      query.textContent = details.query;
      block.append(query);
    }

    if (details.result) {
      const result = document.createElement("pre");
      result.textContent = details.result;
      block.append(result);
    }

    bubble.append(block);
  }

  article.append(bubble);
  messages.append(article);
  messages.scrollTop = messages.scrollHeight;
}

function readConnectionForm() {
  const formData = new FormData(connectForm);
  const db = {};

  for (const [key, value] of formData.entries()) {
    const cleanValue = String(value).trim();
    if (cleanValue) {
      db[key] = key === "DB_PORT" ? Number(cleanValue) : cleanValue;
    }
  }

  return db;
}

function ensureSocket() {
  if (socket && socket.readyState === WebSocket.OPEN) {
    return socket;
  }

  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  socket = new WebSocket(`${protocol}://${window.location.host}/ws`);

  socket.addEventListener("message", (event) => {
    const payload = JSON.parse(event.data);

    if (payload.type === "connected") {
      setStatus(payload.message, true);
      addMessage("system", payload.message);
      questionInput.focus();
      return;
    }

    if (payload.type === "status") {
      addMessage("system", payload.message);
      return;
    }

    if (payload.type === "response") {
      addMessage("assistant", payload.answer, {
        query: payload.query,
        result: payload.result,
      });
      sendButton.disabled = false;
      questionInput.disabled = false;
      questionInput.focus();
      return;
    }

    if (payload.type === "error") {
      addMessage("error", payload.message);
      sendButton.disabled = !connected;
      questionInput.disabled = !connected;
    }
  });

  socket.addEventListener("close", () => {
    setStatus("Disconnected");
  });

  socket.addEventListener("error", () => {
    addMessage("error", "WebSocket connection failed.");
  });

  return socket;
}

connectForm.addEventListener("submit", (event) => {
  event.preventDefault();
  setStatus("Connecting");
  const ws = ensureSocket();
  const connect = () => ws.send(JSON.stringify({ type: "connect", db: readConnectionForm() }));

  if (ws.readyState === WebSocket.OPEN) {
    connect();
  } else {
    ws.addEventListener("open", connect, { once: true });
  }
});

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();

  if (!question || !connected) {
    return;
  }

  addMessage("user", question);
  questionInput.value = "";
  questionInput.disabled = true;
  sendButton.disabled = true;
  socket.send(JSON.stringify({ type: "message", question }));
});

clearButton.addEventListener("click", () => {
  messages.innerHTML = "";
});
