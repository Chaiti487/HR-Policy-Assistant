const API_URL = "http://127.0.0.1:8000";

let adminToken = null;

// ==========================================
// ADMIN LOGIN
// ==========================================

async function adminLogin() {
  const username = document.getElementById("username").value.trim();

  const password = document.getElementById("password").value;

  const loginStatus = document.getElementById("loginStatus");

  if (!username || !password) {
    loginStatus.textContent = "Please enter username and password.";

    return;
  }

  loginStatus.textContent = "Signing in...";

  try {
    const response = await fetch(
      `${API_URL}/admin/login?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
      {
        method: "POST",
      },
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Login failed.");
    }

    adminToken = "admin-session";

    document.getElementById("loginSection").style.display = "none";

    document.getElementById("loginForm").style.display = "none";

    document.getElementById("adminDashboard").style.display = "block";

    loginStatus.textContent = "";

    loadPolicies();
  } catch (error) {
    loginStatus.textContent = `Error: ${error.message}`;
  }
}

// ==========================================
// UPLOAD POLICIES
// ==========================================

async function uploadPolicy() {
  const fileInput = document.getElementById("policyFile");

  const status = document.getElementById("uploadStatus");

  if (!fileInput.files.length) {
    status.textContent = "Please select at least one policy file.";

    return;
  }

  const formData = new FormData();

  for (const file of fileInput.files) {
    formData.append("files", file);
  }

  status.textContent = "Uploading and indexing policies...";

  try {
    const response = await fetch(`${API_URL}/admin/upload`, {
      method: "POST",

      headers: {
        "X-Admin-Token": adminToken,
      },

      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Upload failed.");
    }

    status.textContent = `${data.documents.length} policy file(s) uploaded successfully.`;

    fileInput.value = "";

    loadPolicies();
  } catch (error) {
    status.textContent = `Error: ${error.message}`;
  }
}

// ==========================================
// LOAD CURRENT POLICIES
// ==========================================

async function loadPolicies() {
  const policyList = document.getElementById("policyList");

  const policyCount = document.getElementById("policyCount");

  policyList.innerHTML = `<p class="loading-text">Loading policies...</p>`;

  try {
    const response = await fetch(`${API_URL}/admin/policies`);

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Failed to load policies.");
    }

    policyList.innerHTML = "";

    if (!data.documents || data.documents.length === 0) {
      policyCount.textContent = "0 policies";

      policyList.innerHTML = `
                <div class="empty-state">
                    <p>No policy documents uploaded yet.</p>
                </div>
            `;

      return;
    }

    policyCount.textContent = `${data.documents.length} ${
      data.documents.length === 1 ? "policy" : "policies"
    }`;

    data.documents.forEach((documentName) => {
      const div = document.createElement("div");

      div.className = "policy-item";

      const info = document.createElement("div");

      info.className = "policy-info";

      const icon = document.createElement("div");

      icon.className = "policy-icon";

      icon.textContent = "📄";

      const details = document.createElement("div");

      const name = document.createElement("strong");

      name.textContent = documentName;

      const status = document.createElement("span");

      status.className = "policy-status";

      status.textContent = "✓ Indexed";

      details.appendChild(name);

      details.appendChild(status);

      info.appendChild(icon);

      info.appendChild(details);

      const deleteButton = document.createElement("button");

      deleteButton.textContent = "Delete";

      deleteButton.className = "delete-button";

      deleteButton.onclick = () => deletePolicy(documentName);

      div.appendChild(info);

      div.appendChild(deleteButton);

      policyList.appendChild(div);
    });
  } catch (error) {
    policyList.innerHTML = `
            <p class="status-message">
                Error loading policies: ${error.message}
            </p>
        `;
  }
}

// ==========================================
// DELETE POLICY
// ==========================================

async function deletePolicy(documentName) {
  const confirmed = confirm(
    `Are you sure you want to delete "${documentName}"?`,
  );

  if (!confirmed) {
    return;
  }

  const status = document.getElementById("uploadStatus");

  status.textContent = `Deleting ${documentName}...`;

  try {
    const response = await fetch(
      `${API_URL}/admin/policies/${encodeURIComponent(documentName)}`,
      {
        method: "DELETE",

        headers: {
          "X-Admin-Token": adminToken,
        },
      },
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Delete failed.");
    }

    status.textContent = `${documentName} deleted successfully.`;

    loadPolicies();
  } catch (error) {
    status.textContent = `Error: ${error.message}`;
  }
}

// ==========================================
// LOGOUT
// ==========================================

function logout() {
  adminToken = null;

  document.getElementById("adminDashboard").style.display = "none";

  document.getElementById("loginSection").style.display = "block";

  document.getElementById("loginForm").style.display = "block";

  document.getElementById("username").value = "";

  document.getElementById("password").value = "";

  document.getElementById("loginStatus").textContent = "";

  document.getElementById("uploadStatus").textContent = "";

  document.getElementById("policyList").innerHTML = "";
}
