"use client";

import React, { useState, useEffect } from "react";
import { Building2, Copy, Check, ArrowRight, Play, Sparkles, Bot, RotateCcw, UserCheck, Briefcase, DollarSign, FileText } from "lucide-react";
import { postTelemetryEvent, fetchGraphState } from "@/lib/api";

export type SandboxDomain = "FINANCE" | "HR" | "SALES";

export interface SandboxSample {
  field1Key: string;
  field1Label: string;
  field1Value: string;
  field2Key: string;
  field2Label: string;
  field2Value: string;
  field3Key: string;
  field3Label: string;
  field3Value: string;
}

const FINANCE_SAMPLES: SandboxSample[] = [
  { field1Key: "invoiceId", field1Label: "Invoice ID", field1Value: "INV-2026-9841", field2Key: "amount", field2Label: "Amount", field2Value: "$14,850.00", field3Key: "vendor", field3Label: "Vendor", field3Value: "Acme Cloud Logistics" },
  { field1Key: "invoiceId", field1Label: "Invoice ID", field1Value: "INV-2026-9842", field2Key: "amount", field2Label: "Amount", field2Value: "$22,400.00", field3Key: "vendor", field3Label: "Vendor", field3Value: "Global Tech Systems" },
  { field1Key: "invoiceId", field1Label: "Invoice ID", field1Value: "INV-2026-9843", field2Key: "amount", field2Label: "Amount", field2Value: "$8,750.50", field3Key: "vendor", field3Label: "Vendor", field3Value: "Nexus Freight Solutions" },
  { field1Key: "invoiceId", field1Label: "Invoice ID", field1Value: "INV-2026-9844", field2Key: "amount", field2Label: "Amount", field2Value: "$31,900.00", field3Key: "vendor", field3Label: "Vendor", field3Value: "Apex Industrial Supplies" },
  { field1Key: "invoiceId", field1Label: "Invoice ID", field1Value: "INV-2026-9845", field2Key: "amount", field2Label: "Amount", field2Value: "$19,250.75", field3Key: "vendor", field3Label: "Vendor", field3Value: "Vanguard Cyber Security" },
  { field1Key: "invoiceId", field1Label: "Invoice ID", field1Value: "INV-2026-9846", field2Key: "amount", field2Label: "Amount", field2Value: "$45,000.00", field3Key: "vendor", field3Label: "Vendor", field3Value: "Starlight Media Group" },
  { field1Key: "invoiceId", field1Label: "Invoice ID", field1Value: "INV-2026-9847", field2Key: "amount", field2Label: "Amount", field2Value: "$6,120.00", field3Key: "vendor", field3Label: "Vendor", field3Value: "Orion Hardware Labs" },
  { field1Key: "invoiceId", field1Label: "Invoice ID", field1Value: "INV-2026-9848", field2Key: "amount", field2Label: "Amount", field2Value: "$12,300.00", field3Key: "vendor", field3Label: "Vendor", field3Value: "Horizon Telecom Networks" },
];

