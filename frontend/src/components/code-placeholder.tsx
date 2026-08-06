"use client";

import React from "react";
import Editor from "@monaco-editor/react";

const SAMPLE_PLAYWRIGHT_CODE = `# GhostTrace AI - Synthesized Playwright Automation Placeholder
# Compiler Agent will generate dynamic automation scripts here in Phase 4.

import asyncio
from playwright.async_api import async_playwright

async function run_discovered_workflow():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Step 1: Semantic Action - Navigate to Enterprise SAP Portal
        await page.goto("https://sap-demo.ghosttrace.ai")
        
        # Step 2: Semantic Action - Perform Form Autofill
        await page.fill("#invoice-input", "INV-2026-0891")
        await page.click("button[type='submit']")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_discovered_workflow())
`;

export const CodePlaceholder: React.FC = () => {
  return (
    <div className="w-full h-full min-h-[320px] glass-panel rounded-xl overflow-hidden flex flex-col border border-surface-border">
      <div className="px-4 py-2 bg-slate-950/80 border-b border-slate-800 flex items-center justify-between">
        <span className="text-xs font-mono text-slate-400">generated_automation.py</span>
        <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400">Playwright Python</span>
      </div>
      <div className="flex-1 w-full relative">
        <Editor
          height="100%"
          defaultLanguage="python"
          defaultValue={SAMPLE_PLAYWRIGHT_CODE}
          theme="vs-dark"
          options={{
            readOnly: true,
            minimap: { enabled: false },
            fontSize: 12,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            padding: { top: 12, bottom: 12 },
          }}
        />
      </div>
    </div>
  );
};
