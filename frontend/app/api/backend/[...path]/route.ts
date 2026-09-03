import { NextRequest, NextResponse } from "next/server";

/**
 * Same-origin gateway to FastAPI.
 *
 * `BACKEND_API_BASE_URL` is deliberately server-only: browsers always call
 * `/api/backend/...`, while Docker can use `http://backend:8000/api/v1` and a
 * local Next.js server can use `http://localhost:8000/api/v1`.
 */
const backendBaseUrl = (
  process.env.BACKEND_API_BASE_URL
  // Backwards-compatible with existing local configuration files.
  ?? process.env.NEXT_PUBLIC_API_BASE_URL
  ?? "http://localhost:8000/api/v1"
).replace(/\/$/, "");

export const dynamic = "force-dynamic";

async function proxy(request: NextRequest, context: { params: { path: string[] } }) {
  const path = context.params.path.map(encodeURIComponent).join("/");
  const upstreamUrl = new URL(`${backendBaseUrl}/${path}`);
  upstreamUrl.search = request.nextUrl.search;

  const headers = new Headers();
  const contentType = request.headers.get("content-type");
  const accept = request.headers.get("accept");
  if (contentType) headers.set("content-type", contentType);
  if (accept) headers.set("accept", accept);

  try {
    const upstream = await fetch(upstreamUrl, {
      method: request.method,
      headers,
      body: ["GET", "HEAD"].includes(request.method) ? undefined : await request.arrayBuffer(),
      cache: "no-store",
    });

    const responseHeaders = new Headers();
    const upstreamContentType = upstream.headers.get("content-type");
    if (upstreamContentType) responseHeaders.set("content-type", upstreamContentType);

    return new NextResponse(upstream.body, { status: upstream.status, headers: responseHeaders });
  } catch {
    return NextResponse.json(
      { detail: "The API service is unavailable. Start the backend and verify BACKEND_API_BASE_URL." },
      { status: 502 },
    );
  }
}

export { proxy as GET, proxy as POST, proxy as PUT, proxy as PATCH, proxy as DELETE };