const HR_SAMPLES: SandboxSample[] = [
  { field1Key: "name", field1Label: "Candidate Name", field1Value: "Elena Rostova", field2Key: "cgpa", field2Label: "CGPA", field2Value: "3.92 / 4.0", field3Key: "experience", field3Label: "Experience", field3Value: "5.5 Years" },
  { field1Key: "name", field1Label: "Candidate Name", field1Value: "Marcus Vance", field2Key: "cgpa", field2Label: "CGPA", field2Value: "3.85 / 4.0", field3Key: "experience", field3Label: "Experience", field3Value: "4.0 Years" },
  { field1Key: "name", field1Label: "Candidate Name", field1Value: "Sophia Chen", field2Key: "cgpa", field2Label: "CGPA", field2Value: "3.98 / 4.0", field3Key: "experience", field3Label: "Experience", field3Value: "7.2 Years" },
  { field1Key: "name", field1Label: "Candidate Name", field1Value: "David Miller", field2Key: "cgpa", field2Label: "CGPA", field2Value: "3.76 / 4.0", field3Key: "experience", field3Label: "Experience", field3Value: "3.5 Years" },
  { field1Key: "name", field1Label: "Candidate Name", field1Value: "Aisha Patel", field2Key: "cgpa", field2Label: "CGPA", field2Value: "3.90 / 4.0", field3Key: "experience", field3Label: "Experience", field3Value: "6.0 Years" },
  { field1Key: "name", field1Label: "Candidate Name", field1Value: "Lucas Thorne", field2Key: "cgpa", field2Label: "CGPA", field2Value: "3.82 / 4.0", field3Key: "experience", field3Label: "Experience", field3Value: "4.8 Years" },
  { field1Key: "name", field1Label: "Candidate Name", field1Value: "Hannah Kim", field2Key: "cgpa", field2Label: "CGPA", field2Value: "3.95 / 4.0", field3Key: "experience", field3Label: "Experience", field3Value: "8.0 Years" },
  { field1Key: "name", field1Label: "Candidate Name", field1Value: "Julian Ross", field2Key: "cgpa", field2Label: "CGPA", field2Value: "3.78 / 4.0", field3Key: "experience", field3Label: "Experience", field3Value: "2.5 Years" },
];

const SALES_SAMPLES: SandboxSample[] = [
  { field1Key: "customer", field1Label: "Customer Name", field1Value: "Acme Enterprise", field2Key: "email", field2Label: "Email Address", field2Value: "contact@acme.com", field3Key: "dealSize", field3Label: "Deal Size", field3Value: "$85,000 ARR" },
  { field1Key: "customer", field1Label: "Customer Name", field1Value: "Apex Solutions", field2Key: "email", field2Label: "Email Address", field2Value: "sales@apex.io", field3Key: "dealSize", field3Label: "Deal Size", field3Value: "$120,000 ARR" },
  { field1Key: "customer", field1Label: "Customer Name", field1Value: "Vanguard Tech", field2Key: "email", field2Label: "Email Address", field2Value: "info@vanguard.net", field3Key: "dealSize", field3Label: "Deal Size", field3Value: "$65,000 ARR" },
  { field1Key: "customer", field1Label: "Customer Name", field1Value: "Starlight Corp", field2Key: "email", field2Label: "Email Address", field2Value: "deals@starlight.com", field3Key: "dealSize", field3Label: "Deal Size", field3Value: "$210,000 ARR" },
  { field1Key: "customer", field1Label: "Customer Name", field1Value: "Orion Systems", field2Key: "email", field2Label: "Email Address", field2Value: "ops@orionsys.org", field3Key: "dealSize", field3Label: "Deal Size", field3Value: "$45,000 ARR" },
  { field1Key: "customer", field1Label: "Customer Name", field1Value: "Nexus Dynamics", field2Key: "email", field2Label: "Email Address", field2Value: "lead@nexusdyn.io", field3Key: "dealSize", field3Label: "Deal Size", field3Value: "$150,000 ARR" },
  { field1Key: "customer", field1Label: "Customer Name", field1Value: "Horizon Labs", field2Key: "email", field2Label: "Email Address", field2Value: "team@horizonlabs.ai", field3Key: "dealSize", field3Label: "Deal Size", field3Value: "$95,000 ARR" },
  { field1Key: "customer", field1Label: "Customer Name", field1Value: "Zenith Software", field2Key: "email", field2Label: "Email Address", field2Value: "biz@zenithsoft.com", field3Key: "dealSize", field3Label: "Deal Size", field3Value: "$175,000 ARR" },
];

export interface InteractiveSandboxAppProps {
  isDeploymentMode?: boolean;
}

