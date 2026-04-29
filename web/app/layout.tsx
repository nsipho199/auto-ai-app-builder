import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Auto AI App Builder",
  description: "Idea-to-APK in minutes.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <header className="border-b border-slate-200 dark:border-slate-800">
          <div className="mx-auto max-w-6xl px-6 py-4 flex items-center justify-between">
            <h1 className="text-lg font-semibold tracking-tight">Auto AI App Builder</h1>
            <nav className="flex items-center gap-4">
              <a href="/calculator" className="text-sm text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100 transition-colors">
                Calculator
              </a>
              <span className="text-xs uppercase tracking-widest text-slate-500">MVP</span>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
