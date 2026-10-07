const apiUrlInput = document.getElementById("api-url");
const healthPill = document.getElementById("health-pill");
const checkHealthButton = document.getElementById("check-health");
const suggestions = document.getElementById("suggestions");
const sendButton = document.getElementById("send");
const questionInput = document.getElementById("question");
const chat = document.getElementById("chat");
const template = document.getElementById("message-template");
const clearButton = document.getElementById("clear-chat");
const exportButton = document.getElementById("export-chat");
const uploadButton = document.getElementById("upload-btn");
const metricTotal = document.getElementById("metric-total");
const metricLatency = document.getElementById("metric-latency");
const metricStatus = document.getElementById("metric-status");
const charCount = document.getElementById("char-count");

// Upload Modal elements
const uploadModal = document.getElementById("upload-modal");
const closeModalButton = document.getElementById("close-modal");
const cancelUploadButton = document.getElementById("cancel-upload");
const confirmUploadButton = document.getElementById("confirm-upload");
const uploadZone = document.getElementById("upload-zone");
const fileInput = document.getElementById("file-input");
const uploadList = document.getElementById("upload-list");

let totalQuestions = 0;
let lastLatencies = [];
let isLoading = false;
let selectedFiles = [];

// Auto-detect API base URL - use same origin by default
const getApiBase = () => {
  const base = apiUrlInput.value.trim().replace(/\/$/, "");
  return base || window.location.origin;
};

// Set initial API URL to current origin
window.addEventListener("load", () => {
  if (!apiUrlInput.value) {
    apiUrlInput.value = window.location.origin;
  }
  checkHealth();
});

const updateCharCount = () => {
  const length = questionInput.value.length;
  charCount.textContent = `${length} / 1000`;
};

const setHealth = (status) => {
  healthPill.classList.remove("ok", "pending", "fail");
  if (status === "ok") {
    healthPill.textContent = "🟢 Online";
    healthPill.classList.add("ok");
  } else if (status === "fail") {
    healthPill.textContent = "🔴 Offline";
    healthPill.classList.add("fail");
  } else {
    healthPill.textContent = "🟡 Checking…";
    healthPill.classList.add("pending");
  }
};

const checkHealth = async () => {
  setHealth("pending");
  try {
    const response = await fetch(`${getApiBase()}/health`, { 
      signal: AbortSignal.timeout(5000) 
    });
    if (response.ok) {
      setHealth("ok");
      metricStatus.textContent = "Connected";
      sendButton.disabled = false;
    } else {
      setHealth("fail");
      metricStatus.textContent = `Error ${response.status}`;
      sendButton.disabled = true;
    }
  } catch (error) {
    setHealth("fail");
    metricStatus.textContent = "Disconnected";
    sendButton.disabled = true;
  }
};

const addMessage = (role, text) => {
  const node = template.content.firstElementChild.cloneNode(true);
  node.classList.add(role);
  node.querySelector(".role").textContent = role === "user" ? "You" : "DocuMind";
  node.querySelector(".time").textContent = new Date().toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit"
  });
  node.querySelector(".bubble").textContent = text;
  node.querySelector(".avatar").textContent = role === "user" ? "👤" : "🤖";

  const empty = chat.querySelector(".chat-empty");
  if (empty) empty.remove();
  chat.appendChild(node);
  chat.scrollTop = chat.scrollHeight;
};

const recordLatency = (ms) => {
  lastLatencies.push(ms);
  if (lastLatencies.length > 10) lastLatencies.shift();
  const avg = lastLatencies.reduce((a, b) => a + b, 0) / lastLatencies.length;
  metricLatency.textContent = `${Math.round(avg)}ms`;
};

