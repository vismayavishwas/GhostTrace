// GhostTrace AI Extension Background Service Worker (Manifest v3)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "POST_TELEMETRY") {
    fetch("http://127.0.0.1:8000/api/v1/telemetry/events", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request.payload),
    })
      .then((res) => res.json())
      .then((data) => sendResponse({ status: "SUCCESS", data }))
      .catch((err) => sendResponse({ status: "ERROR", error: err.message }));
    return true; // Async response
  }
});
