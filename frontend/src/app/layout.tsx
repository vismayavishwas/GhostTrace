import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GhostTrace AI - Process Intelligence Platform",
  description: "Enterprise autonomous process intelligence and workflow automation platform powered by Google Vertex AI & LangGraph.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-slate-100 min-h-screen flex flex-col antialiased">
        {children}
      </body>
    </html>
  );
}
