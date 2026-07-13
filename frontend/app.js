async function postJson(url, payload, timeoutMs = 30000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  let res;
  try {
    res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timeoutId);
  }

  const raw = await res.text();
  let data = {};
  try {
    data = raw ? JSON.parse(raw) : {};
  } catch {
    data = { detail: raw || "Unexpected server response" };
  }

  if (!res.ok) {
    if (res.status === 503) {
      throw new Error(data.detail || "Gemini is currently busy. Please retry shortly.");
    }
    throw new Error(data.detail || "Request failed");
  }
  return data;
}

function pretty(el, obj) {
  el.textContent = JSON.stringify(obj, null, 2);
}

function appendChat(role, message) {
  const thread = document.getElementById("chat-thread");
  const bubble = document.createElement("div");
  bubble.className = `bubble ${role}`;
  bubble.textContent = message;
  thread.appendChild(bubble);
  thread.scrollTop = thread.scrollHeight;
  return bubble;
}

async function updateUiStatus() {
  const statusEl = document.getElementById("ui-status");
  if (!statusEl) return;
  try {
    const res = await fetch("/health", { method: "GET" });
    if (!res.ok) {
      statusEl.textContent = `Backend check failed (${res.status}).`;
      return;
    }
    statusEl.textContent = "Backend connected. Chat is ready.";
  } catch {
    statusEl.textContent = "Backend not reachable. Check server and refresh.";
  }
}

function init() {
  const adminForm = document.getElementById("admin-upload-form");
  const queryForm = document.getElementById("query-form");
  const queryInput = document.getElementById("query-text");
  const queryResult = document.getElementById("query-result");

  if (!adminForm || !queryForm || !queryInput || !queryResult) {
    return;
  }

  updateUiStatus();

  adminForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const resultEl = document.getElementById("admin-result");
    try {
      const role = document.getElementById("admin-role").value;
      const fileInput = document.getElementById("admin-file");
      if (!fileInput.files.length) {
        throw new Error("Select a file first.");
      }
      const file = fileInput.files[0];
      const ext = file.name.toLowerCase();
      let endpoint = "/documents/upload/markdown";
      if (ext.endsWith(".pdf")) endpoint = "/documents/upload/pdf";
      if (ext.endsWith(".xlsx") || ext.endsWith(".xlsm") || ext.endsWith(".xltx") || ext.endsWith(".xltm")) endpoint = "/documents/upload/excel";

      const fd = new FormData();
      fd.append("file", file);
      fd.append("document_role", role);
      fd.append("industry", "food_processing");

      const res = await fetch(endpoint, { method: "POST", body: fd });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");
      pretty(resultEl, data);
    } catch (error) {
      resultEl.textContent = `Error: ${error.message}`;
    }
  });

  queryForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const resultEl = document.getElementById("query-result");
    const submitButton = queryForm.querySelector("button[type='submit']");
    try {
      const question = queryInput.value;
      if (!question.trim()) {
        resultEl.textContent = "Enter a question first.";
        return;
      }

      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = "Sending...";
      }

      appendChat("user", question);
      const pendingBubble = appendChat("bot", "Thinking...");

      const data = await postJson(
        "/chat/scoped",
        {
          question,
          applicant_document_ids: [],
        },
        35000,
      );

      pendingBubble.textContent = data.answer || "No response generated from model. Please retry.";
      pretty(resultEl, data);
      queryInput.value = "";
    } catch (error) {
      const message = error.name === "AbortError"
        ? "The request timed out. Gemini may be busy. Please retry in a few seconds."
        : (error.message || "Unable to get response right now. Please retry.");
      appendChat("bot", message);
      resultEl.textContent = `Error: ${message}`;
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = "Send";
      }
    }
  });
}

window.addEventListener("DOMContentLoaded", init);
