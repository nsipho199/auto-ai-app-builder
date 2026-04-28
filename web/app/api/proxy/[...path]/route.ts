// Forwards /api/proxy/* to the FastAPI backend so the browser doesn't need
// to know about the backend host (and we avoid CORS in dev).

import { NextRequest, NextResponse } from "next/server";

const BACKEND = process.env.BACKEND_URL ?? "http://localhost:8000";

async function forward(req: NextRequest, ctx: { params: { path: string[] } }) {
  const path = ctx.params.path.join("/");
  const url = new URL(`/${path}`, BACKEND);
  url.search = req.nextUrl.search;

  const init: RequestInit = {
    method: req.method,
    headers: filterHeaders(req.headers),
    redirect: "manual",
  };
  if (req.method !== "GET" && req.method !== "HEAD") {
    init.body = await req.arrayBuffer();
  }

  let upstream: Response;
  try {
    upstream = await fetch(url.toString(), init);
  } catch (e) {
    return NextResponse.json(
      { error: `proxy: failed to reach backend at ${BACKEND}: ${(e as Error).message}` },
      { status: 502 },
    );
  }

  const body = upstream.body;
  const headers = new Headers(upstream.headers);
  // Don't leak hop-by-hop headers.
  headers.delete("transfer-encoding");
  return new NextResponse(body, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers,
  });
}

function filterHeaders(h: Headers): Headers {
  const out = new Headers();
  h.forEach((v, k) => {
    const lk = k.toLowerCase();
    if (lk === "host" || lk === "connection" || lk === "content-length") return;
    out.set(k, v);
  });
  return out;
}

export const GET = forward;
export const POST = forward;
export const PUT = forward;
export const PATCH = forward;
export const DELETE = forward;
export const HEAD = forward;
export const OPTIONS = forward;
