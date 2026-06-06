import ReactMarkdown from "react-markdown"
import { ShieldCheck, ShieldAlert, ShieldX } from "lucide-react"

interface ReportViewerProps {
  report: string
  confidenceScore: number
}

export function ReportViewer({ report, confidenceScore }: ReportViewerProps) {
  
  // Determine badge color and icon based on score
  let ScoreIcon = ShieldX
  let scoreColor = "text-destructive"
  let scoreBg = "bg-destructive/10 border-destructive/20"
  
  if (confidenceScore >= 0.8) {
    ScoreIcon = ShieldCheck
    scoreColor = "text-emerald-400"
    scoreBg = "bg-emerald-400/10 border-emerald-400/20"
  } else if (confidenceScore >= 0.5) {
    ScoreIcon = ShieldAlert
    scoreColor = "text-amber-400"
    scoreBg = "bg-amber-400/10 border-amber-400/20"
  }

  return (
    <div className="w-full max-w-4xl mx-auto mt-12 animate-in slide-in-from-bottom-8 duration-1000 pb-20">
      
      {/* Meta Header */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">
          Research Findings
        </h2>
        
        <div className={`flex items-center gap-2 px-4 py-1.5 rounded-full border ${scoreBg} ${scoreColor}`}>
          <ScoreIcon className="w-4 h-4" />
          <span className="text-sm font-medium">
            Confidence Score: {(confidenceScore * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* The Markdown Report Container */}
      <div className="glass p-8 md:p-12 rounded-3xl text-left relative overflow-hidden">
        {/* Decorative corner glow */}
        <div className="absolute -top-24 -right-24 w-48 h-48 bg-primary/20 rounded-full blur-[80px]" />
        
        {/* Tailwind Typography Plugin handles the markdown styling via prose classes */}
        <div className="prose prose-invert prose-lg max-w-none prose-headings:font-bold prose-h1:text-4xl prose-h2:text-3xl prose-h3:text-2xl prose-a:text-primary hover:prose-a:text-primary/80 prose-li:marker:text-primary/50 relative z-10">
          <ReactMarkdown>
            {report}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  )
}
