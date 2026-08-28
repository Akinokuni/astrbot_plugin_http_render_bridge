// 数据报告模板
// 支持变量: title, total_users, active_users, new_users, total_messages, timestamp
#let data = json(bytes(sys.inputs.at("data", default: "{}")))
#let title = data.at("title", default: "数据报告")
#let total_users = data.at("total_users", default: "0")
#let active_users = data.at("active_users", default: "0")
#let new_users = data.at("new_users", default: "0")
#let total_messages = data.at("total_messages", default: "0")
#let timestamp = data.at("timestamp", default: "刚刚")

#set page(width: 620pt, height: auto, margin: 30pt,
         fill: gradient.linear(rgb("#eef2ff"), rgb("#e0e7ff"), angle: 180deg))
#set text(font: ("Noto Sans SC", "Microsoft YaHei"), lang: "zh", region: "cn", size: 14pt)

#let metric-card(label, value) = block(
  fill: rgb("#f5f7ff"), radius: 10pt, inset: (x: 16pt, y: 14pt), width: 100%,
)[
  #text(size: 11pt, fill: rgb("#6366f1"))[#label]
  #v(6pt)
  #text(size: 22pt, weight: "bold", fill: rgb("#1e1b4b"))[#value]
]

#block(fill: white, radius: 14pt, inset: (x: 28pt, y: 24pt))[
  #text(size: 22pt, weight: "bold", fill: rgb("#3730a3"))[#title]
  #v(16pt)
  #grid(columns: (1fr, 1fr), column-gutter: 14pt, row-gutter: 14pt)[
    #metric-card("总用户数", total_users)
    #metric-card("活跃用户", active_users)
    #metric-card("新增用户", new_users)
    #metric-card("消息总数", total_messages)
  ]
  #v(14pt)
  #line(length: 100%, stroke: 0.8pt + rgb("#e0e7ff"))
  #v(10pt)
  #align(center)[#text(size: 10pt, fill: rgb("#94a3b8"))[生成时间: #timestamp]]
]
