import { type NextRequest, NextResponse } from "next/server"
import { openai } from "@ai-sdk/openai"
import { generateObject } from "ai"
import { z } from "zod"

const HighlightSchema = z.object({
  highlights: z.array(
    z.object({
      factIndex: z.number().describe("Index of the fact (0-based)"),
      factText: z.string().describe("The original fact text"),
      mentions: z.array(
        z.object({
          text: z.string().describe("The exact text that mentions the fact"),
          startIndex: z.number().describe("Start position in the response text"),
          endIndex: z.number().describe("End position in the response text"),
          confidence: z.number().min(0).max(1).describe("Confidence score 0-1"),
          type: z.enum(["direct", "paraphrase", "implicit"]).describe("Type of mention"),
        }),
      ),
    }),
  ),
})

export async function POST(request: NextRequest) {
  try {
    const { response: responseText, facts } = await request.json()

    if (!responseText || !facts || !Array.isArray(facts)) {
      return NextResponse.json({ error: "Missing required fields: response and facts array" }, { status: 400 })
    }

    console.log("Highlighting facts in response:", {
      responseLength: responseText.length,
      factsCount: facts.length,
    })

    // Use OpenAI to identify fact mentions
    const result = await generateObject({
      model: openai("gpt-4o"),
      schema: HighlightSchema,
      prompt: `
You are an expert fact-checker. Analyze the following response text and identify where each of the provided facts is mentioned.

RESPONSE TEXT:
"""
${responseText}
"""

FACTS TO FIND:
${facts.map((fact, index) => `${index}: ${fact}`).join("\n")}

For each fact, find ALL mentions in the response text, including:
1. DIRECT mentions - exact or very similar wording
2. PARAPHRASES - same meaning but different words  
3. IMPLICIT references - indirect references or implications

For each mention found:
- Provide the exact text span that mentions the fact
- Give precise start and end character indices (0-based)
- Assign confidence score (0.8+ for direct, 0.6+ for paraphrases, 0.4+ for implicit)
- Classify the mention type

Be thorough but accurate with the character indices. Double-check that the indices correctly correspond to the mentioned text.

If a fact is not mentioned at all, don't include it in the results.
      `,
    })

    console.log("OpenAI highlight result:", result.object)

    // Validate the indices
    const validatedHighlights = {
      highlights: result.object.highlights
        .map((highlight) => ({
          ...highlight,
          mentions: highlight.mentions.filter((mention) => {
            const isValid =
              mention.startIndex >= 0 &&
              mention.endIndex > mention.startIndex &&
              mention.endIndex <= responseText.length &&
              responseText.slice(mention.startIndex, mention.endIndex) === mention.text

            if (!isValid) {
              console.warn("Invalid mention indices:", mention)
            }

            return isValid
          }),
        }))
        .filter((highlight) => highlight.mentions.length > 0),
    }

    return NextResponse.json(validatedHighlights)
  } catch (error) {
    console.error("Error in highlight-facts API:", error)

    // Fallback: simple keyword highlighting
    try {
      const { response: responseText, facts } = await request.json()

      const fallbackHighlights = {
        highlights: facts
          .map((fact, factIndex) => {
            const mentions = []
            const keywords = fact
              .toLowerCase()
              .split(" ")
              .filter((word) => word.length > 3)

            for (const keyword of keywords) {
              let startIndex = 0
              while (true) {
                const index = responseText.toLowerCase().indexOf(keyword, startIndex)
                if (index === -1) break

                mentions.push({
                  text: responseText.slice(index, index + keyword.length),
                  startIndex: index,
                  endIndex: index + keyword.length,
                  confidence: 0.6,
                  type: "direct" as const,
                })

                startIndex = index + 1
              }
            }

            return {
              factIndex,
              factText: fact,
              mentions,
            }
          })
          .filter((highlight) => highlight.mentions.length > 0),
      }

      return NextResponse.json(fallbackHighlights)
    } catch (fallbackError) {
      return NextResponse.json({ error: "Failed to highlight facts", details: error.message }, { status: 500 })
    }
  }
}
