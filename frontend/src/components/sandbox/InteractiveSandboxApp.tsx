"use client";

import React, { useState, useEffect } from "react";
import { Building2, Copy, Check, ArrowRight, Play, Sparkles, Bot, RotateCcw } from "lucide-react";
import { postTelemetryEvent } from "@/lib/api";

const INVOICE_SAMPLES = [
  { invoiceId: "INV-2026-9841", amount: "$14,850.00", vendor: "Acme Cloud Logistics Inc." },
  { invoiceId: "INV-2026-9842", amount: "$22,400.00", vendor: "Global Tech Systems" },
  { invoiceId: "INV-2026-9843", amount: "$8,750.50", vendor: "Nexus Freight Solutions" },
  { invoiceId: "INV-2026-9844", amount: "$31,900.00", vendor: "Apex Industrial Supplies" },
  { invoiceId: "INV-2026-9845", amount: "$19,250.75", vendor: "Vanguard Cyber Security" },
  { invoiceId: "INV-2026-9846", amount: "$45,000.00", vendor: "Starlight Media Group" },
  { invoiceId: "INV-2026-9847", amount: "$6,120.00", vendor: "Orion Hardware Labs" },
  { invoiceId: "INV-2026-9848", amount: "$12,300.00", vendor: "Horizon Telecom Networks" },
];

