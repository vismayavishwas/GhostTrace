// GhostTrace AI Chrome Extension Content Script (Manifest v3)
(function () {
  const BACKEND_URL = "https://ghosttrace-bcp2.onrender.com/api/v1/telemetry/events";

  // Signal to the GhostTrace dashboard that the extension is installed and active.
  // The dashboard listens for this event to show/hide the "Install Extension" CTA.
  try {
    window.dispatchEvent(new CustomEvent("ghosttrace:extension-ping", { detail: { version: "1.0" } }));
  } catch (_) {}

  function getCssSelector(el) {
    if (!el || el.nodeType !== Node.ELEMENT_NODE) return "element";
    if (el.id) return `#${el.id}`;
    if (el.className && typeof el.className === "string") {
      const cls = el.className.split(" ").filter(Boolean).join(".");
      if (cls) return `${el.tagName.toLowerCase()}.${cls}`;
    }
    return el.tagName.toLowerCase();
  }

  function getXPath(el) {
    if (!el || el.nodeType !== Node.ELEMENT_NODE) return "element";
    if (el.id) return `//*[@id="${el.id}"]`;
    if (el === document.body) return "/html/body";
    let ix = 0;
    const siblings = el.parentNode ? el.parentNode.childNodes : [];
    for (let i = 0; i < siblings.length; i++) {
      const sibling = siblings[i];
      if (sibling === el) return `${getXPath(el.parentNode)}/${el.tagName.toLowerCase()}[${ix + 1}]`;
      if (sibling.nodeType === 1 && sibling.tagName === el.tagName) ix++;
    }
    return "element";
  }

  function maskInputValue(val) {
    if (!val) return "";
    return val.length > 2 ? `${val[0]}***${val[val.length - 1]}` : "***";
  }

  function captureAndSend(evtType, targetEl, inputValue) {
    const rect = targetEl && targetEl.getBoundingClientRect
      ? targetEl.getBoundingClientRect()
      : { left: 0, top: 0, width: 0, height: 0 };

    const payload = {
      event_type: evtType.toUpperCase(),
      active_tab: document.title,
      url: window.location.href,
      target_selector: getCssSelector(targetEl),
      xpath: getXPath(targetEl),
      bounding_box: { x: Math.round(rect.left), y: Math.round(rect.top), width: Math.round(rect.width), height: Math.round(rect.height) },
      scroll_pos: { x: Math.round(window.scrollX), y: Math.round(window.scrollY) },
      input_masked: maskInputValue(inputValue),
      coordinates_x: Math.round(rect.left + rect.width / 2),
      coordinates_y: Math.round(rect.top + rect.height / 2),
      timestamp: new Date().toISOString(),
      app_title: document.title,
    };

    // Primary path: route through background service worker (avoids CSP/mixed-content issues)
    if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.id && chrome.runtime.sendMessage) {
      try {
        chrome.runtime.sendMessage({ action: "POST_TELEMETRY", payload }, (response) => {
          if (chrome.runtime.lastError) {
            // Context invalidated — fall back to direct fetch to live backend
            fetch(BACKEND_URL, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload),
            }).catch(() => {});
          }
        });
        return;
      } catch (e) {
        // Extension context invalidated — fall through to direct fetch
      }
    }

    // Fallback: direct fetch to live Render backend (works on http and https pages)
    fetch(BACKEND_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).catch(() => {});
  }

  // Click Event Listener
  document.addEventListener("click", (e) => {
    captureAndSend("CLICK", e.target, null);
  }, true);

  // Input & Change Listener
  document.addEventListener("change", (e) => {
    captureAndSend("TYPE", e.target, e.target.value || e.target.innerText);
  }, true);

  // Copy & Paste Listeners
  document.addEventListener("copy", (e) => {
    captureAndSend("COPY", e.target, window.getSelection() ? window.getSelection().toString() : null);
  }, true);

  document.addEventListener("paste", (e) => {
    captureAndSend("PASTE", e.target, null);
  }, true);

  // Keydown shortcut listener (Ctrl+C / Ctrl+V / Cmd+C / Cmd+V)
  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "c") {
      captureAndSend("COPY", e.target, window.getSelection() ? window.getSelection().toString() : null);
    } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "v") {
      captureAndSend("PASTE", e.target, null);
    }
  }, true);
})();
