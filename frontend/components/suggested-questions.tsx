"use client"

import { cn } from "@/lib/utils"
import { Button } from "./ui/button"

interface SuggestedQuestionsProps {
  className?: string
}
export function SuggestedQuestions({ className }: SuggestedQuestionsProps) {
  return (
    <div className={cn("flex flex-wrap gap-2", className)}>
      {/* 推荐问题项 */}
      <Button variant="outline" className="cursor-pointer">
        推荐问题1
      </Button>
      <Button variant="outline" className="cursor-pointer">
        推荐问题2
      </Button>
      <Button variant="outline" className="cursor-pointer">
        推荐问题3
      </Button>
    </div>
  )
}
