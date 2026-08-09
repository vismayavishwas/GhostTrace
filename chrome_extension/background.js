// GhostTrace AI Extension Background Service Worker (Manifest v3)
const DEFAULT_API_URL = "https://ghosttrace-bcp2.onrender.com/api/v1/telemetry/events";

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "POST_TELEMETRY") {
    chrome.storage.local.get(["targetApiUrl"], (result) => {
      const targetUrl = result.targetApiUrl || DEFAULT_API_URL;
      fetch(targetUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request.payload),
      })
        .then((res) => res.json())
        .then((data) => sendResponse({ status: "SUCCESS", data }))
        .catch((err) => sendResponse({ status: "ERROR", error: err.message }));
    });
    return true; // Async response
  }
});
