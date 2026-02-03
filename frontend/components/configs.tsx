"use client"

import {
  Gift,
  Languages,
  LayoutGrid,
  LayoutList,
  Settings,
  Trash,
  Wrench,
} from "lucide-react"
import { Button } from "./ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog"
import { useState } from "react"
import { Separator } from "./ui/separator"
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
  FieldLegend,
  FieldSet,
} from "./ui/field"
import { Kbd } from "./ui/kbd"
import { Input } from "./ui/input"
import {
  Item,
  ItemContent,
  ItemDescription,
  ItemGroup,
  ItemTitle,
} from "./ui/item"
import { Badge } from "./ui/badge"
import { Switch } from "./ui/switch"
import { Textarea } from "./ui/textarea"

export function CommonSetting() {
  return (
    <form className="w-full px-1">
      <FieldGroup>
        <FieldSet>
          {/* 顶部表单标题 */}
          <FieldLegend className="text-lg font-bold text-gray-700">
            通用设置
          </FieldLegend>
          <FieldDescription className="text-sm">
            配置通用设置信息。
          </FieldDescription>
          {/* 表单内容区域 */}
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="max_iterations">
                最大迭代次数
                <Kbd>max_iterations</Kbd>
              </FieldLabel>
              <Input
                id="max_iterations"
                type="number"
                placeholder="Agent最大迭代次数"
                defaultValue={100}
                min={0}
                max={200}
                required
              />
              <FieldDescription className="text-xs">
                设置Agent在执行任务时允许的最大迭代次数。默认100次。
              </FieldDescription>
            </Field>
            <Field>
              <FieldLabel htmlFor="max_retries">
                最大重试次数
                <Kbd>max_retries</Kbd>
              </FieldLabel>
              <Input
                id="max_retries"
                type="number"
                placeholder="LLM/Tool最大重试次数"
                defaultValue={3}
                min={0}
                max={10}
                required
              />
              <FieldDescription className="text-xs">
                默认情况下，最大重试次数为3。
              </FieldDescription>
            </Field>
            <Field>
              <FieldLabel htmlFor="max_search_results">
                最大搜索结果
                <Kbd>max_search_results</Kbd>
              </FieldLabel>
              <Input
                id="max_search_results"
                type="number"
                placeholder="搜索工具返回的最大结果数"
                defaultValue={10}
                min={0}
                max={30}
                required
              />
              <FieldDescription className="text-xs">
                默认情况下, 每个搜索步骤包含10个结果。
              </FieldDescription>
            </Field>
          </FieldGroup>
        </FieldSet>
      </FieldGroup>
    </form>
  )
}

export function LLMSetting() {
  return (
    <form className="w-full px-1">
      <FieldGroup>
        <FieldSet>
          {/* 顶部表单标题 */}
          <FieldLegend className="text-lg font-bold text-gray-700">
            模型提供商
          </FieldLegend>
          <FieldDescription className="text-sm">
            配置Agent使用的基础LLM模型(兼容OpenAI格式)。
          </FieldDescription>
          {/* 中间表单内容 */}
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="base_url">
                提供商基础地址
                <Kbd>base_url</Kbd>
              </FieldLabel>
              <Input
                id="base_url"
                type="url"
                placeholder="请填写LLM基础URL地址, 不带/"
                defaultValue="https://api.deepseek.com"
                required
              />
              <FieldDescription className="text-xs">
                请填写模型提供商的基础 url 地址, 需兼容 OpenAI 格式。
              </FieldDescription>
            </Field>
            <Field>
              <FieldLabel htmlFor="api_key">
                提供商秘钥
                <Kbd>api_key</Kbd>
              </FieldLabel>
              <Input
                id="api_key"
                type="text"
                placeholder="请填写提供商API秘钥"
                required
              />
              <FieldDescription className="text-xs">
                请填写模型提供商秘钥信息。
              </FieldDescription>
            </Field>
            <Field>
              <FieldLabel htmlFor="model_name">
                模型名
                <Kbd>model_name</Kbd>
              </FieldLabel>
              <Input
                id="model_name"
                type="text"
                placeholder="请填写需要使用的模型名字"
                required
              />
              <FieldDescription className="text-xs">
                请填写调用的模型名字, 模型必须支持工具调用、图像识别等功能。
              </FieldDescription>
            </Field>
            <Field>
              <FieldLabel htmlFor="temperature">
                温度
                <Kbd>temperature</Kbd>
              </FieldLabel>
              <Input
                id="temperature"
                type="number"
                placeholder="请填写模型温度信息"
                defaultValue={0.7}
                required
              />
              <FieldDescription className="text-xs">
                温度越低, 模型输出内容越确定, 创意性越差, 默认配置0.7。
              </FieldDescription>
            </Field>
            <Field>
              <FieldLabel htmlFor="max_tokens">
                最大输出token数
                <Kbd>max_tokens</Kbd>
              </FieldLabel>
              <Input
                id="max_tokens"
                type="number"
                placeholder="请填写模型最大输出token数"
                defaultValue={8192}
                min={0}
                required
              />
              <FieldDescription className="text-xs">
                设置模型的最大输出token数, 默认8192。
              </FieldDescription>
            </Field>
          </FieldGroup>
        </FieldSet>
      </FieldGroup>
    </form>
  )
}