export const InteractiveSandboxApp: React.FC<InteractiveSandboxAppProps> = ({ isDeploymentMode = false }) => {
  const [mounted, setMounted] = useState<boolean>(false);
  const [domain, setDomain] = useState<SandboxDomain>("FINANCE");
  const [sampleIndex, setSampleIndex] = useState<number>(0);
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [formData, setFormData] = useState({ f1: "", f2: "", f3: "" });
  const [statusMsg, setStatusMsg] = useState<string>("");
  const [isAutoFilling, setIsAutoFilling] = useState<boolean>(false);
  const [remainingCount, setRemainingCount] = useState<number>(8);

  useEffect(() => {
    setMounted(true);

    const handleReset = () => {
      setSampleIndex(0);
      setFormData({ f1: "", f2: "", f3: "" });
      setStatusMsg("");
    };

    const handleGlobalCopy = () => {
      const activeEl = typeof document !== "undefined" ? (document.activeElement as HTMLElement) : null;
      if (activeEl && !activeEl.closest("#sandbox-app")) return;
      const selection = window.getSelection()?.toString() || "";
      if (selection) {
        dispatchTelemetry("COPY", "window.selection", selection.slice(0, 30));
      }
    };

    const handleGlobalPaste = (e: ClipboardEvent) => {
      const target = e.target as HTMLElement;
      if (!target || !target.closest("#sandbox-app")) return;
      const text = e.clipboardData?.getData("text") || "";
      const id = target?.id ? `#${target.id}` : (target?.tagName.toLowerCase() || "input");
      dispatchTelemetry("PASTE", id, text.slice(0, 30));
    };

    if (typeof window !== "undefined") {
      window.addEventListener("ghosttrace:reset-sandbox", handleReset);
      window.addEventListener("copy", handleGlobalCopy);
      window.addEventListener("paste", handleGlobalPaste);
    }

    return () => {
      if (typeof window !== "undefined") {
        window.removeEventListener("ghosttrace:reset-sandbox", handleReset);
        window.removeEventListener("copy", handleGlobalCopy);
        window.removeEventListener("paste", handleGlobalPaste);
      }
    };
  }, []);



  const getDomainSamples = () => {
    if (domain === "HR") return HR_SAMPLES;
    if (domain === "SALES") return SALES_SAMPLES;
    return FINANCE_SAMPLES;
  };

  const samples = getDomainSamples();
  const currentSample = samples[sampleIndex] || samples[0];

  const getDomainTitles = () => {
    if (domain === "HR") {
      return { sourceTitle: "CANDIDATE RESUME PDF", targetTitle: "WORKDAY ATS PORTAL", icon: UserCheck, color: "text-purple-400" };
    }
    if (domain === "SALES") {
      return { sourceTitle: "EXCEL LEADS SPREADSHEET", targetTitle: "SALESFORCE CRM PORTAL", icon: Briefcase, color: "text-emerald-400" };
    }
    return { sourceTitle: "PDF INVOICE SOURCE", targetTitle: "SAP ERP FINANCIALS", icon: DollarSign, color: "text-cyan-400" };
  };

  const titles = getDomainTitles();

  const handleSwitchDomain = (newDomain: SandboxDomain) => {
    setDomain(newDomain);
    setSampleIndex(0);
    setFormData({ f1: "", f2: "", f3: "" });
    setStatusMsg(`[Environment Switched] Active Sandbox: ${newDomain}`);
  };

  const dispatchTelemetry = async (eventType: string, selector: string, value: string, explicitLabel?: string, isAutomated: boolean = false) => {
    const isSource = selector.includes("source");
    const appTitle = isSource ? titles.sourceTitle : titles.targetTitle;

    let labelText = explicitLabel || "";
    if (!labelText) {
      const selLower = String(selector || "").toLowerCase();
      if (selLower.includes("f1") || selLower.includes(currentSample.field1Key.toLowerCase())) {
        labelText = currentSample.field1Label;
      } else if (selLower.includes("f2") || selLower.includes(currentSample.field2Key.toLowerCase())) {
        labelText = currentSample.field2Label;
      } else if (selLower.includes("f3") || selLower.includes(currentSample.field3Key.toLowerCase())) {
        labelText = currentSample.field3Label;
      } else {
        labelText = "Field";
      }
    }

    const currentCycleId = `cycle-${sampleIndex + 1}`;

    const payload = {
      event_type: eventType,
      active_tab: appTitle,
      url: typeof window !== "undefined" ? window.location.href : "http://localhost:3000/demo",
      target_selector: selector,
      element_tag: isSource ? "BUTTON" : "INPUT",
      field_label: labelText,
      aria_label: labelText,
      placeholder: `Enter ${labelText}`,
      input_value: value,
      input_masked: value ? `${value[0]}***` : "",
      xpath: `//*[@id="${selector.replace("#", "")}"]`,
      bounding_box: { x: 120, y: 240, width: 200, height: 35 },
      scroll_pos: { x: 0, y: 0 },
      coordinates_x: 250.0,
      coordinates_y: 300.0,
      timestamp: new Date().toISOString(),
      app_title: appTitle,
      cycle_id: currentCycleId,
      metadata: { is_sandbox: true, field_label: labelText, aria_label: labelText, app_title: appTitle, is_automated: isAutomated, cycle_id: currentCycleId }
    };

    setStatusMsg(`[Telemetry Transmitted] ${eventType} on ${selector} ${isAutomated ? "(Automated)" : ""}`);
    await postTelemetryEvent(payload);
    setTimeout(() => setStatusMsg(""), 2000);
  };

  const handleCopy = async (fieldKey: string, value: string, label?: string) => {
    try {
      if (typeof navigator !== "undefined" && navigator.clipboard) {
        await navigator.clipboard.writeText(value);
      }
    } catch {}
    setCopiedField(fieldKey);
    dispatchTelemetry("COPY", `#source-${fieldKey}`, value, label);
    setTimeout(() => setCopiedField(null), 1500);
  };

  const handlePaste = async (fieldKey: string, sampleFallback: string, label?: string) => {
    let textToPaste = sampleFallback;
    try {
      if (typeof navigator !== "undefined" && navigator.clipboard) {
        const clip = await navigator.clipboard.readText();
        if (clip && clip.trim().length > 0) {
          textToPaste = clip;
        }
      }
    } catch {}

    setFormData((prev) => ({ ...prev, [fieldKey]: textToPaste }));
    dispatchTelemetry("PASTE", `#target-${fieldKey}`, textToPaste, label);
  };

  const handleNextRecord = () => {
    dispatchTelemetry("SUBMIT", "#btn-next-record", `Record ${sampleIndex + 2}`);
    if (sampleIndex < samples.length - 1) {
      const nextIdx = sampleIndex + 1;
      setSampleIndex(nextIdx);
      setFormData({ f1: "", f2: "", f3: "" });
      setStatusMsg(`[Record Advanced] Moved to Record ${nextIdx + 1} of ${samples.length}`);
    } else {
      setStatusMsg(`[End of Records] Completed all ${samples.length} ${domain} records!`);
    }
  };

  const handlePrevRecord = () => {
    if (sampleIndex > 0) {
      const prevIdx = sampleIndex - 1;
      setSampleIndex(prevIdx);
      setFormData({ f1: "", f2: "", f3: "" });
      setStatusMsg(`[Record Moved] Back to Record ${prevIdx + 1} of ${samples.length}`);
    }
  };

  const [autoStarted, setAutoStarted] = useState<boolean>(false);
  const [autoCursorPos, setAutoCursorPos] = useState<{ x: number; y: number } | null>(null);
  const [autoActionLabel, setAutoActionLabel] = useState<string | null>(null);

  useEffect(() => {
    if (isDeploymentMode && !autoStarted && !isAutoFilling && remainingCount > 0) {
      setAutoStarted(true);
      const timer = setTimeout(() => {
        handleAutoFillRemaining();
      }, 700);
      return () => clearTimeout(timer);
    }
  }, [isDeploymentMode, autoStarted, isAutoFilling, remainingCount]);

  const handleAutoFillRemaining = async () => {
    setIsAutoFilling(true);
    setStatusMsg(`🤖 Ghost Digital Employee executing parameterized Workflow DNA on remaining records...`);

    // Read current state to retrieve learned parameterized mappings
    let mappings: any[] = [];
    try {
      const state = await fetchGraphState();
      mappings = state?.observation_synthesis?.approved_workflow || state?.field_mappings || [];
    } catch {}

    const remainingStart = sampleIndex < 3 ? 3 : sampleIndex;

    for (let idx = remainingStart; idx < samples.length; idx++) {
      setSampleIndex(idx);
      const item = samples[idx];

      setFormData({ f1: "", f2: "", f3: "" });
      await new Promise((r) => setTimeout(r, 400));

      // 1. Field 1 Copy & Paste
      setAutoCursorPos({ x: 22, y: 35 });
      setAutoActionLabel(`COPY ${item.field1Label}`);
      await new Promise((r) => setTimeout(r, 400));

      setAutoCursorPos({ x: 78, y: 35 });
      setAutoActionLabel(`PASTE ${item.field1Label}`);
      setFormData((prev) => ({ ...prev, f1: item.field1Value }));
      await dispatchTelemetry("PASTE", `#target-${item.field1Key}`, item.field1Value, item.field1Label, true);
      await new Promise((r) => setTimeout(r, 500));

      // 2. Field 2 Copy & Paste
      setAutoCursorPos({ x: 22, y: 55 });
      setAutoActionLabel(`COPY ${item.field2Label}`);
      await new Promise((r) => setTimeout(r, 400));

      setAutoCursorPos({ x: 78, y: 55 });
      setAutoActionLabel(`PASTE ${item.field2Label}`);
      setFormData((prev) => ({ ...prev, f2: item.field2Value }));
      await dispatchTelemetry("PASTE", `#target-${item.field2Key}`, item.field2Value, item.field2Label, true);
      await new Promise((r) => setTimeout(r, 500));

      // 3. Field 3 Copy & Paste
      setAutoCursorPos({ x: 22, y: 75 });
      setAutoActionLabel(`COPY ${item.field3Label}`);
      await new Promise((r) => setTimeout(r, 400));

      setAutoCursorPos({ x: 78, y: 75 });
      setAutoActionLabel(`PASTE ${item.field3Label}`);
      setFormData((prev) => ({ ...prev, f3: item.field3Value }));
      await dispatchTelemetry("PASTE", `#target-${item.field3Key}`, item.field3Value, item.field3Label, true);
      await new Promise((r) => setTimeout(r, 500));

      // 4. Record Transition
      setAutoCursorPos({ x: 50, y: 92 });
      setAutoActionLabel("NEXT RECORD");
      await dispatchTelemetry("RECORD_TRANSITION", "#btn-next-record", `Record ${idx + 2}`, "Next Record", true);
      await new Promise((r) => setTimeout(r, 500));

      setRemainingCount(samples.length - 1 - idx);
    }

    setAutoCursorPos(null);
    setAutoActionLabel(null);
    setIsAutoFilling(false);
    setStatusMsg(`✅ Ghost completed autonomous execution across all remaining records! Remaining: 0`);
  };

  if (!mounted) return null;

  return (
    <div id="sandbox-app" suppressHydrationWarning className="relative flex flex-col gap-4 rounded-2xl border border-cyan-500/30 bg-slate-900/90 p-5 shadow-2xl backdrop-blur-xl">
      {/* Visual Phantom Cursor Overlay during Autonomous Execution */}
      {autoCursorPos && (
        <div
          className="absolute z-50 transition-all duration-500 ease-in-out pointer-events-none"
          style={{
            left: `${autoCursorPos.x}%`,
            top: `${autoCursorPos.y}%`,
          }}
        >
          <div className="relative flex items-center gap-1.5">
            <span className="absolute -top-2 -left-2 h-10 w-10 rounded-full border-2 border-emerald-400 animate-ping" />
            <svg className="h-8 w-8 text-emerald-400 drop-shadow-[0_0_15px_rgba(52,211,153,0.9)] animate-pulse" viewBox="0 0 24 24" fill="currentColor">
              <path d="M3 3l7 18 3-7 7-3L3 3z" />
            </svg>
            <span className="rounded bg-emerald-500 px-2 py-0.5 text-[10px] font-black text-slate-950 font-mono shadow-xl uppercase border border-emerald-300">
              🤖 GHOST: {autoActionLabel}
            </span>
          </div>
        </div>
      )}

      {/* Deployment Mode Banner */}
      {isDeploymentMode && (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-emerald-500/40 bg-gradient-to-r from-emerald-950/80 via-slate-900 to-purple-950/80 p-4 shadow-xl">
          <div className="flex items-center gap-3">
            <Bot className="h-6 w-6 text-emerald-400 shrink-0 animate-pulse" />
            <div>
              <div className="flex items-center gap-2">
                <h4 className="text-sm font-extrabold text-emerald-200">🚀 Digital Employee Deployment Engine Active</h4>
                <span className="rounded bg-emerald-500/20 px-2 py-0.5 text-[10px] font-mono text-emerald-300 font-bold border border-emerald-500/30">
                  Autonomous Replay Mode
                </span>
              </div>
              <p className="text-xs text-emerald-400/80">Executing canonical 1-cycle Workflow DNA sequence across remaining records.</p>
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs font-mono">
            <div className="flex flex-col items-end">
              <span className="text-[10px] text-slate-400 uppercase">Total Records</span>
              <span className="font-bold text-slate-200">8</span>
            </div>
            <div className="h-6 w-[1px] bg-slate-800" />
            <div className="flex flex-col items-end">
              <span className="text-[10px] text-slate-400 uppercase">Remaining</span>
              <span className={`font-bold ${remainingCount === 0 ? "text-emerald-400" : "text-amber-400"}`}>{remainingCount}</span>
            </div>

            <button
              suppressHydrationWarning
              onClick={handleAutoFillRemaining}
              disabled={isAutoFilling || remainingCount === 0}
              className="flex items-center gap-2 rounded-xl bg-emerald-500 px-4 py-2 text-xs font-black text-slate-950 shadow-lg shadow-emerald-500/20 hover:bg-emerald-400 transition disabled:opacity-50"
            >
              <Bot className={`h-4 w-4 ${isAutoFilling ? "animate-spin" : ""}`} />
              <span>{isAutoFilling ? "Executing Replay..." : remainingCount === 0 ? "✓ Completed 8 Records" : `Auto-Process Remaining (${remainingCount})`}</span>
            </button>
          </div>
        </div>
      )}

      {/* Top Header & Domain Switcher */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-cyan-500/10 p-2 text-cyan-400 border border-cyan-500/20">
            <Building2 className="h-4 w-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-slate-100">Live Sandboxed Enterprise Environments</h3>
              <span className="rounded-full bg-cyan-500/20 px-2 py-0.5 text-[10px] font-mono text-cyan-300 border border-cyan-500/30">
                Record {sampleIndex + 1} of 8
              </span>
            </div>
            <p className="text-[10px] text-slate-400">Interchangeable sandbox environments — telemetry processed identically by backend</p>
          </div>
        </div>

        {/* Environment Switcher Tabs */}
        <div className="flex items-center gap-1.5 rounded-xl border border-slate-800 bg-slate-950 p-1">
          <button
            suppressHydrationWarning
            onClick={() => handleSwitchDomain("FINANCE")}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1 text-xs font-bold transition ${
              domain === "FINANCE" ? "bg-cyan-500 text-slate-950 shadow-md" : "text-slate-400 hover:text-white"
            }`}
          >
            <span>💳 Finance</span>
          </button>

          <button
            suppressHydrationWarning
            onClick={() => handleSwitchDomain("HR")}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1 text-xs font-bold transition ${
              domain === "HR" ? "bg-purple-500 text-white shadow-md" : "text-slate-400 hover:text-white"
            }`}
          >
            <span>👥 HR / ATS</span>
          </button>

          <button
            suppressHydrationWarning
            onClick={() => handleSwitchDomain("SALES")}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1 text-xs font-bold transition ${
              domain === "SALES" ? "bg-emerald-500 text-slate-950 shadow-md" : "text-slate-400 hover:text-white"
            }`}
          >
            <span>📈 Sales / CRM</span>
          </button>
        </div>

        <div className="flex items-center gap-2">
          <button
            suppressHydrationWarning
            onClick={handleAutoFillRemaining}
            disabled={isAutoFilling}
            className="flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-purple-600 to-cyan-500 px-3.5 py-1.5 text-xs font-bold text-white shadow-lg shadow-purple-500/20 hover:brightness-110 transition disabled:opacity-50"
          >
            <Bot className={`h-4 w-4 ${isAutoFilling ? "animate-spin" : ""}`} />
            <span>🤖 Ghost Auto-Fill Remaining</span>
          </button>
        </div>
      </div>

      {/* Main 2-Column Portal Sandbox */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Left Column: Source Document / Spreadsheet App */}
        <div className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-950/80 p-4">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
            <span className="text-xs font-mono font-extrabold text-cyan-400 uppercase tracking-wider">
              1. {titles.sourceTitle}
            </span>
            <span className="rounded bg-slate-800 px-2 py-0.5 text-[9px] font-mono text-slate-400">
              Sample Record #{sampleIndex + 1}
            </span>
          </div>

          <div className="flex flex-col gap-2.5">
            {/* Field 1 */}
            <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/60 p-2.5">
              <div>
                <span className="text-[10px] font-semibold text-slate-400 block">{currentSample.field1Label}</span>
                <span className="text-xs font-mono font-bold text-slate-100">{currentSample.field1Value}</span>
              </div>
              <button
                suppressHydrationWarning
                onClick={() => handleCopy("f1", currentSample.field1Value, currentSample.field1Label)}
                className="flex items-center gap-1 rounded-md bg-cyan-500/10 px-2.5 py-1 text-[11px] font-semibold text-cyan-400 border border-cyan-500/20 hover:bg-cyan-500/20 transition"
              >
                {copiedField === "f1" ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                <span>{copiedField === "f1" ? "Copied!" : "Copy"}</span>
              </button>
            </div>

            {/* Field 2 */}
            <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/60 p-2.5">
              <div>
                <span className="text-[10px] font-semibold text-slate-400 block">{currentSample.field2Label}</span>
                <span className="text-xs font-mono font-bold text-slate-100">{currentSample.field2Value}</span>
              </div>
              <button
                suppressHydrationWarning
                onClick={() => handleCopy("f2", currentSample.field2Value, currentSample.field2Label)}
                className="flex items-center gap-1 rounded-md bg-cyan-500/10 px-2.5 py-1 text-[11px] font-semibold text-cyan-400 border border-cyan-500/20 hover:bg-cyan-500/20 transition"
              >
                {copiedField === "f2" ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                <span>{copiedField === "f2" ? "Copied!" : "Copy"}</span>
              </button>
            </div>

            {/* Field 3 */}
            <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/60 p-2.5">
              <div>
                <span className="text-[10px] font-semibold text-slate-400 block">{currentSample.field3Label}</span>
                <span className="text-xs font-mono font-bold text-slate-100">{currentSample.field3Value}</span>
              </div>
              <button
                suppressHydrationWarning
                onClick={() => handleCopy("f3", currentSample.field3Value, currentSample.field3Label)}
                className="flex items-center gap-1 rounded-md bg-cyan-500/10 px-2.5 py-1 text-[11px] font-semibold text-cyan-400 border border-cyan-500/20 hover:bg-cyan-500/20 transition"
              >
                {copiedField === "f3" ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                <span>{copiedField === "f3" ? "Copied!" : "Copy"}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Target System Portal */}
        <div className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-950/80 p-4">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
            <span className="text-xs font-mono font-extrabold text-emerald-400 uppercase tracking-wider">
              2. {titles.targetTitle}
            </span>
            <span className="rounded bg-emerald-500/10 px-2 py-0.5 text-[9px] font-mono text-emerald-400 border border-emerald-500/20">
              Target Form
            </span>
          </div>

          <div className="flex flex-col gap-2.5">
            {/* Target Field 1 */}
            <div className="flex flex-col gap-1">
              <label className="text-[10px] font-semibold text-slate-400">{currentSample.field1Label}</label>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  readOnly
                  placeholder={`Paste ${currentSample.field1Label}...`}
                  value={formData.f1}
                  className="flex-1 rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs font-mono text-slate-100 focus:outline-none"
                />
                <button
                  suppressHydrationWarning
                  onClick={() => handlePaste("f1", currentSample.field1Value, currentSample.field1Label)}
                  className="rounded-lg bg-emerald-500/20 px-3 py-1.5 text-xs font-bold text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/30 transition"
                >
                  Paste
                </button>
              </div>
            </div>

            {/* Target Field 2 */}
            <div className="flex flex-col gap-1">
              <label className="text-[10px] font-semibold text-slate-400">{currentSample.field2Label}</label>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  readOnly
                  placeholder={`Paste ${currentSample.field2Label}...`}
                  value={formData.f2}
                  className="flex-1 rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs font-mono text-slate-100 focus:outline-none"
                />
                <button
                  suppressHydrationWarning
                  onClick={() => handlePaste("f2", currentSample.field2Value, currentSample.field2Label)}
                  className="rounded-lg bg-emerald-500/20 px-3 py-1.5 text-xs font-bold text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/30 transition"
                >
                  Paste
                </button>
              </div>
            </div>

            {/* Target Field 3 */}
            <div className="flex flex-col gap-1">
              <label className="text-[10px] font-semibold text-slate-400">{currentSample.field3Label}</label>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  readOnly
                  placeholder={`Paste ${currentSample.field3Label}...`}
                  value={formData.f3}
                  className="flex-1 rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs font-mono text-slate-100 focus:outline-none"
                />
                <button
                  suppressHydrationWarning
                  onClick={() => handlePaste("f3", currentSample.field3Value, currentSample.field3Label)}
                  className="rounded-lg bg-emerald-500/20 px-3 py-1.5 text-xs font-bold text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/30 transition"
                >
                  Paste
                </button>
              </div>
            </div>

            {/* Manual Navigation Controls (Explicit user control per record) */}
            <div className="flex items-center justify-between border-t border-slate-800 pt-3 mt-1">
              <button
                suppressHydrationWarning
                disabled={sampleIndex === 0}
                onClick={handlePrevRecord}
                className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:bg-slate-800 disabled:opacity-40 transition"
              >
                ⬅️ Prev Record
              </button>

              <span className="text-[11px] font-mono text-cyan-400 font-bold">
                Record {sampleIndex + 1} of {samples.length}
              </span>

              <button
                suppressHydrationWarning
                onClick={handleNextRecord}
                className="flex items-center gap-1.5 rounded-lg border border-cyan-500/40 bg-cyan-500/20 px-3 py-1.5 text-xs font-bold text-cyan-300 hover:bg-cyan-500/30 transition shadow-lg"
              >
                <span>Next Record ➡️</span>
              </button>
            </div>
          </div>
        </div>
      </div>


      {statusMsg && (
        <div className="rounded-xl border border-cyan-500/30 bg-slate-950 px-3.5 py-1.5 text-[11px] font-mono text-cyan-300 animate-pulse">
          {statusMsg}
        </div>
      )}
    </div>
  );
};
