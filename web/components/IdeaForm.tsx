"use client";

import { useState } from "react";

import type { Architecture, IdeaSpec } from "@/lib/api";

import ArchitectureCheckboxes from "./ArchitectureCheckboxes";

interface Props {
  busy: boolean;
  onSubmit: (spec: IdeaSpec) => void;
}

const SAMPLES: { label: string; idea: string }[] = [
  { label: "Notes", idea: "A simple notes app that stores items in a list." },
  { label: "Calculator", idea: "A basic four-function calculator." },
  { label: "Translator", idea: "Siswati ↔ English phrase translator." },
  { label: "Flashlight", idea: "A flashlight that toggles a bright white screen." },
];

export default function IdeaForm({ busy, onSubmit }: Props) {
  const [idea, setIdea] = useState("");
  const [appName, setAppName] = useState("");
  const [archs, setArchs] = useState<Architecture[]>(["arm64-v8a", "x86_64"]);
  const [color, setColor] = useState("#1976d2");

  const submit = () => {
    if (!idea.trim()) return;
    onSubmit({
      idea: idea.trim(),
      app_name: appName.trim() || null,
      architectures: archs,
      primary_color: color,
    });
  };

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {SAMPLES.map((s) => (
          <button
            key={s.label}
            type="button"
            className="text-xs px-3 py-1 rounded-full border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800"
            onClick={() => setIdea(s.idea)}
          >
            {s.label}
          </button>
        ))}
      </div>

      <label className="block">
        <span className="text-sm font-medium">Your idea</span>
        <textarea
          className="mt-1 w-full min-h-[120px] rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 p-3 text-sm"
          placeholder="A Siswati ↔ English translator…"
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
        />
      </label>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <label className="block">
          <span className="text-sm font-medium">App name (optional)</span>
          <input
            className="mt-1 w-full rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 p-2 text-sm"
            value={appName}
            onChange={(e) => setAppName(e.target.value)}
            placeholder="e.g. Siswati Phrasebook"
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium">Primary color</span>
          <input
            type="color"
            className="mt-1 h-10 w-20 rounded-md border border-slate-300 dark:border-slate-700"
            value={color}
            onChange={(e) => setColor(e.target.value)}
          />
        </label>
      </div>

      <ArchitectureCheckboxes value={archs} onChange={setArchs} />

      <div>
        <button
          type="button"
          disabled={busy || !idea.trim()}
          onClick={submit}
          className="px-4 py-2 rounded-md bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 disabled:opacity-60"
        >
          {busy ? "Generating…" : "Generate project"}
        </button>
      </div>
    </section>
  );
}
