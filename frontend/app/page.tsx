"use client"
import { ChatHeader } from "@/components/chat-header"
import { ChatInput } from "@/components/chat-input"
import { SuggestedQuestions } from "@/components/suggested-questions"

export default function Page() {
  return (
    <div className="h-full flex flex-col">
      {/* 顶部header */}
      <ChatHeader />
      {/* 中间对话框 */}
      <div className="relative w-full max-w-full sm:max-w-[768px] sm:min-w-[390px] px-4 mx-auto mt-[20vh]">
        {/* 会话提示内容*/}
        <div className="flex-1 text-[32px] font-bold mb-4">
          <div className="text-gray-700">欢迎使用灵析 AI助手</div>
          <div className="text-gray-700">我能为您做什么?</div>
        </div>
        {/* 对话框 */}
        <ChatInput className="mb-4" />
        {/* 推荐对话内容 */}
        <SuggestedQuestions />
      </div>
    </div>
  )
}
