"use client"

import { FileSearchCorner } from "lucide-react"
import { Button } from "./ui/button"
import { SidebarTrigger, useSidebar } from "./ui/sidebar"

export function SessionHeader() {
  const { open, isMobile } = useSidebar()
  return (
    <header className="bg-[#f8f8f7] sm:min-w-[390px] flex flex-row items-center justify-between pt-3 pb-2 gap-1 sticky top-0 z-10 flex-shrink-0">
      {/* 左侧操作按钮 */}
      <div className="flex items-center flex-1">
        <div className="relative flex items-center">
          {(!open || isMobile) && <SidebarTrigger className="cursor-pointer" />}
        </div>
      </div>
      {/* 中间会话标题区 */}
      <div className="max-w-full sm:max-w-[768px] sm:min-w-[390px] flex w-full items-center justify-between gap-1 overflow-hidden">
        {/* 左侧标题 */}
        <div className="text-gray-700 text-lg whitespace-nowrap text-ellipsis overflow-hidden">
          编写Python冒泡排序算法
        </div>
        {/* 右侧按钮 */}
        <Button variant="ghost" size="icon-sm" className="cursor-pointer">
          <FileSearchCorner />
        </Button>
      </div>
      {/* 右侧按钮 */}
    </header>
  )
}
