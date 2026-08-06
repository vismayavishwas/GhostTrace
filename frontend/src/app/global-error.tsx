"use client";

import React from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-100 font-sans min-h-screen flex items-center justify-center p-6">
        <div className="flex max-w-md flex-col items-center gap-4 rounded-2xl border border-red-500/30 bg-slate-900/90 p-6 text-center shadow-2xl backdrop-blur-xl">
          <div className="rounded-full bg-red-500/10 p-3 text-red-400 border border-red-500/20">
            ⚠️
          </div>
          <h2 className="text-lg font-bold text-white">Global Application Error</h2>
          <p className="text-xs text-slate-400 font-mono bg-slate-950 p-3 rounded-lg border border-slate-800 text-left w-full">
            {error.message || "A global error occurred."}
          </p>
          <button
            onClick={() => reset()}
            className="rounded-xl bg-cyan-500 px-5 py-2 text-xs font-extrabold text-slate-950 hover:bg-cyan-400 transition"
          >
            Reload Application
          </button>
        </div>
      </body>
    </html>
  );
}
