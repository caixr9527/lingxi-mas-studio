"use client"

import { cn } from "@/lib/utils"
import { Languages } from "lucide-react"
import { AIIcon } from "./ai-icon"
import { ToolUse } from "./tool-use"

interface ChatMessageProps {
  className?: string
  message: {
    type: string
    role?: string
  }
}

export function ChatMessage({ className, message }: ChatMessageProps) {
  if (message.type === "user") {
    return (
      <div
        className={cn(
          "flex w-full flex-col items-end justify-end gap-1 group mt-3",
          className,
        )}
      >
        {/* 顶部时间 */}
        <div className="flex items-end">
          <div className="flex items-center justify-end gap-1 invisible group-hover:visible">
            <div className="float-right transition text-xs text-gray-500 invisible group-hover:visible">
              2个月前
            </div>
          </div>
        </div>
        {/* 底部用户消息 */}
        <div className="flex max-w-[90%] relative flex-col gap-2 items-end">
          <div className="text-gray-700 relative flex items-center rounded-lg overflow-hidden bg-white p-3 border">
            帮我写一个Python版本的冒泡排序
          </div>
        </div>
      </div>
    )
  } else if (message.type === "assistant") {
    return (
      <div className={cn("flex flex-col gap-2 w-full group mt-3", className)}>
        {/* AI图标&时间 */}
        <div className="flex items-center justify-between h-7 group">
          <div className="flex items-center justify-center gap-1 text-gray-700">
            {/* <Languages size={18} /> */}
            <AIIcon />
          </div>
          <div className="flex items-center gap-[3px] invisible group-hover:visible">
            <div className="float-right transition text-xs text-gray-500 invisible group-hover:visible">
              2个月前
            </div>
          </div>
        </div>
        {/* AI消息 */}
        <div className="max-w-none p-0 m-0 text-gray-700">
          用户请求编写一个Python版本的冒泡排序算法。冒泡排序是一种简单的排序算法，通过重复遍历列表，比较相邻元素并交换它们的位置，直到列表完全排序。我将创建一个Python脚本来实现这个算法，包括必要的注释和示例使用。这个任务需要编写代码并保存到文件中，以便后续执行或修改。
        </div>
      </div>
    )
  } else if (message.type === "tool") {
    return <ToolUse />
  } else if (message.type === "step") {
    return <div>步骤消息</div>
  } else if (message.type === "attachments") {
    return <div>附件消息</div>
  }
}
