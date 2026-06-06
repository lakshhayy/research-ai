import { QueryInput } from "@/components/QueryInput"
import { useResearchSSE } from "@/hooks/useResearchSSE"
import { ReportViewer } from "@/components/report/ReportViewer"
import { GraphVisualizer } from "@/components/graph/GraphVisualizer"

function App() {
  const { status, logs, finalReport, confidenceScore, startResearch } = useResearchSSE()

  const handleSearch = (query: string) => {
    startResearch(query)
  }

  return (
    <div className="min-h-screen flex flex-col items-center p-8 relative overflow-hidden pt-32">
      {/* Decorative background elements */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent/20 rounded-full blur-[120px] pointer-events-none" />
      
      <div className="text-center relative z-10 mb-12">
        <h1 className="text-6xl font-bold mb-4 tracking-tight bg-gradient-to-br from-white via-white/90 to-white/40 bg-clip-text text-transparent">
          ResearchPilot
        </h1>
        <p className="text-xl text-muted-foreground max-w-xl mx-auto">
          An autonomous AI agent that deeply researches, critiques, and synthesizes full reports.
        </p>
      </div>

      <div className="w-full relative z-10 transition-all duration-700 ease-in-out">
        <div className={`transition-all duration-700 ${status === "complete" ? "-translate-y-8 opacity-90 scale-95" : ""}`}>
          <QueryInput onSubmit={handleSearch} disabled={status === "running" || status === "connecting"} />
        </div>
        
        {/* Graph Visualizer replaces the basic terminal logs */}
        {status !== "idle" && (
          <GraphVisualizer logs={logs} status={status} />
        )}

        {/* Live Streaming Logs (Smaller view below the graph) */}
        {status !== "idle" && status !== "complete" && (
          <div className="mt-8 p-4 glass rounded-xl text-left max-w-2xl mx-auto font-mono text-xs opacity-70 animate-in fade-in duration-500">
            <ul className="space-y-1 h-24 overflow-y-auto flex flex-col justify-end">
              {logs.map((log) => (
                <li key={log.id} className="text-muted-foreground animate-in fade-in slide-in-from-left-2">
                  <span className="text-accent font-semibold">[{log.node}]</span> {log.message}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Final Report */}
        {status === "complete" && finalReport && confidenceScore !== null && (
          <ReportViewer report={finalReport} confidenceScore={confidenceScore} />
        )}
      </div>
    </div>
  )
}

export default App
