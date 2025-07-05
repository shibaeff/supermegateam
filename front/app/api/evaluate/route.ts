import type { NextRequest } from "next/server"

const UPSTREAM_URL = "https://4a35-185-199-104-14.ngrok-free.app/api/eval-facts"

export async function POST(request: NextRequest) {
  try {
    const { prompts, facts } = await request.json()

    const upstreamRes = await fetch(UPSTREAM_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      // Disable any edge/runtime cache – we always want fresh results
      cache: "no-store",
      body: JSON.stringify({ prompts, facts }),
    })

    if (!upstreamRes.ok) {
      return new Response(JSON.stringify({ error: "Upstream error" }), { status: upstreamRes.status })
    }

    const data = await upstreamRes.json() // { percentages: [...] }
    return Response.json(data)
  } catch (err) {
    console.error("Proxy error:", err)
    return new Response(JSON.stringify({ error: "Failed to call evaluation service" }), { status: 500 })
  }
}
