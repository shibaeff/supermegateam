"use client"

import { useState } from "react"
import { v4 as uuidv4 } from "uuid"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import {
  LayoutDashboard,
  MessageSquare,
  Database,
  Users,
  Tag,
  Settings,
  Building,
  CreditCard,
  Plus,
  X,
  Download,
  Calendar,
  Filter,
  BarChart3,
  ChevronDown,
  ChevronRight,
  Sparkles,
  Target,
  TrendingUp,
} from "lucide-react"

interface ListItem {
  id: string
  text: string
}

interface EvaluationResult {
  factIndex: number
  factText: string
  mentionRate: number
  source: string
  timestamp: string
}

interface DetailedEvaluationResult {
  fact_ids_per_context: number[][]
  percentages: number[]
  prompt_response_pairs: string[]
  responses: string[]
  original_answers?: string[]
}

interface FactHighlight {
  factIndex: number
  factText: string
  mentions: {
    text: string
    startIndex: number
    endIndex: number
    confidence: number
    type?: string
  }[]
}

interface HighlightData {
  highlights: FactHighlight[]
}

export default function LLMEvaluationDashboard() {
  const [facts, setFacts] = useState<ListItem[]>([
    { id: uuidv4(), text: "BMW electric cars have a great range" },
    { id: uuidv4(), text: "BMW cars have sleek modern design" },
    { id: uuidv4(), text: "BMW supports LGBTQ" },
  ])
  const [prompts, setPrompts] = useState<ListItem[]>([
    { id: uuidv4(), text: "BEST SUV's of 2025" },
    { id: uuidv4(), text: "What is so special about BMW electric cars" },
    { id: uuidv4(), text: "Car brands that support minorities" },
    { id: uuidv4(), text: "BMW VS Mercedes electric cars" },
  ])
  const [results, setResults] = useState<EvaluationResult[]>([])
  const [detailedResults, setDetailedResults] = useState<DetailedEvaluationResult | null>(null)
  const [highlights, setHighlights] = useState<Map<number, HighlightData>>(new Map())
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [activeSection, setActiveSection] = useState("dashboard")
  const [isLoading, setIsLoading] = useState(false)
  const [expandedPrompts, setExpandedPrompts] = useState<Set<number>>(new Set())
  const [highlightingPrompts, setHighlightingPrompts] = useState<Set<number>>(new Set())

  const addFact = () => {
    setFacts([...facts, { id: uuidv4(), text: "" }])
  }

  const removeFact = (id: string) => {
    if (facts.length > 1) {
      setFacts(facts.filter((fact) => fact.id !== id))
    }
  }

  const updateFact = (id: string, text: string) => {
    setFacts(facts.map((fact) => (fact.id === id ? { ...fact, text } : fact)))
  }

  const addPrompt = () => {
    setPrompts([...prompts, { id: uuidv4(), text: "" }])
  }

  const removePrompt = (id: string) => {
    if (prompts.length > 1) {
      setPrompts(prompts.filter((prompt) => prompt.id !== id))
    }
  }

  const updatePrompt = (id: string, text: string) => {
    setPrompts(prompts.map((prompt) => (prompt.id === id ? { ...prompt, text } : prompt)))
  }

  const genPercForFactsAndPrompts = async (facts: string[], prompts: string[]): Promise<number[]> => {
    try {
      const response = await fetch("/api/evaluate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompts: prompts,
          facts: facts,
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data.percentages
    } catch (error) {
      console.error("Error calling evaluation API:", error)
      return facts.map(() => Math.random())
    }
  }

  const getDetailedEvaluation = async (
    facts: string[],
    prompts: string[],
  ): Promise<DetailedEvaluationResult | null> => {
    try {
      const response = await fetch("/api/evaluate-all", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompts: prompts,
          facts: facts,
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error("Error calling detailed evaluation API:", error)
      return null
    }
  }

  const highlightFactsInResponse = async (responseText: string, facts: string[], promptIndex: number) => {
    try {
      setHighlightingPrompts((prev) => new Set([...prev, promptIndex]))

      const response = await fetch("/api/highlight-facts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          response: responseText,
          facts: facts,
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const highlightData = await response.json()
      console.log("Highlight data received:", highlightData)
      setHighlights((prev) => new Map([...prev, [promptIndex, highlightData]]))
    } catch (error) {
      console.error("Error highlighting facts:", error)
    } finally {
      setHighlightingPrompts((prev) => {
        const newSet = new Set(prev)
        newSet.delete(promptIndex)
        return newSet
      })
    }
  }

  const generateResults = async (): Promise<EvaluationResult[]> => {
    const factsList = facts.filter((f) => f.text.trim()).map((f) => f.text)
    const promptsList = prompts.filter((p) => p.text.trim()).map((p) => p.text)

    const percentages = await genPercForFactsAndPrompts(factsList, promptsList)

    return factsList.map((factText, index) => ({
      factIndex: index,
      factText: factText,
      mentionRate: Math.round(percentages[index] * 100),
      source: "eval-api",
      timestamp: "just now",
    }))
  }

  const handleSubmitAll = async () => {
    try {
      setIsLoading(true)
      setIsSubmitted(false)
      setHighlights(new Map())

      const factsList = facts.filter((f) => f.text.trim()).map((f) => f.text)
      const promptsList = prompts.filter((p) => p.text.trim()).map((p) => p.text)

      const [generatedResults, detailedEval] = await Promise.all([
        generateResults(),
        getDetailedEvaluation(factsList, promptsList),
      ])

      setResults(generatedResults)
      setDetailedResults(detailedEval)
      setIsSubmitted(true)
    } catch (error) {
      console.error("Error during evaluation:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const togglePromptExpansion = (index: number) => {
    const newExpanded = new Set(expandedPrompts)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedPrompts(newExpanded)
  }

  const getFactsForPrompt = (promptIndex: number): string[] => {
    if (!detailedResults) return []
    const factIds = detailedResults.fact_ids_per_context[promptIndex] || []
    return factIds.map((id) => facts[id]?.text || `Fact ${id + 1}`).filter(Boolean)
  }

  const renderHighlightedText = (text: string, promptIndex: number) => {
    const highlightData = highlights.get(promptIndex)

    console.log(`Rendering highlights for prompt ${promptIndex}:`, highlightData)

    if (!highlightData || !highlightData.highlights || highlightData.highlights.length === 0) {
      return <span>{text}</span>
    }

    const allMentions = highlightData.highlights
      .flatMap(
        (highlight) =>
          highlight.mentions?.map((mention) => ({
            ...mention,
            factIndex: highlight.factIndex,
            factText: highlight.factText,
          })) || [],
      )
      .filter(
        (mention) =>
          mention.startIndex >= 0 && mention.endIndex > mention.startIndex && mention.endIndex <= text.length,
      )
      .sort((a, b) => a.startIndex - b.startIndex)

    console.log(`Found ${allMentions.length} mentions for prompt ${promptIndex}`)

    if (allMentions.length === 0) {
      return <span>{text}</span>
    }

    const parts = []
    let lastIndex = 0

    allMentions.forEach((mention, index) => {
      if (mention.startIndex > lastIndex) {
        parts.push(<span key={`text-${index}`}>{text.slice(lastIndex, mention.startIndex)}</span>)
      }

      const mentionType = mention.type || "direct"
      const bgClass =
        mentionType === "direct"
          ? "bg-red-300 border-red-600"
          : mentionType === "paraphrase"
            ? "bg-red-200 border-red-500"
            : "bg-red-100 border-red-400"

      parts.push(
        <span
          key={`highlight-${index}`}
          className={`${bgClass} border-2 rounded px-1 py-0.5 font-bold text-red-900 shadow-sm`}
          title={`Narrative Point ${mention.factIndex + 1}: "${mention.factText}" 
Type: ${mentionType}
Confidence: ${Math.round((mention.confidence || 0.8) * 100)}%`}
        >
          {text.slice(mention.startIndex, mention.endIndex)}
        </span>,
      )

      lastIndex = mention.endIndex
    })

    if (lastIndex < text.length) {
      parts.push(<span key="text-end">{text.slice(lastIndex)}</span>)
    }

    return <>{parts}</>
  }

  const sidebarItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard, section: "General" },
    { id: "prompts", label: "Prompts", icon: MessageSquare, section: "General" },
    { id: "sources", label: "Sources", icon: Database, section: "General" },
    { id: "competitors", label: "Competitors", icon: Users, section: "Preferences", badge: "10+" },
    { id: "tags", label: "Tags", icon: Tag, section: "Preferences" },
    { id: "people", label: "People", icon: Users, section: "Settings" },
    { id: "workspace", label: "Workspace", icon: Building, section: "Settings" },
    { id: "company", label: "Company", icon: Building, section: "Settings" },
    { id: "billing", label: "Billing", icon: CreditCard, section: "Settings" },
  ]

  const groupedItems = sidebarItems.reduce(
    (acc, item) => {
      if (!acc[item.section]) acc[item.section] = []
      acc[item.section].push(item)
      return acc
    },
    {} as Record<string, typeof sidebarItems>,
  )

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            <span className="font-semibold text-gray-900">LLM Eval</span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto py-4">
          {Object.entries(groupedItems).map(([section, items]) => (
            <div key={section} className="mb-6">
              <div className="px-4 mb-2">
                <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider">{section}</h3>
              </div>
              <nav className="space-y-1 px-2">
                {items.map((item) => {
                  const Icon = item.icon
                  return (
                    <button
                      key={item.id}
                      onClick={() => setActiveSection(item.id)}
                      className={`w-full flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-colors ${
                        activeSection === item.id
                          ? "bg-blue-50 text-blue-700 border-r-2 border-blue-600"
                          : "text-gray-700 hover:bg-gray-50"
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      <span className="flex-1 text-left">{item.label}</span>
                      {item.badge && (
                        <Badge variant="secondary" className="text-xs">
                          {item.badge}
                        </Badge>
                      )}
                    </button>
                  )
                })}
              </nav>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h1 className="text-xl font-semibold text-gray-900">Narrative Performance</h1>
            </div>
            <div className="flex items-center gap-3">
              <Select defaultValue="14days">
                <SelectTrigger className="w-32">
                  <Calendar className="w-4 h-4 mr-2" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7days">Last 7 days</SelectItem>
                  <SelectItem value="14days">Last 14 days</SelectItem>
                  <SelectItem value="30days">Last 30 days</SelectItem>
                </SelectContent>
              </Select>
              <Select defaultValue="all-models">
                <SelectTrigger className="w-36">
                  <Filter className="w-4 h-4 mr-2" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all-models">All Models</SelectItem>
                  <SelectItem value="gpt-4">GPT-4</SelectItem>
                  <SelectItem value="claude">Claude</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="outline" size="sm">
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </Button>
            </div>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeSection === "dashboard" && (
            <div className="space-y-6">
              {/* Input Section */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Facts */}
                <Card>
                  <CardHeader className="pb-4">
                    <CardTitle className="text-lg font-medium">📝 Narrative Points</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {facts.map((fact, index) => (
                      <div key={fact.id} className="flex items-center gap-2">
                        <Input
                          placeholder={`Narrative Point ${index + 1}`}
                          value={fact.text}
                          onChange={(e) => updateFact(fact.id, e.target.value)}
                          className="flex-1"
                        />
                        {facts.length > 1 && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeFact(fact.id)}
                            className="text-gray-400 hover:text-red-600"
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    ))}
                    <Button onClick={addFact} variant="outline" size="sm" className="w-full bg-transparent">
                      <Plus className="w-4 h-4 mr-2" />
                      Add Narrative Point
                    </Button>
                  </CardContent>
                </Card>

                {/* Prompts */}
                <Card>
                  <CardHeader className="pb-4">
                    <CardTitle className="text-lg font-medium">💬 Prompts</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {prompts.map((prompt, index) => (
                      <div key={prompt.id} className="flex items-center gap-2">
                        <Input
                          placeholder={`Prompt ${index + 1}`}
                          value={prompt.text}
                          onChange={(e) => updatePrompt(prompt.id, e.target.value)}
                          className="flex-1"
                        />
                        {prompts.length > 1 && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removePrompt(prompt.id)}
                            className="text-gray-400 hover:text-red-600"
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    ))}
                    <Button onClick={addPrompt} variant="outline" size="sm" className="w-full bg-transparent">
                      <Plus className="w-4 h-4 mr-2" />
                      Add Prompt
                    </Button>
                  </CardContent>
                </Card>
              </div>

              {/* Submit Button */}
              <div className="flex justify-center">
                <Button onClick={handleSubmitAll} className="px-8" disabled={isLoading}>
                  {isLoading ? "Running Evaluation..." : "Run Evaluation"}
                </Button>
              </div>

              {/* Results Section */}
              {isSubmitted && results.length > 0 && (
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between">
                    <CardTitle className="text-lg font-medium">Evaluation Results</CardTitle>
                    <Button variant="outline" size="sm">
                      <Download className="w-4 h-4 mr-2" />
                      Download
                    </Button>
                  </CardHeader>
                  <CardContent>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Narrative Point</TableHead>
                          <TableHead>Mention Rate</TableHead>
                          <TableHead>Created</TableHead>
                          <TableHead>Used On</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {results.map((result, index) => (
                          <TableRow key={index}>
                            <TableCell className="font-medium max-w-md">
                              <div className="truncate" title={result.factText}>
                                {result.factText || `Narrative Point ${result.factIndex + 1}`}
                              </div>
                            </TableCell>
                            <TableCell>
                              <div className="flex items-center gap-2">
                                <div className="w-16 bg-gray-200 rounded-full h-2">
                                  <div
                                    className="bg-blue-600 h-2 rounded-full"
                                    style={{ width: `${result.mentionRate}%` }}
                                  />
                                </div>
                                <span className="text-sm font-medium">{result.mentionRate}%</span>
                              </div>
                            </TableCell>
                            <TableCell className="text-sm text-gray-500">{result.timestamp}</TableCell>
                            <TableCell className="text-sm text-gray-500">
                              {prompts.filter((p) => p.text.trim()).length} prompt
                              {prompts.filter((p) => p.text.trim()).length !== 1 ? "s" : ""}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>
              )}

              {/* Prompt-to-Facts Mapping Visualization */}
              {isSubmitted && detailedResults && (
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Target className="w-5 h-5 text-blue-600" />
                      <CardTitle className="text-lg font-medium">Prompt-to-Narrative Points Mapping</CardTitle>
                    </div>
                    <Button variant="outline" size="sm">
                      <TrendingUp className="w-4 h-4 mr-2" />
                      View Analytics
                    </Button>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {detailedResults.fact_ids_per_context.map((factIds, promptIndex) => {
                        const promptText = prompts[promptIndex]?.text || `Prompt ${promptIndex + 1}`
                        const mentionedFacts = factIds.map((factId) => ({
                          id: factId,
                          text: facts[factId]?.text || `Narrative Point ${factId + 1}`,
                        }))

                        return (
                          <div
                            key={promptIndex}
                            className="border rounded-lg p-4 bg-gradient-to-r from-blue-50 to-indigo-50"
                          >
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex-1">
                                <h4 className="font-medium text-gray-900 mb-1">
                                  <span className="text-blue-600">#{promptIndex + 1}</span> {promptText}
                                </h4>
                                <div className="text-sm text-gray-600">
                                  {mentionedFacts.length > 0 ? (
                                    <span className="text-green-700 font-medium">
                                      ✓ {mentionedFacts.length} narrative point{mentionedFacts.length !== 1 ? "s" : ""}{" "}
                                      mentioned
                                    </span>
                                  ) : (
                                    <span className="text-orange-600 font-medium">⚠ No narrative points mentioned</span>
                                  )}
                                </div>
                              </div>
                            </div>

                            {/* Facts Grid */}
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                              {facts.map((fact, factIndex) => {
                                const isMentioned = factIds.includes(factIndex)
                                return (
                                  <div
                                    key={factIndex}
                                    className={`p-3 rounded-lg border-2 transition-all ${
                                      isMentioned
                                        ? "bg-green-100 border-green-300 shadow-sm"
                                        : "bg-gray-50 border-gray-200 opacity-60"
                                    }`}
                                  >
                                    <div className="flex items-center gap-2">
                                      <div
                                        className={`w-3 h-3 rounded-full ${
                                          isMentioned ? "bg-green-500" : "bg-gray-300"
                                        }`}
                                      />
                                      <span className="text-xs font-medium text-gray-600">
                                        Narrative Point {factIndex + 1}
                                      </span>
                                    </div>
                                    <p
                                      className={`text-sm mt-1 ${
                                        isMentioned ? "text-gray-900 font-medium" : "text-gray-500"
                                      }`}
                                    >
                                      {fact.text || `Narrative Point ${factIndex + 1}`}
                                    </p>
                                  </div>
                                )
                              })}
                            </div>

                            {/* Summary Stats */}
                            <div className="mt-3 pt-3 border-t border-gray-200">
                              <div className="flex items-center justify-between text-xs text-gray-600">
                                <span>
                                  Coverage: {mentionedFacts.length}/{facts.length} narrative points (
                                  {Math.round((mentionedFacts.length / facts.length) * 100)}%)
                                </span>
                                <div className="flex items-center gap-4">
                                  <span className="flex items-center gap-1">
                                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                    Mentioned
                                  </span>
                                  <span className="flex items-center gap-1">
                                    <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
                                    Not Mentioned
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                        )
                      })}
                    </div>

                    {/* Overall Summary */}
                    <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                      <h5 className="font-medium text-blue-900 mb-2">📊 Overall Summary</h5>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-blue-600">
                            {detailedResults.fact_ids_per_context.length}
                          </div>
                          <div className="text-gray-600">Total Prompts</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-600">
                            {detailedResults.fact_ids_per_context.filter((factIds) => factIds.length > 0).length}
                          </div>
                          <div className="text-gray-600">Prompts with Narrative Points</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-orange-600">
                            {Math.round(
                              (detailedResults.fact_ids_per_context.reduce((sum, factIds) => sum + factIds.length, 0) /
                                (detailedResults.fact_ids_per_context.length * facts.length)) *
                                100,
                            )}
                            %
                          </div>
                          <div className="text-gray-600">Avg Coverage</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-purple-600">
                            {detailedResults.fact_ids_per_context.reduce((sum, factIds) => sum + factIds.length, 0)}
                          </div>
                          <div className="text-gray-600">Total Mentions</div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Detailed Evaluation Results */}
              {isSubmitted && detailedResults && (
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between">
                    <CardTitle className="text-lg font-medium">Detailed Evaluation Analysis</CardTitle>
                    <Button variant="outline" size="sm">
                      <Download className="w-4 h-4 mr-2" />
                      Export Details
                    </Button>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {detailedResults.responses.map((response, index) => {
                      const promptText = prompts[index]?.text || `Prompt ${index + 1}`
                      const factsUsed = getFactsForPrompt(index)
                      const isExpanded = expandedPrompts.has(index)
                      const isHighlighting = highlightingPrompts.has(index)
                      const hasHighlights = highlights.has(index)
                      const originalAnswer = detailedResults.original_answers?.[index] || response

                      return (
                        <div key={index} className="border rounded-lg">
                          <Collapsible>
                            <CollapsibleTrigger asChild>
                              <div
                                className="flex items-center justify-between p-4 hover:bg-gray-50 cursor-pointer"
                                onClick={() => togglePromptExpansion(index)}
                              >
                                <div className="flex-1">
                                  <div className="flex items-center gap-2">
                                    {isExpanded ? (
                                      <ChevronDown className="w-4 h-4 text-gray-500" />
                                    ) : (
                                      <ChevronRight className="w-4 h-4 text-gray-500" />
                                    )}
                                    <h4 className="font-medium text-gray-900">{promptText}</h4>
                                  </div>
                                  <div className="mt-2 flex flex-wrap gap-1">
                                    {factsUsed.length > 0 ? (
                                      factsUsed.map((fact, factIndex) => (
                                        <Badge key={factIndex} variant="secondary" className="text-xs">
                                          {fact}
                                        </Badge>
                                      ))
                                    ) : (
                                      <Badge variant="outline" className="text-xs">
                                        No narrative points mentioned
                                      </Badge>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </CollapsibleTrigger>
                            <CollapsibleContent>
                              <div className="px-4 pb-4 border-t bg-gray-50">
                                {/* Original Extended Answer */}
                                <div className="mt-4">
                                  <div className="flex items-center justify-between mb-2">
                                    <h5 className="font-medium text-sm text-gray-700">Original Extended Answer:</h5>
                                    <div className="flex gap-2">
                                      <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => {
                                          const textToHighlight = detailedResults.original_answers?.[index] || response
                                          highlightFactsInResponse(
                                            textToHighlight,
                                            facts.map((f) => f.text).filter(Boolean),
                                            index,
                                          )
                                        }}
                                        disabled={isHighlighting}
                                        className="text-xs"
                                      >
                                        {isHighlighting ? (
                                          <>
                                            <Sparkles className="w-3 h-3 mr-1 animate-spin" />
                                            Highlighting...
                                          </>
                                        ) : hasHighlights ? (
                                          <>
                                            <Sparkles className="w-3 h-3 mr-1" />
                                            Re-highlight Narrative Points
                                          </>
                                        ) : (
                                          <>
                                            <Sparkles className="w-3 h-3 mr-1" />
                                            Highlight Narrative Points
                                          </>
                                        )}
                                      </Button>
                                      <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => {
                                          const mockHighlight = {
                                            highlights: [
                                              {
                                                factIndex: 0,
                                                factText: facts[0]?.text || "Test fact",
                                                mentions: [
                                                  {
                                                    text: "BMW",
                                                    startIndex: originalAnswer.indexOf("BMW"),
                                                    endIndex: originalAnswer.indexOf("BMW") + 3,
                                                    confidence: 0.9,
                                                    type: "direct",
                                                  },
                                                ],
                                              },
                                            ],
                                          }
                                          setHighlights((prev) => new Map([...prev, [index, mockHighlight]]))
                                        }}
                                        className="text-xs"
                                      >
                                        Test Highlight
                                      </Button>
                                    </div>
                                  </div>
                                  <div className="text-sm text-gray-600 bg-white p-4 rounded border max-h-96 overflow-y-auto leading-relaxed">
                                    {renderHighlightedText(originalAnswer, index)}
                                  </div>
                                  {hasHighlights && (
                                    <div className="mt-2 text-xs text-gray-500">
                                      <div className="flex flex-wrap gap-2">
                                        <span className="bg-red-200 border border-red-400 rounded px-1 font-medium">
                                          🎯 Exact Narrative Point Mentions
                                        </span>
                                        <span className="text-gray-400">
                                          • Red highlights show where narrative points were detected
                                        </span>
                                      </div>
                                    </div>
                                  )}
                                </div>

                                {/* Processed Response (if different) */}
                                {originalAnswer !== response && (
                                  <div className="mt-6 pt-4 border-t">
                                    <h5 className="font-medium text-sm text-gray-700 mb-2">Processed Response:</h5>
                                    <div className="text-sm text-gray-600 bg-gray-100 p-3 rounded border max-h-48 overflow-y-auto leading-relaxed">
                                      {response}
                                    </div>
                                  </div>
                                )}
                              </div>
                            </CollapsibleContent>
                          </Collapsible>
                        </div>
                      )
                    })}
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {activeSection === "prompts" && (
            <Card>
              <CardHeader>
                <CardTitle>Prompt Management</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">Manage your evaluation prompts here.</p>
              </CardContent>
            </Card>
          )}

          {activeSection === "sources" && (
            <Card>
              <CardHeader>
                <CardTitle>Data Sources</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">Configure your data sources and integrations.</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
