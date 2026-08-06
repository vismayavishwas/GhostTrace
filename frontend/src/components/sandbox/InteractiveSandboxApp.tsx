"use client";

import React, { useState } from "react";
import { Building2, Copy, Check, ArrowRight, Play, Sparkles } from "lucide-react";
import { postTelemetryEvent } from "@/lib/api";

export const InteractiveSandboxApp: React.FC = () => {
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    invoiceId: "",
    amount: "",
    vendor: "",
  });
  const [statusMsg, setStatusMsg] = useState<string>("");

  const sampleData = {
    invoiceId: "INV-2026-9842",
    amount: "$14,850.00",
    vendor: "Acme Cloud Logistics Inc.",
  };

  const dispatchTelemetry = async (eventType: string, selector: string, value: string) => {
    const payload = {
      event_type: eventType,
      active_tab: "Enterprise ERP Portal",
      url: typeof window !== "undefined" ? window.location.href : "http://localhost:3000/demo",
      target_selector: selector,
      xpath: `//*[@id="${selector.replace("#", "")}"]`,
      bounding_box: { x: 120, y: 240, width: 200, height: 35 },
      scroll_pos: { x: 0, y: 0 },
      input_masked: value ? `${value[0]}***` : "",
      coordinates_x: 250.0,
      coordinates_y: 300.0,
      timestamp: new Date().toISOString(),
      app_title: "Enterprise ERP Portal",
    };

    setStatusMsg(`[Telemetry Transmitted] ${eventType} on ${selector}`);
    await postTelemetryEvent(payload);
    setTimeout(() => setStatusMsg(""), 2000);
  };

  const handleCopy = (fieldKey: string, value: string) => {
    navigator.clipboard.writeText(value);
    setCopiedField(fieldKey);
    dispatchTelemetry("COPY", `#source-${fieldKey}`, value);
    setTimeout(() => setCopiedField(null), 1500);
  };

  const handlePaste = (fieldKey: string, value: string) => {
    setFormData((prev) => ({ ...prev, [fieldKey]: value }));
    dispatchTelemetry("PASTE", `#target-erp-${fieldKey}`, value);
  };

  const handleInputClick = (fieldKey: string) => {
    dispatchTelemetry("CLICK", `#target-erp-${fieldKey}`, "");
  };

  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-cyan-500/30 bg-slate-900/90 p-5 shadow-2xl backdrop-blur-xl">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-cyan-500/10 p-2 text-cyan-400 border border-cyan-500/20">
            <Building2 className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100">Live Sandboxed Enterprise Portal</h3>
            <p className="text-[10px] text-slate-400">Click & copy/paste below to trigger live telemetry perception</p>
          </div>
        </div>
        {statusMsg && (
          <span className="rounded-full bg-cyan-500/20 px-2.5 py-0.5 text-[10px] font-mono text-cyan-300 border border-cyan-500/30 animate-pulse">
            {statusMsg}
          </span>
        )}
      </div>

      {/* 2-Column Split: Left Source Invoice PDF, Right Target ERP Portal */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        {/* Left: Source Vendor Invoice */}
        <div className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-950/70 p-4">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
            <span className="font-bold text-slate-300">📄 Source Invoice PDF</span>
            <span className="text-[10px] font-mono text-amber-400">Vendor Portal</span>
          </div>

          <div className="flex flex-col gap-2.5">
            <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/60 p-2">
              <div>
                <span className="text-[10px] text-slate-400">Invoice Number</span>
                <p id="source-invoiceId" className="font-mono font-bold text-slate-200">{sampleData.invoiceId}</p>
              </div>
              <button
                onClick={() => handleCopy("invoiceId", sampleData.invoiceId)}
                className="flex items-center gap-1 rounded-md bg-slate-800 px-2 py-1 text-[10px] text-slate-300 hover:bg-slate-700 hover:text-white transition"
              >
                {copiedField === "invoiceId" ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                <span>{copiedField === "invoiceId" ? "Copied" : "Copy"}</span>
              </button>
            </div>

            <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/60 p-2">
              <div>
                <span className="text-[10px] text-slate-400">Total Amount</span>
                <p id="source-amount" className="font-mono font-bold text-slate-200">{sampleData.amount}</p>
              </div>
              <button
                onClick={() => handleCopy("amount", sampleData.amount)}
                className="flex items-center gap-1 rounded-md bg-slate-800 px-2 py-1 text-[10px] text-slate-300 hover:bg-slate-700 hover:text-white transition"
              >
                {copiedField === "amount" ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                <span>{copiedField === "amount" ? "Copied" : "Copy"}</span>
              </button>
            </div>

            <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/60 p-2">
              <div>
                <span className="text-[10px] text-slate-400">Vendor Name</span>
                <p id="source-vendor" className="font-mono font-bold text-slate-200">{sampleData.vendor}</p>
              </div>
              <button
                onClick={() => handleCopy("vendor", sampleData.vendor)}
                className="flex items-center gap-1 rounded-md bg-slate-800 px-2 py-1 text-[10px] text-slate-300 hover:bg-slate-700 hover:text-white transition"
              >
                {copiedField === "vendor" ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                <span>{copiedField === "vendor" ? "Copied" : "Copy"}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Right: Target ERP Intake Form */}
        <div className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-950/70 p-4">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
            <span className="font-bold text-slate-300">🏢 Target ERP Intake Form</span>
            <span className="text-[10px] font-mono text-cyan-400">SAP / ERP System</span>
          </div>

          <div className="flex flex-col gap-2.5">
            <div>
              <label className="text-[10px] text-slate-400 block mb-1">Target Invoice #</label>
              <div className="flex gap-1.5">
                <input
                  id="target-erp-invoiceId"
                  type="text"
                  value={formData.invoiceId}
                  onChange={(e) => setFormData((prev) => ({ ...prev, invoiceId: e.target.value }))}
                  onClick={() => handleInputClick("invoiceId")}
                  placeholder="Click or paste invoice #..."
                  className="flex-1 rounded-md border border-slate-800 bg-slate-900 px-2.5 py-1.5 font-mono text-slate-200 focus:border-cyan-500 focus:outline-none"
                />
                <button
                  onClick={() => handlePaste("invoiceId", sampleData.invoiceId)}
                  className="rounded-md bg-cyan-500/20 border border-cyan-500/30 px-2 py-1 text-[10px] font-bold text-cyan-300 hover:bg-cyan-500/30 transition"
                >
                  Paste
                </button>
              </div>
            </div>

            <div>
              <label className="text-[10px] text-slate-400 block mb-1">Target Amount</label>
              <div className="flex gap-1.5">
                <input
                  id="target-erp-amount"
                  type="text"
                  value={formData.amount}
                  onChange={(e) => setFormData((prev) => ({ ...prev, amount: e.target.value }))}
                  onClick={() => handleInputClick("amount")}
                  placeholder="Click or paste amount..."
                  className="flex-1 rounded-md border border-slate-800 bg-slate-900 px-2.5 py-1.5 font-mono text-slate-200 focus:border-cyan-500 focus:outline-none"
                />
                <button
                  onClick={() => handlePaste("amount", sampleData.amount)}
                  className="rounded-md bg-cyan-500/20 border border-cyan-500/30 px-2 py-1 text-[10px] font-bold text-cyan-300 hover:bg-cyan-500/30 transition"
                >
                  Paste
                </button>
              </div>
            </div>

            <div>
              <label className="text-[10px] text-slate-400 block mb-1">Target Vendor Name</label>
              <div className="flex gap-1.5">
                <input
                  id="target-erp-vendor"
                  type="text"
                  value={formData.vendor}
                  onChange={(e) => setFormData((prev) => ({ ...prev, vendor: e.target.value }))}
                  onClick={() => handleInputClick("vendor")}
                  placeholder="Click or paste vendor..."
                  className="flex-1 rounded-md border border-slate-800 bg-slate-900 px-2.5 py-1.5 font-mono text-slate-200 focus:border-cyan-500 focus:outline-none"
                />
                <button
                  onClick={() => handlePaste("vendor", sampleData.vendor)}
                  className="rounded-md bg-cyan-500/20 border border-cyan-500/30 px-2 py-1 text-[10px] font-bold text-cyan-300 hover:bg-cyan-500/30 transition"
                >
                  Paste
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
