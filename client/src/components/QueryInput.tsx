import { useState } from "react"
import { Send, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"

const EXAMPLE_QUERIES = [
  "What are the best backend frameworks in 2025 and why?",
  "Compare Rust vs Go for systems programming in 2025",
  "What is the current state of LLM agent frameworks?",
  "What are the top open source projects gaining traction this year?"
]

interface QueryInputProps {
  onSubmit: (query: string) => void
  disabled?: boolean
}

export function QueryInput({ onSubmit, disabled = false }: QueryInputProps) {
  const [query, setQuery] = useState("")
  const MAX_CHARS = 500

  const handleSubmit = () => {
    if (query.trim() && query.length <= MAX_CHARS) {
      onSubmit(query.trim())
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="w-full max-w-3xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="glass p-2 rounded-3xl relative group transition-all duration-300 focus-within:ring-2 focus-within:ring-primary/50 focus-within:shadow-[0_0_30px_rgba(139,92,246,0.2)]">
        <Textarea
          placeholder="What do you want to research today?"
          value={query}
          onChange={(e) => setQuery(e.target.value.slice(0, MAX_CHARS))}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          className="min-h-[120px] resize-none border-0 bg-transparent text-lg focus-visible:ring-0 placeholder:text-muted-foreground/50 p-6"
        />
        
        <div className="absolute bottom-4 right-4 flex items-center gap-4">
          <span className={`text-sm ${query.length >= MAX_CHARS ? "text-destructive" : "text-muted-foreground"}`}>
            {query.length} / {MAX_CHARS}
          </span>
          <Button 
            onClick={handleSubmit} 
            disabled={disabled || !query.trim()}
            size="icon"
            className="rounded-full bg-primary hover:bg-primary/90 text-primary-foreground h-12 w-12 shadow-[0_0_15px_rgba(139,92,246,0.5)] transition-transform hover:scale-105 active:scale-95"
          >
            <Send className="w-5 h-5 ml-1" />
          </Button>
        </div>
      </div>

      <div className="flex flex-col items-center gap-3">
        <div className="flex items-center gap-2 text-sm text-muted-foreground font-medium">
          <Sparkles className="w-4 h-4 text-accent" />
          <span>Try an example</span>
        </div>
        <div className="flex flex-wrap justify-center gap-2">
          {EXAMPLE_QUERIES.map((example) => (
            <Badge 
              key={example}
              variant="secondary" 
              className="cursor-pointer hover:bg-primary/20 hover:text-primary transition-colors py-1.5 px-4 rounded-full text-sm font-normal border border-white/5"
              onClick={() => {
                setQuery(example)
                // Optional: Automatically submit when clicking an example
                // onSubmit(example)
              }}
            >
              {example}
            </Badge>
          ))}
        </div>
      </div>
    </div>
  )
}