export const InteractiveSandboxApp: React.FC = () => {
  const [mounted, setMounted] = useState<boolean>(false);
  const [sampleIndex, setSampleIndex] = useState<number>(0);
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [formData, setFormData] = useState({ invoiceId: "", amount: "", vendor: "" });
  const [statusMsg, setStatusMsg] = useState<string>("");
  const [isAutoFilling, setIsAutoFilling] = useState<boolean>(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const currentSample = INVOICE_SAMPLES[sampleIndex] || INVOICE_SAMPLES[0];

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

  const handleCopy = async (fieldKey: string, value: string) => {
    try {
      if (typeof navigator !== "undefined" && navigator.clipboard) {
        await navigator.clipboard.writeText(value);
      }
    } catch {}
    setCopiedField(fieldKey);
    dispatchTelemetry("COPY", `#source-${fieldKey}`, value);
    setTimeout(() => setCopiedField(null), 1500);
  };

  const handlePaste = async (fieldKey: string, sampleFallback: string) => {
    let textToPaste = sampleFallback;
    try {
      if (typeof navigator !== "undefined" && navigator.clipboard) {
        const clip = await navigator.clipboard.readText();
        if (clip && clip.trim().length > 0) {
          textToPaste = clip;
        }
      }
    } catch {}

    setFormData((prev) => {
      const nextForm = { ...prev, [fieldKey]: textToPaste };
      if (nextForm.invoiceId && nextForm.amount && nextForm.vendor) {
        setTimeout(() => {
          if (sampleIndex < INVOICE_SAMPLES.length - 1) {
            setSampleIndex((idx) => idx + 1);
            setFormData({ invoiceId: "", amount: "", vendor: "" });
            setStatusMsg(`[Sample Advanced] Moved to Invoice #${sampleIndex + 2} of 8`);
          }
        }, 1000);
      }
      return nextForm;
    });

    dispatchTelemetry("PASTE", `#target-erp-${fieldKey}`, textToPaste);
  };

  const handlePasteWrongData = (fieldKey: string) => {
    const wrongText = `ERR_TYPO_${Math.floor(Math.random() * 900 + 100)}`;
    setFormData((prev) => ({ ...prev, [fieldKey]: wrongText }));
    setStatusMsg(`[Mistake Injected] Pasted wrong value '${wrongText}' (Testing Noise Filter)`);
    dispatchTelemetry("NOISE_TYPO", `#target-erp-${fieldKey}`, wrongText);
  };

  const handleInputClick = (fieldKey: string) => {
    dispatchTelemetry("CLICK", `#target-erp-${fieldKey}`, "");
  };


  const handleAutoFillRemaining = async () => {
    setIsAutoFilling(true);
    setStatusMsg("🤖 Ghost Digital Employee auto-filling remaining invoices...");

    for (let idx = sampleIndex; idx < INVOICE_SAMPLES.length; idx++) {
      setSampleIndex(idx);
      const item = INVOICE_SAMPLES[idx];

      setFormData({ invoiceId: "", amount: "", vendor: "" });
      await new Promise((r) => setTimeout(r, 400));

      setFormData((prev) => ({ ...prev, invoiceId: item.invoiceId }));
      await dispatchTelemetry("PASTE", "#target-erp-invoiceId", item.invoiceId);
      await new Promise((r) => setTimeout(r, 300));

      setFormData((prev) => ({ ...prev, amount: item.amount }));
      await dispatchTelemetry("PASTE", "#target-erp-amount", item.amount);
      await new Promise((r) => setTimeout(r, 300));

      setFormData((prev) => ({ ...prev, vendor: item.vendor }));
      await dispatchTelemetry("PASTE", "#target-erp-vendor", item.vendor);
      await new Promise((r) => setTimeout(r, 600));
    }

    setIsAutoFilling(false);
    setStatusMsg("✅ Ghost completed auto-filling all 8 sample invoices!");
  };

  if (!mounted) return null;

  return (
    <div suppressHydrationWarning className="flex flex-col gap-4 rounded-2xl border border-cyan-500/30 bg-slate-900/90 p-5 shadow-2xl backdrop-blur-xl">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-cyan-500/10 p-2 text-cyan-400 border border-cyan-500/20">
            <Building2 className="h-4 w-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-slate-100">Live Sandboxed Enterprise Portal</h3>
              <span className="rounded-full bg-cyan-500/20 px-2 py-0.5 text-[10px] font-mono text-cyan-300 border border-cyan-500/30">
                Sample {sampleIndex + 1} of 8
              </span>
            </div>
            <p className="text-[10px] text-slate-400">Values advance dynamically after each copy/paste sequence</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            suppressHydrationWarning
            onClick={handleAutoFillRemaining}
            disabled={isAutoFilling}
            className="flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-purple-600 to-cyan-500 px-3.5 py-1.5 text-xs font-bold text-white shadow-lg shadow-purple-500/20 hover:brightness-110 transition disabled:opacity-50"
          >
            <Bot className={`h-4 w-4 ${isAutoFilling ? "animate-spin" : ""}`} />
            <span>{isAutoFilling ? "Ghost Auto-Filling..." : "Ghost Auto-Fill Remaining Invoices"}</span>
          </button>
        </div>
      </div>

      {/* Status Alert Banner */}
      {statusMsg && (
        <div className="rounded-lg bg-cyan-500/10 border border-cyan-500/30 px-3 py-1.5 text-center text-xs font-mono text-cyan-300 animate-pulse">
          {statusMsg}
        </div>
      )}

      {/* 2-Column Split: Left Source Invoice PDF, Right Target ERP Portal */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        {/* Left: Source Vendor Invoice */}
        <div className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-950/70 p-4">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
            <span className="font-bold text-slate-300">📄 Source Invoice PDF ({sampleIndex + 1}/8)</span>
            <span className="text-[10px] font-mono text-amber-400">Vendor Portal</span>
          </div>

          <div className="flex flex-col gap-2.5">
            <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/60 p-2">
              <div>
                <span className="text-[10px] text-slate-400">Invoice Number</span>
                <p id="source-invoiceId" className="font-mono font-bold text-slate-200">{currentSample.invoiceId}</p>
              </div>
              <button
                suppressHydrationWarning
                onClick={() => handleCopy("invoiceId", currentSample.invoiceId)}
                className="flex items-center gap-1 rounded-md bg-slate-800 px-2 py-1 text-[10px] text-slate-300 hover:bg-slate-700 hover:text-white transition"
              >
                {copiedField === "invoiceId" ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                <span>{copiedField === "invoiceId" ? "Copied" : "Copy"}</span>
              </button>
            </div>

            <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/60 p-2">
              <div>
                <span className="text-[10px] text-slate-400">Total Amount</span>
                <p id="source-amount" className="font-mono font-bold text-slate-200">{currentSample.amount}</p>
              </div>
              <button
                suppressHydrationWarning
                onClick={() => handleCopy("amount", currentSample.amount)}
                className="flex items-center gap-1 rounded-md bg-slate-800 px-2 py-1 text-[10px] text-slate-300 hover:bg-slate-700 hover:text-white transition"
              >
                {copiedField === "amount" ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                <span>{copiedField === "amount" ? "Copied" : "Copy"}</span>
              </button>
            </div>

            <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/60 p-2">
              <div>
                <span className="text-[10px] text-slate-400">Vendor Name</span>
                <p id="source-vendor" className="font-mono font-bold text-slate-200">{currentSample.vendor}</p>
              </div>
              <button
                suppressHydrationWarning
                onClick={() => handleCopy("vendor", currentSample.vendor)}
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
                  suppressHydrationWarning
                  id="target-erp-invoiceId"
                  type="text"
                  value={formData.invoiceId}
                  onChange={(e) => setFormData((prev) => ({ ...prev, invoiceId: e.target.value }))}
                  onClick={() => handleInputClick("invoiceId")}
                  placeholder="Click or paste invoice #..."
                  className="flex-1 rounded-md border border-slate-800 bg-slate-900 px-2.5 py-1.5 font-mono text-slate-200 focus:border-cyan-500 focus:outline-none"
                />
                <button
                  suppressHydrationWarning
                  onClick={() => handlePaste("invoiceId", currentSample.invoiceId)}
                  className="rounded-md bg-cyan-500/20 border border-cyan-500/30 px-2 py-1 text-[10px] font-bold text-cyan-300 hover:bg-cyan-500/30 transition"
                >
                  Paste
                </button>
                <button
                  suppressHydrationWarning
                  onClick={() => handlePasteWrongData("invoiceId")}
                  title="Paste wrong/noisy data to test GhostTrace Noise Filter"
                  className="rounded-md bg-rose-500/20 border border-rose-500/30 px-2 py-1 text-[10px] font-bold text-rose-300 hover:bg-rose-500/30 transition"
                >
                  Paste Wrong (Noise)
                </button>
              </div>
            </div>

            <div>
              <label className="text-[10px] text-slate-400 block mb-1">Target Amount</label>
              <div className="flex gap-1.5">
                <input
                  suppressHydrationWarning
                  id="target-erp-amount"
                  type="text"
                  value={formData.amount}
                  onChange={(e) => setFormData((prev) => ({ ...prev, amount: e.target.value }))}
                  onClick={() => handleInputClick("amount")}
                  placeholder="Click or paste amount..."
                  className="flex-1 rounded-md border border-slate-800 bg-slate-900 px-2.5 py-1.5 font-mono text-slate-200 focus:border-cyan-500 focus:outline-none"
                />
                <button
                  suppressHydrationWarning
                  onClick={() => handlePaste("amount", currentSample.amount)}
                  className="rounded-md bg-cyan-500/20 border border-cyan-500/30 px-2 py-1 text-[10px] font-bold text-cyan-300 hover:bg-cyan-500/30 transition"
                >
                  Paste
                </button>
                <button
                  suppressHydrationWarning
                  onClick={() => handlePasteWrongData("amount")}
                  title="Paste wrong/noisy data to test GhostTrace Noise Filter"
                  className="rounded-md bg-rose-500/20 border border-rose-500/30 px-2 py-1 text-[10px] font-bold text-rose-300 hover:bg-rose-500/30 transition"
                >
                  Paste Wrong (Noise)
                </button>
              </div>
            </div>

            <div>
              <label className="text-[10px] text-slate-400 block mb-1">Target Vendor Name</label>
              <div className="flex gap-1.5">
                <input
                  suppressHydrationWarning
                  id="target-erp-vendor"
                  type="text"
                  value={formData.vendor}
                  onChange={(e) => setFormData((prev) => ({ ...prev, vendor: e.target.value }))}
                  onClick={() => handleInputClick("vendor")}
                  placeholder="Click or paste vendor..."
                  className="flex-1 rounded-md border border-slate-800 bg-slate-900 px-2.5 py-1.5 font-mono text-slate-200 focus:border-cyan-500 focus:outline-none"
                />
                <button
                  suppressHydrationWarning
                  onClick={() => handlePaste("vendor", currentSample.vendor)}
                  className="rounded-md bg-cyan-500/20 border border-cyan-500/30 px-2 py-1 text-[10px] font-bold text-cyan-300 hover:bg-cyan-500/30 transition"
                >
                  Paste
                </button>
                <button
                  suppressHydrationWarning
                  onClick={() => handlePasteWrongData("vendor")}
                  title="Paste wrong/noisy data to test GhostTrace Noise Filter"
                  className="rounded-md bg-rose-500/20 border border-rose-500/30 px-2 py-1 text-[10px] font-bold text-rose-300 hover:bg-rose-500/30 transition"
                >
                  Paste Wrong (Noise)
                </button>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};
