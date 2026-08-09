const HEALTH_URL = "https://ghosttrace-bcp2.onrender.com/health";
const DEFAULT_URL = "https://ghosttrace-bcp2.onrender.com/api/v1/telemetry/events";

const statusText = document.getElementById("statusText");
const statusDot = document.getElementById("statusDot");
const pingTime = document.getElementById("pingTime");
const select = document.getElementById("targetEndpoint");
const pingBtn = document.getElementById("pingBtn");

function setStatus(state, ms) {
  if (state === "online") {
    statusDot.style.background = "#10b981";
    statusText.className = "status-text online";
    statusText.innerHTML = `<span class="status-dot" style="background:#10b981"></span>Live`;
    pingTime.textContent = ms ? `Response: ${ms}ms` : "";
  } else if (state === "offline") {
    statusDot.style.background = "#ef4444";
    statusText.className = "status-text offline";
    statusText.innerHTML = `<span class="status-dot" style="background:#ef4444"></span>Offline`;
    pingTime.textContent = ms === -1 ? "Backend is cold-starting, wait ~30s" : "Cannot reach backend";
  } else {
    statusDot.style.background = "#f59e0b";
    statusText.className = "status-text checking";
    statusText.innerHTML = `<span class="status-dot" style="background:#f59e0b"></span>Checking...`;
    pingTime.textContent = "";
  }
}

function pingBackend() {
  setStatus("checking");
  const t0 = Date.now();
  fetch(HEALTH_URL, { method: "GET" })
    .then((res) => {
      const ms = Date.now() - t0;
      if (res.ok) {
        setStatus("online", ms);
      } else {
        setStatus("offline");
      }
    })
    .catch(() => {
      setStatus("offline", -1);
    });
}

document.addEventListener("DOMContentLoaded", () => {
  // Load saved URL
  chrome.storage.local.get(["targetApiUrl"], (result) => {
    select.value = result.targetApiUrl || DEFAULT_URL;
  });

  // Save on change
  select.addEventListener("change", (e) => {
    chrome.storage.local.set({ targetApiUrl: e.target.value });
  });

  // Ping button
  pingBtn.addEventListener("click", pingBackend);

  // Auto-ping on open
  pingBackend();
});
