import { useState, useCallback } from "react"

export type LogEntry = {
  id: string
  node: string
  message: string
  timestamp: Date
}

export type ResearchStatus = "idle" | "connecting" | "running" | "complete" | "error"

export function useResearchSSE() {
  const [status, setStatus] = useState<ResearchStatus>("idle")
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [finalReport, setFinalReport] = useState<string | null>(null)
  const [confidenceScore, setConfidenceScore] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  const startResearch = useCallback(async (query: string) => {
    // Reset state
    setStatus("connecting")
    setLogs([])
    setFinalReport(null)
    setConfidenceScore(null)
    setError(null)

    try {
      const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000"
      const response = await fetch(`${API_BASE}/api/research`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query, search_depth: "basic" }),
      })

      if (!response.ok || !response.body) {
        throw new Error(`Failed to start research: ${response.statusText}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder("utf-8")
      let done = false

      setStatus("running")

      // Read the stream chunk by chunk
      while (!done) {
        const { value, done: readerDone } = await reader.read()
        done = readerDone
        if (value) {
          const chunk = decoder.decode(value, { stream: true })
          // SSE format is data: {...}\n\n
          const lines = chunk.split("\n")
          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const data = JSON.parse(line.replace("data: ", ""))
                
                if (data.type === "connected") {
                  console.log(`[SSE] Connected to session: ${data.session_id}`)
                } 
                else if (data.type === "update") {
                  setLogs((prev) => [...prev, {
                    id: crypto.randomUUID(),
                    node: data.node,
                    message: data.message,
                    timestamp: new Date()
                  }])
                } 
                else if (data.type === "complete") {
                  setFinalReport(data.report)
                  setConfidenceScore(data.confidence_score)
                  setStatus("complete")
                } 
                else if (data.type === "error") {
                  setError(data.message)
                  setStatus("error")
                }
              } catch (e) {
                console.error("Failed to parse SSE JSON:", line, e)
              }
            }
          }
        }
      }
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.")
      setStatus("error")
    }
  }, [])

  return { status, logs, finalReport, confidenceScore, error, startResearch }
}
