import { ChatInput } from "@/components/chat-input"
import { ChatMessage } from "@/components/chat-message"
import { PlanPanel } from "@/components/plan-panel"
import { SessionHeader } from "@/components/session-header"

interface PageProps {
  params: Promise<{ id: string }>
}

export default async function Page({ params }: PageProps) {
  const { id } = await params
  const messages = [
    { id: 1, type: "user" },
    { id: 2, type: "attachments", role: "user" },
    { id: 3, type: "assistant" },
    { id: 4, type: "tool" },
    { id: 5, type: "step" },
    { id: 6, type: "assistant" },
    { id: 7, type: "attachments", role: "assistant" },
  ]
  return (
    <div className="relative flex flex-col h-full flex-1 min-w-0 px-4">
      {/* 顶部标题&操作按钮 */}
      <SessionHeader />
      {/* 中间内容&底部输入框 */}
      <div className="mx-auto w-full max-full sm:max-w-[768px] sm:min-w-[390px] flex flex-col flex-1">
        <div className="flex flex-col w-full gap-3 pb-[40px] pt-3 flex-1">
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
        </div>
        {/* 输入框&任务列表 */}
        <div className="sticky bottom-0 mt-auto">
          {/* 规划列表 */}
          <PlanPanel className="mb-2" />
          {/* 输入框 */}
          <ChatInput className="mb-4" />
        </div>
      </div>
    </div>
  )
}
