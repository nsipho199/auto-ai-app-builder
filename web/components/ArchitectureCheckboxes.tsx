"use client";

import type { Architecture } from "@/lib/api";

const ALL: { value: Architecture; label: string; help: string }[] = [
  { value: "arm64-v8a", label: "arm64-v8a", help: "Modern 64-bit phones" },
  { value: "x86_64", label: "x86_64", help: "Emulators / Chromebooks" },
  { value: "armeabi-v7a", label: "armeabi-v7a", help: "Older 32-bit phones" },
];

interface Props {
  value: Architecture[];
  onChange: (next: Architecture[]) => void;
}

export default function ArchitectureCheckboxes({ value, onChange }: Props) {
  const toggle = (arch: Architecture) => {
    if (value.includes(arch)) {
      onChange(value.filter((a) => a !== arch));
    } else {
      onChange([...value, arch]);
    }
  };
  return (
    <fieldset>
      <legend className="text-sm font-medium">Architectures</legend>
      <div className="mt-2 grid grid-cols-1 sm:grid-cols-3 gap-2">
        {ALL.map((a) => {
          const checked = value.includes(a.value);
          return (
            <label
              key={a.value}
              className={`flex items-start gap-2 p-3 border rounded-md cursor-pointer ${
                checked
                  ? "border-blue-500 bg-blue-50 dark:bg-blue-950/40"
                  : "border-slate-300 dark:border-slate-700"
              }`}
            >
              <input
                type="checkbox"
                checked={checked}
                onChange={() => toggle(a.value)}
                className="mt-1"
              />
              <span>
                <span className="block text-sm font-medium">{a.label}</span>
                <span className="block text-xs text-slate-500">{a.help}</span>
              </span>
            </label>
          );
        })}
      </div>
    </fieldset>
  );
}