export function A2ASetting() {
  return (
    <div className="w-full px-1">
      <FieldGroup>
        <FieldSet>
          {/* 顶部标题 */}
          <FieldLegend className="w-full flex justify-between items-center text-lg font-bold text-gray-700">
            A2A Agent配置
            <Dialog>
              {/* 模态窗触发按钮 */}
              <DialogTrigger asChild>
                <Button type="button" size="xs" className="cursor-pointer">
                  新增远程Agent
                </Button>
              </DialogTrigger>
              {/* 新增A2A服务器模态窗 */}
              <DialogContent>
                <DialogHeader>
                  <DialogTitle className="text-gray-700">
                    添加远程Agent
                  </DialogTitle>
                  <DialogDescription className="text-gray-500">
                    使用标准的 A2A 协议来连接远程 Agent。
                    <br />
                    请将您的配置粘贴到下方，然后点击“添加”即可添加 Agent。
                  </DialogDescription>
                </DialogHeader>
                <form className="w-full">
                  <FieldGroup>
                    <FieldSet>
                      <Field>
                        <Input
                          id="base_url"
                          type="url"
                          placeholder="Example: https://manus.com/weather-agent"
                        />
                      </Field>
                    </FieldSet>
                  </FieldGroup>
                </form>
                <DialogFooter>
                  <DialogClose asChild>
                    <Button variant="outline" className="cursor-pointer">
                      取消
                    </Button>
                  </DialogClose>
                  <Button className="cursor-pointer">添加</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </FieldLegend>
          <FieldDescription className="text-sm">
            模型A2A协议 (Agent to Agent Protocol) 通过集成外部 Agent
            来增强性能。
          </FieldDescription>
          {/* 中间列表内容 */}
          <ItemGroup>
            <Item variant="outline">
              <ItemContent>
                <ItemTitle className="w-full flex justify-between items-center text-md font-bold text-gray-700">
                  {/* 左侧Agent名称 */}
                  <div className="flex gap-2 items-center">
                    天气Agent
                    <Badge>禁用</Badge>
                  </div>
                  {/* 右侧基础操作 */}
                  <div className="flex items-center justify-center gap-2">
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon-xs"
                      className="cursor-pointer"
                    >
                      <Trash />
                    </Button>
                    <Switch />
                  </div>
                </ItemTitle>
                <ItemDescription>提供天气查询相关功能</ItemDescription>
                <ItemDescription className="flex flex-wrap items-center gap-x-2 gap-y-1">
                  <LayoutList size={12} />
                  <Badge variant="secondary" className="text-gray-500">
                    输入: text
                  </Badge>
                  <Badge variant="secondary" className="text-gray-500">
                    输出: text
                  </Badge>
                  <Badge variant="secondary" className="text-gray-500">
                    流式输出
                  </Badge>
                  <Badge variant="secondary" className="text-gray-500">
                    推送通知
                  </Badge>
                </ItemDescription>
              </ItemContent>
            </Item>
          </ItemGroup>
        </FieldSet>
      </FieldGroup>
    </div>
  )
}

