async function postJson(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
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
}

document.getElementById("admin-upload-form").addEventListener("submit", async (event) => {
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
    appendChat("bot", error.message || "Model is temporarily unavailable. Please retry.");
    resultEl.textContent = `Error: ${error.message}`;
  }
});

document.getElementById("query-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const resultEl = document.getElementById("query-result");
  try {
    const question = document.getElementById("query-text").value;
    appendChat("user", question);

    const data = await postJson("/chat/scoped", {
      question,
      applicant_document_ids: [],
    });
    appendChat("bot", data.answer || "No response generated.");
    pretty(resultEl, data);
    document.getElementById("query-text").value = "";
  } catch (error) {
    resultEl.textContent = `Error: ${error.message}`;
  }
});