const sendQuestion = async (question) => {
  if (!question.trim() || isLoading) return;
  
  isLoading = true;
  sendButton.disabled = true;
  
  addMessage("user", question.trim());
  questionInput.value = "";
  updateCharCount();
  totalQuestions += 1;
  metricTotal.textContent = totalQuestions.toString();

  const start = performance.now();

  try {
    const response = await fetch(`${getApiBase()}/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
      signal: AbortSignal.timeout(60000)
    });

    const elapsed = performance.now() - start;
    recordLatency(elapsed);

    if (!response.ok) {
      const detail = await response.text();
      addMessage("bot", `⚠️ Error ${response.status}: ${detail}`);
      metricStatus.textContent = `Error ${response.status}`;
    } else {
      const data = await response.json();
      addMessage("bot", data.answer || "No answer returned.");
      metricStatus.textContent = "Answered";
    }
  } catch (error) {
    addMessage("bot", `❌ Connection error: ${error.message || error}`);
    metricStatus.textContent = "Error";
  } finally {
    isLoading = false;
    sendButton.disabled = false;
    questionInput.focus();
  }
};

const exportChat = () => {
  const messages = Array.from(chat.querySelectorAll(".message"));
  if (messages.length === 0) {
    alert("No messages to export");
    return;
  }

  const transcript = messages
    .map((message) => {
      const role = message.classList.contains("user") ? "User" : "DocuMind";
      const time = message.querySelector(".time").textContent;
      const text = message.querySelector(".bubble").textContent;
      return `[${time}] ${role}:\n${text}`;
    })
    .join("\n\n" + "=".repeat(50) + "\n\n");

  const metadata = `DocuMind Enterprise - Conversation Export\nExported: ${new Date().toLocaleString()}\nTotal Questions: ${totalQuestions}\n\n${"=".repeat(50)}\n\n`;

  const blob = new Blob([metadata + transcript], { type: "text/plain" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `documind-export-${Date.now()}.txt`;
  link.click();
  URL.revokeObjectURL(link.href);
};

const clearChat = () => {
  if (chat.querySelector(".message") && !confirm("Clear all messages?")) {
    return;
  }
  
  chat.innerHTML = `
    <div class="chat-empty">
      <div class="empty-icon">🔍</div>
      <h2>Start asking questions</h2>
      <p>
        Connect to your API and ask questions about your documents. 
        Powered by advanced AI and semantic search.
      </p>
    </div>
  `;
  totalQuestions = 0;
  lastLatencies = [];
  metricTotal.textContent = "0";
  metricLatency.textContent = "—";
  metricStatus.textContent = "—";
};

// Event Listeners
checkHealthButton.addEventListener("click", checkHealth);
apiUrlInput.addEventListener("change", checkHealth);

suggestions.addEventListener("click", (event) => {
  if (event.target.classList.contains("chip")) {
    questionInput.value = event.target.textContent;
    updateCharCount();
    questionInput.focus();
  }
});

sendButton.addEventListener("click", () => {
  sendQuestion(questionInput.value);
});

questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
    event.preventDefault();
    sendQuestion(questionInput.value);
  }
});

questionInput.addEventListener("input", updateCharCount);
clearButton.addEventListener("click", clearChat);
exportButton.addEventListener("click", exportChat);

// Upload Modal Functions
const openUploadModal = () => {
  uploadModal.classList.add("active");
  selectedFiles = [];
  uploadList.innerHTML = "";
  confirmUploadButton.disabled = true;
};

const closeUploadModal = () => {
  uploadModal.classList.remove("active");
  selectedFiles = [];
  uploadList.innerHTML = "";
  fileInput.value = "";
  confirmUploadButton.disabled = true;
};

const addFileToList = (file) => {
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    alert("Only PDF files are supported");
    return;
  }
  
  const exists = selectedFiles.some(f => f.name === file.name);
  if (exists) {
    alert("This file is already in the list");
    return;
  }
  
  selectedFiles.push(file);
  renderFileList();
};

const removeFileFromList = (fileName) => {
  selectedFiles = selectedFiles.filter(f => f.name !== fileName);
  renderFileList();
};

const renderFileList = () => {
  uploadList.innerHTML = "";
  
  selectedFiles.forEach(file => {
    const item = document.createElement("div");
    item.className = "upload-item";
    
    const size = (file.size / 1024).toFixed(1);
    
    item.innerHTML = `
      <div class="upload-item-info">
        <div class="upload-item-icon">📄</div>
        <div class="upload-item-name" title="${file.name}">${file.name}</div>
      </div>
      <div style="font-size: 12px; color: var(--muted); margin-right: 10px;">${size} KB</div>
      <button class="upload-item-remove">✕</button>
    `;
    
    item.querySelector(".upload-item-remove").addEventListener("click", () => {
      removeFileFromList(file.name);
    });
    
    uploadList.appendChild(item);
  });
  
  confirmUploadButton.disabled = selectedFiles.length === 0;
};

const uploadFiles = async () => {
  if (selectedFiles.length === 0) return;
  
  confirmUploadButton.disabled = true;
  const statusDiv = document.createElement("div");
  statusDiv.className = "upload-status uploading";
  statusDiv.textContent = `Uploading ${selectedFiles.length} file(s)...`;
  uploadList.appendChild(statusDiv);
  
  let successCount = 0;
  let errorCount = 0;
  
  for (const file of selectedFiles) {
    try {
      const formData = new FormData();
      formData.append("file", file);
      
      const response = await fetch(`${getApiBase()}/upload`, {
        method: "POST",
        body: formData
      });
      
      if (response.ok) {
        successCount++;
      } else {
        errorCount++;
      }
    } catch (error) {
      errorCount++;
    }
  }
  
  statusDiv.className = errorCount === 0 ? "upload-status success" : "upload-status error";
  statusDiv.textContent = `✓ ${successCount} uploaded${errorCount > 0 ? `, ✕ ${errorCount} failed` : ""}`;
  
  confirmUploadButton.disabled = false;
  
  setTimeout(() => {
    if (errorCount === 0) {
      closeUploadModal();
    }
  }, 2000);
};

// Upload Zone Drag & Drop
uploadZone.addEventListener("click", () => fileInput.click());

uploadZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  uploadZone.classList.add("dragover");
});

uploadZone.addEventListener("dragleave", () => {
  uploadZone.classList.remove("dragover");
});

uploadZone.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadZone.classList.remove("dragover");
  
  const files = e.dataTransfer.files;
  Array.from(files).forEach(file => addFileToList(file));
});

fileInput.addEventListener("change", (e) => {
  const files = e.target.files;
  Array.from(files).forEach(file => addFileToList(file));
});

// Modal Button Events
uploadButton.addEventListener("click", openUploadModal);
closeModalButton.addEventListener("click", closeUploadModal);
cancelUploadButton.addEventListener("click", closeUploadModal);
confirmUploadButton.addEventListener("click", uploadFiles);

uploadModal.querySelector(".modal-overlay").addEventListener("click", closeUploadModal);

// Initialize
updateCharCount();
checkHealth();
