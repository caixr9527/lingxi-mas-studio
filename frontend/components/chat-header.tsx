"use client"

import Link from "next/link"
import { SidebarTrigger, useSidebar } from "./ui/sidebar"
import { Configs } from "./configs"

export function ChatHeader() {
  const { open, isMobile } = useSidebar()
  return (
    <header className="flex justify-between items-center w-full py-2 px-4">
      {/* 左侧操作&logo */}
      <div className="flex items-center gap-2">
        {/* 面板操作按钮 */}
        {(!open || isMobile) && <SidebarTrigger className="cursor-pointer" />}
        {/* logo */}
        <Link href="/" className="block bg-white w-[80px] h-9 rounded-md" />
      </div>
      {/* 设置模态窗 */}
      <Configs />
    </header>
  )
}
