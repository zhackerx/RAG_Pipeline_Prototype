async function postJson(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) {
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

function updateScopeBadge() {
  const select = document.getElementById("applicant-doc-select");
  const badge = document.getElementById("scope-badge");
  const selectedDocIds = Array.from(select.selectedOptions)
    .map((opt) => opt.value)
    .filter((value) => value);

  if (selectedDocIds.length === 0) {
    badge.textContent = "Scope: All Applicant Docs";
    return;
  }
  badge.textContent = `Scope: ${selectedDocIds.length} Selected Doc(s)`;
}

async function loadApplicantDocuments() {
  const select = document.getElementById("applicant-doc-select");
  select.innerHTML = "";
  const defaultOpt = document.createElement("option");
  defaultOpt.value = "";
  defaultOpt.textContent = "No selection = use all uploaded applicant docs";
  select.appendChild(defaultOpt);

  const res = await fetch("/documents/applicants");
  const docs = await res.json();
  for (const doc of docs) {
    const opt = document.createElement("option");
    opt.value = doc.document_id;
    opt.textContent = `${doc.source} (${doc.document_id.slice(0, 8)})`;
    select.appendChild(opt);
  }
  updateScopeBadge();
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
    resultEl.textContent = `Error: ${error.message}`;
  }
});

document.getElementById("application-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const resultEl = document.getElementById("application-result");
  try {
    const payload = {
      business_name: document.getElementById("business-name").value,
      promoter_name: document.getElementById("promoter-name").value,
      annual_turnover_crore: Number(document.getElementById("turnover").value),
      dscr: Number(document.getElementById("dscr").value),
      gst_delay_months: Number(document.getElementById("gst-delays").value || 0),
      top_customer_revenue_percent: Number(document.getElementById("top-customer").value || 0),
      working_capital_days: Number(document.getElementById("working-capital").value || 0),
      existing_overdues_90_plus: document.getElementById("overdues").value === "true",
      notes: document.getElementById("notes").value,
    };
    const data = await postJson("/application/submit", payload);
    pretty(resultEl, data);
  } catch (error) {
    resultEl.textContent = `Error: ${error.message}`;
  }
});

document.getElementById("query-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const resultEl = document.getElementById("query-result");
  try {
    const question = document.getElementById("query-text").value;
    const select = document.getElementById("applicant-doc-select");
    const selectedDocIds = Array.from(select.selectedOptions)
      .map((opt) => opt.value)
      .filter((value) => value);
    appendChat("user", question);

    const data = await postJson("/chat/scoped", {
      question,
      applicant_document_ids: selectedDocIds,
    });
    appendChat("bot", data.answer || "No response generated.");
    pretty(resultEl, data);
    document.getElementById("query-text").value = "";
  } catch (error) {
    resultEl.textContent = `Error: ${error.message}`;
  }
});

document.getElementById("refresh-docs").addEventListener("click", async () => {
  const resultEl = document.getElementById("query-result");
  try {
    await loadApplicantDocuments();
    resultEl.textContent = "Applicant document list refreshed.";
  } catch (error) {
    resultEl.textContent = `Error: ${error.message}`;
  }
});

document.getElementById("applicant-doc-select").addEventListener("change", updateScopeBadge);

loadApplicantDocuments().catch((error) => {
  const resultEl = document.getElementById("query-result");
  resultEl.textContent = `Error: ${error.message}`;
});
