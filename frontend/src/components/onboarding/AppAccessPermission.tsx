"use client";

import React, { useState } from "react";
import { ShieldCheck, Monitor, FileSpreadsheet, Globe, Lock } from "lucide-react";

export interface AppAccessPermissionProps {
  onGrantPermission: (selectedApps: string[]) => void;
}

export const AppAccessPermission: React.FC<AppAccessPermissionProps> = ({
  onGrantPermission,
}) => {
  const [apps, setApps] = useState<{ id: string; name: string; category: string; icon: any; enabled: boolean }[]>([
    { id: "chrome", name: "Google Chrome Browser", category: "Web Applications & ERP Portals", icon: Globe, enabled: true },
    { id: "sap", name: "SAP ERP Portal", category: "Enterprise Resource Planning", icon: Monitor, enabled: true },
    { id: "excel", name: "Microsoft Excel & PDF Viewer", category: "Documents & Spreadsheets", icon: FileSpreadsheet, enabled: true },
  ]);

  const toggleApp = (id: string) => {
    setApps((prev) => prev.map((a) => (a.id === id ? { ...a, enabled: !a.enabled } : a)));
  };

  const handleConfirm = () => {
    const selected = apps.filter((a) => a.enabled).map((a) => a.name);
    onGrantPermission(selected.length > 0 ? selected : ["Google Chrome Browser"]);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/90 p-4 backdrop-blur-xl">
      <div className="w-full max-w-lg rounded-2xl border border-slate-800 bg-slate-900/95 p-6 shadow-2xl backdrop-blur-2xl">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-cyan-500/10 p-3 text-cyan-400 border border-cyan-500/20">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight">GhostTrace Access Permission</h2>
            <p className="text-xs text-slate-400">Explicitly grant Shadow Mode observation privileges to target apps.</p>
          </div>
        </div>

        <div className="mt-6 flex flex-col gap-3">
          {apps.map((app) => {
            const Icon = app.icon;
            return (
              <div
                key={app.id}
                onClick={() => toggleApp(app.id)}
                className={`flex items-center justify-between rounded-xl border p-4 cursor-pointer transition-all duration-200 ${
                  app.enabled
                    ? "border-cyan-500/40 bg-slate-800/80 shadow-md shadow-cyan-500/5"
                    : "border-slate-800 bg-slate-950/40 opacity-60"
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`rounded-lg p-2.5 ${app.enabled ? "bg-cyan-500/10 text-cyan-400" : "bg-slate-800 text-slate-500"}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-slate-200">{app.name}</h4>
                    <p className="text-[11px] text-slate-400">{app.category}</p>
                  </div>
                </div>

                <div className={`relative h-6 w-11 rounded-full transition-colors ${app.enabled ? "bg-cyan-500" : "bg-slate-800"}`}>
                  <div
                    className={`absolute top-1 h-4 w-4 rounded-full bg-white transition-transform ${
                      app.enabled ? "left-6" : "left-1"
                    }`}
                  />
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-6 flex items-center justify-between border-t border-slate-800/80 pt-4">
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <Lock className="h-3.5 w-3.5 text-emerald-400" />
            <span>Read-Only Perception Isolation Active</span>
          </div>
          <button
            onClick={handleConfirm}
            className="rounded-xl bg-cyan-500 px-5 py-2.5 text-xs font-bold text-slate-950 shadow-lg shadow-cyan-500/25 transition-all hover:bg-cyan-400 hover:shadow-cyan-500/40"
          >
            Grant Access & Enable Shadow Mode
          </button>
        </div>
      </div>
    </div>
  );
};
