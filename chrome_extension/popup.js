document.addEventListener("DOMContentLoaded", () => {
  const select = document.getElementById("targetEndpoint");
  const DEFAULT_URL = "https://ghosttrace-bcp2.onrender.com/api/v1/telemetry/events";

  chrome.storage.local.get(["targetApiUrl"], (result) => {
    select.value = result.targetApiUrl || DEFAULT_URL;
  });

  select.addEventListener("change", (e) => {
    const val = e.target.value;
    chrome.storage.local.set({ targetApiUrl: val });
  });
});
