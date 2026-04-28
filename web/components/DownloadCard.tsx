"use client";

import { QRCodeSVG } from "qrcode.react";

import type { BuildJob, ProjectMeta } from "@/lib/api";
import { api } from "@/lib/api";

interface Props {
  project: ProjectMeta;
  job: BuildJob | null;
}

export default function DownloadCard({ project, job }: Props) {
  const apkUrl = job && job.state === "succeeded" ? api.downloadUrl(job.job_id) : null;
  const zipUrl = api.zipUrl(project.project_id);

  // We need an absolute URL for the QR code (since users will scan it from
  // a phone). Resolve it client-side if possible.
  const absApkUrl =
    apkUrl && typeof window !== "undefined" ? new URL(apkUrl, window.location.href).toString() : apkUrl;

  return (
    <section className="border border-slate-200 dark:border-slate-800 rounded-md p-4 space-y-4">
      <h3 className="text-sm font-semibold">Artifacts</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-2">
          <p className="text-sm">
            <strong>Project zip</strong>
            <span className="block text-xs text-slate-500">
              The full Flutter project source.
            </span>
          </p>
          <a
            href={zipUrl}
            className="inline-flex items-center px-3 py-2 rounded-md bg-slate-900 text-white text-sm hover:bg-slate-800 dark:bg-slate-200 dark:text-slate-900 dark:hover:bg-white"
            download
          >
            Download .zip
          </a>
        </div>
        <div className="space-y-2">
          <p className="text-sm">
            <strong>APK</strong>
            <span className="block text-xs text-slate-500">
              {job?.builder === "stub"
                ? "Stub build — actually a renamed zip. Run with a real builder for a real APK."
                : "Built by the configured builder."}
            </span>
          </p>
          {absApkUrl ? (
            <div className="flex items-center gap-4">
              <a
                href={absApkUrl}
                className="inline-flex items-center px-3 py-2 rounded-md bg-blue-600 text-white text-sm hover:bg-blue-700"
                download
              >
                Download .apk
              </a>
              <div className="bg-white p-2 rounded">
                <QRCodeSVG value={absApkUrl} size={96} />
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-500">Build hasn&apos;t succeeded yet.</p>
          )}
        </div>
      </div>
    </section>
  );
}
