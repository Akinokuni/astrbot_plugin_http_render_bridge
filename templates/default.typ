// 默认模板
// 支持变量: title, content, timestamp
#let data = json(bytes(sys.inputs.at("data", default: "{}")))
#let title = data.at("title", default: "通知")
#let content = data.at("content", default: "这是一条通知消息")
#let timestamp = data.at("timestamp", default: "刚刚")

#set page(width: 600pt, height: auto, margin: 28pt,
         fill: gradient.linear(rgb("#667eea"), rgb("#764ba2"), angle: 135deg))
#set text(font: ("Noto Sans SC", "Noto Sans CJK SC", "Microsoft YaHei", "PingFang SC", "SimHei"), lang: "zh", region: "cn", size: 14pt)

#block(fill: white, radius: 15pt, inset: (x: 28pt, y: 26pt))[
  #align(center)[#text(size: 22pt, weight: "bold", fill: rgb("#333333"))[#title]]
  #v(16pt)
  #text(fill: rgb("#666666"))[#content]
  #v(16pt)
  #line(length: 100%, stroke: 0.8pt + rgb("#eeeeee"))
  #v(12pt)
  #align(center)[#text(size: 10pt, fill: rgb("#999999"))[#timestamp]]
]