export function MCPSetting() {
  const mcpConfigPlaceholder = `{
  "mcpServers": {
    "qiniu": {
      "command": "uvx",
      "args": [
        "qiniu-mcp-server"
      ],
      "env": {
        "QINIU_ACCESS_KEY": "YOUR_ACCESS_KEY",
        "QINIU_SECRET_KEY": "YOUR_SECRET_KEY",
        "QINIU_REGION_NAME": "YOUR_REGION_NAME",
        "QINIU_ENDPOINT_URL": "YOUR_ENDPOINT_URL",
        "QINIU_BUCKETS": ""
      },
      "disabled": false
    }
  }
}`

  return (
    <div className="w-full px-1">
      <FieldGroup>
        <FieldSet>
          {/* 顶部标题 */}
          <FieldLegend className="w-full flex justify-between items-center text-lg font-bold text-gray-700">
            MCP 服务器
            <Dialog>
              {/* 模态窗触发按钮 */}
              <DialogTrigger asChild>
                <Button type="button" size="xs" className="cursor-pointer">
                  新增服务器
                </Button>
              </DialogTrigger>
              {/* 新增MCP服务器模态窗 */}
              <DialogContent>
                <DialogHeader>
                  <DialogTitle className="text-gray-700">
                    添加新的 MCP 服务器
                  </DialogTitle>
                  <DialogDescription className="text-gray-500">
                    使用标准的 JSON MCP 配置来创建新服务器。
                    请将您的配置粘贴到下方，然后点击“添加”即可添加新服务器。
                  </DialogDescription>
                </DialogHeader>
                <form className="w-full">
                  <FieldGroup>
                    <FieldSet>
                      <Field>
                        <Textarea
                          id="mcp_config"
                          placeholder={mcpConfigPlaceholder}
                          required
                        />
                      </Field>
                    </FieldSet>
                  </FieldGroup>
                </form>
                <DialogFooter>
                  <DialogClose asChild>
                    <Button variant="outline" className="cursor-pointer">
                      取消
                    </Button>
                  </DialogClose>
                  <Button className="cursor-pointer">添加</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </FieldLegend>
          <FieldDescription className="text-sm">
            模型上下文协议 (MCP)
            通过集成外部工具来增强性能，例如私有域搜索、网页浏览、订餐、PPT
            生成等任务。
          </FieldDescription>
          {/* 中间列表内容 */}
          <ItemGroup>
            <Item variant="outline">
              <ItemContent>
                <ItemTitle className="w-full flex justify-between items-center text-md font-bold text-gray-700">
                  {/* 左侧MCP名称 */}
                  <div className="flex gap-2 items-center">
                    bilibili-video-info-mcp
                    <Badge>stdio</Badge>
                    <Badge>禁用</Badge>
                  </div>
                  {/* 右侧基础操作 */}
                  <div className="flex items-center justify-center gap-2">
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon-xs"
                      className="cursor-pointer"
                    >
                      <Trash />
                    </Button>
                    <Switch />
                  </div>
                </ItemTitle>
                <ItemDescription className="flex flex-wrap items-center gap-x-2 gap-y-1">
                  <Wrench size={12} />
                  <Badge variant="secondary" className="text-gray-500">
                    get_subtitles
                  </Badge>
                  <Badge variant="secondary" className="text-gray-500">
                    get_danmuku
                  </Badge>
                  <Badge variant="secondary" className="text-gray-500">
                    get_comments
                  </Badge>
                  <Badge variant="secondary" className="text-gray-500">
                    version
                  </Badge>
                  <Badge variant="secondary" className="text-gray-500">
                    list_buckets
                  </Badge>
                  <Badge variant="secondary" className="text-gray-500">
                    get_object
                  </Badge>
                  <Badge variant="secondary" className="text-gray-500">
                    get_images
                  </Badge>
                  <Badge variant="secondary" className="text-gray-500">
                    get_pngs
                  </Badge>
                </ItemDescription>
              </ItemContent>
            </Item>
          </ItemGroup>
        </FieldSet>
      </FieldGroup>
    </div>
  )
}

export function Configs() {
  const [activetedSetting, setActivetedSetting] = useState("common-setting")
  const settingMenus = [
    {
      key: "common-setting",
      icon: Settings,
      title: "通用设置",
      childComponent: CommonSetting,
    },
    {
      key: "llm-setting",
      icon: Languages,
      title: "模型提供商",
      childComponent: LLMSetting,
    },
    {
      key: "a2a-setting",
      icon: LayoutGrid,
      title: "A2A Agent设置",
      childComponent: A2ASetting,
    },
    {
      key: "mcp-setting",
      icon: Gift,
      title: "MCP 服务器",
      childComponent: MCPSetting,
    },
  ]
  return (
    <Dialog>
      {/* 模态窗触发器 */}
      <DialogTrigger asChild>
        <Button variant="outline" size="icon-sm" className="cursor-pointer">
          <Settings />
        </Button>
      </DialogTrigger>
      {/* 模态窗内容 */}
      <DialogContent className="!max-w-[850px]">
        {/* 模态窗头部 */}
        <DialogHeader className="border-b pb-4">
          <DialogTitle className="text-gray-700">设置</DialogTitle>
          <DialogDescription className="text-gray-500">
            在此管理您的设置。
          </DialogDescription>
        </DialogHeader>
        {/* 模态窗主体 */}
        <div className="flex flex-row gap-4">
          {/* 左侧快捷菜单 */}
          <div className="max-w-[180px]">
            <div className="flex flex-col gap-0">
              {settingMenus.map((setting) => (
                <Button
                  key={setting.key}
                  variant={
                    activetedSetting === setting.key ? "default" : "ghost"
                  }
                  className="cursor-pointer justify-start"
                  onClick={() => setActivetedSetting(setting.key)}
                >
                  <setting.icon />
                  {setting.title}
                </Button>
              ))}
            </div>
          </div>
          {/* 分隔 */}
          <Separator orientation="vertical" />
          {/* 右侧表单内容 */}
          <div className="flex-1 h-[500px] scrollbar-hide overflow-y-auto">
            {activetedSetting === "common-setting" && <CommonSetting />}
            {activetedSetting === "llm-setting" && <LLMSetting />}
            {activetedSetting === "a2a-setting" && <A2ASetting />}
            {activetedSetting === "mcp-setting" && <MCPSetting />}
          </div>
        </div>
        {/* 模态窗footer */}
        <DialogFooter className="border-t pt-4">
          <DialogClose asChild>
            <Button variant="outline" className="cursor-pointer">
              取消
            </Button>
          </DialogClose>
          <Button className="cursor-pointer">保存</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
