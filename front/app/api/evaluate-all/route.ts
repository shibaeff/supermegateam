export async function POST(request: Request) {
  try {
    const body = await request.json()

    const response = await fetch("https://4a35-185-199-104-14.ngrok-free.app/api/eval-all", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()

    // Ensure we have original_answers field, fallback to responses if not provided
    if (!data.original_answers && data.responses) {
      data.original_answers = data.responses
    }

    return Response.json(data)
  } catch (error) {
    console.error("Error calling detailed evaluation API:", error)
    return Response.json({ error: "Failed to evaluate" }, { status: 500 })
  }
}
