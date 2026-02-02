import { SidebarProvider } from "@/components/ui/sidebar"
import { LeftPanel } from "@/components/left-panel"
import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "灵析 - AI助手",
  description:
    "灵析 - AI助手 是一个行动引擎，它超越了答案的范畴，可以执行任务、自动化工作流程，并扩展您的能力。",
  icons: {
    icon: "/icon.png",
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="zh-CN">
      <body>
        <SidebarProvider
          style={{
            "--sidebar-width": "300px",
            "--sidebar-width-icon": "300px",
          }}
        >
          {/*左侧 */}
          <LeftPanel />
          {/*右侧 */}
          {children}
        </SidebarProvider>
      </body>
    </html>
  )
}
