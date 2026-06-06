import { motion } from "framer-motion"
import { BrainCircuit, Search, Scale, FileText, CheckCircle2 } from "lucide-react"

interface GraphVisualizerProps {
  logs: { id: string; node: string; message: string }[]
  status: string
}

type NodeName = "planner" | "researcher" | "critic" | "synthesizer" | "grader" | "idle"

export function GraphVisualizer({ logs, status }: GraphVisualizerProps) {
  // Determine the active node based on the most recent log
  const activeNode: NodeName = logs.length > 0 
    ? (logs[logs.length - 1].node as NodeName) 
    : status === "complete" ? "grader" : "idle"

  const nodes = [
    { id: "planner", label: "Planner", icon: BrainCircuit, color: "text-blue-400", bg: "bg-blue-400/20", border: "border-blue-400/30", shadow: "shadow-[0_0_15px_rgba(96,165,250,0.5)]" },
    { id: "researcher", label: "Researchers", icon: Search, color: "text-purple-400", bg: "bg-purple-400/20", border: "border-purple-400/30", shadow: "shadow-[0_0_15px_rgba(192,132,252,0.5)]" },
    { id: "critic", label: "Critic", icon: Scale, color: "text-amber-400", bg: "bg-amber-400/20", border: "border-amber-400/30", shadow: "shadow-[0_0_15px_rgba(251,191,36,0.5)]" },
    { id: "synthesizer", label: "Synthesizer", icon: FileText, color: "text-emerald-400", bg: "bg-emerald-400/20", border: "border-emerald-400/30", shadow: "shadow-[0_0_15px_rgba(52,211,153,0.5)]" },
    { id: "grader", label: "Grader", icon: CheckCircle2, color: "text-cyan-400", bg: "bg-cyan-400/20", border: "border-cyan-400/30", shadow: "shadow-[0_0_15px_rgba(34,211,238,0.5)]" },
  ]

  // Count retries by counting how many times planner was called after the first time
  const plannerCount = logs.filter((log) => log.node === "planner").length
  const retryCount = Math.max(0, plannerCount - 1)

  return (
    <div className="w-full max-w-4xl mx-auto my-12 animate-in fade-in slide-in-from-bottom-8 duration-700">
      
      {/* Title & Retry Counter */}
      <div className="flex justify-between items-center mb-8 px-4">
        <h3 className="text-xl font-medium text-white/80">LangGraph Pipeline</h3>
        {retryCount > 0 && (
          <div className="flex items-center gap-2 px-3 py-1 bg-amber-500/10 border border-amber-500/20 rounded-full text-amber-400 text-sm font-medium animate-pulse">
            <Scale className="w-4 h-4" />
            <span>Critic Retry Loop: {retryCount}</span>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between relative px-6">
        
        {/* Background Connecting Line */}
        <div className="absolute top-1/2 left-10 right-10 h-1 bg-white/5 -translate-y-1/2 z-0 rounded-full" />
        
        {nodes.map((node, index) => {
          const isActive = activeNode === node.id || (status === "complete" && index <= nodes.findIndex(n => n.id === "grader"))
          const isPast = status === "complete" || (logs.findIndex(l => l.node === activeNode) > -1 && index < nodes.findIndex(n => n.id === activeNode))
          
          return (
            <div key={node.id} className="relative z-10 flex flex-col items-center gap-4">
              <motion.div
                animate={{
                  scale: isActive ? 1.15 : 1,
                  opacity: isActive || isPast ? 1 : 0.4,
                }}
                transition={{ duration: 0.3 }}
                className={`w-16 h-16 rounded-2xl flex items-center justify-center backdrop-blur-md border ${
                  isActive ? `${node.bg} ${node.border} ${node.shadow}` : isPast ? "bg-white/10 border-white/20" : "bg-black/40 border-white/5"
                } transition-all duration-500`}
              >
                <node.icon className={`w-8 h-8 ${isActive ? node.color : isPast ? "text-white/60" : "text-white/30"}`} />
                
                {/* Ping animation if currently active */}
                {isActive && status !== "complete" && (
                  <span className={`absolute flex h-full w-full -z-10 rounded-2xl opacity-50 ${node.bg}`}>
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-2xl opacity-75"></span>
                  </span>
                )}
              </motion.div>
              
              <motion.span 
                animate={{ opacity: isActive || isPast ? 1 : 0.4 }}
                className={`text-sm font-medium tracking-wide ${isActive ? node.color : "text-muted-foreground"}`}
              >
                {node.label}
              </motion.span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
