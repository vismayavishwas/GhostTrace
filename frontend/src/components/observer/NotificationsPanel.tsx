"use client";

import React from "react";

export interface NotificationData {
  notification_id: string;
  notification_type: string;
  title: string;
  message: string;
  severity?: "INFO" | "SUCCESS" | "WARNING" | "ERROR";
  timestamp?: string;
}

export interface NotificationsPanelProps {
  notifications?: NotificationData[];
}

export const NotificationsPanel: React.FC<NotificationsPanelProps> = ({
  notifications = [],
}) => {
  const getSeverityStyle = (sev?: string) => {
    switch (sev) {
      case "SUCCESS":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
      case "WARNING":
        return "bg-amber-500/10 text-amber-400 border-amber-500/20";
      case "ERROR":
        return "bg-rose-500/10 text-rose-400 border-rose-500/20";
      default:
        return "bg-cyan-500/10 text-cyan-400 border-cyan-500/20";
    }
  };

  return (
    <div className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl backdrop-blur-sm">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500"></span>
          </span>
          <h3 className="text-sm font-semibold text-slate-200">Observer Stream Notifications</h3>
        </div>
        <span className="text-xs text-slate-500">{notifications.length} alerts</span>
      </div>

      <div className="flex max-h-80 flex-col gap-2.5 overflow-y-auto pr-1">
        {notifications.length === 0 ? (
          <div className="py-6 text-center text-xs text-slate-500">No stream notifications yet.</div>
        ) : (
          notifications.map((n) => (
            <div
              key={n.notification_id}
              className="flex flex-col gap-1 rounded-lg border border-slate-800/60 bg-slate-950/50 p-3 transition hover:border-slate-700/80"
            >
              <div className="flex items-center justify-between gap-2">
                <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold border ${getSeverityStyle(n.severity)}`}>
                  {n.notification_type}
                </span>
                <span className="text-[10px] text-slate-500 font-mono">
                  {n.timestamp ? new Date(n.timestamp).toLocaleTimeString() : "Just now"}
                </span>
              </div>
              <h4 className="mt-1 text-xs font-semibold text-slate-200">{n.title}</h4>
              <p className="text-[11px] text-slate-400 leading-relaxed">{n.message}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
