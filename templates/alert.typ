// 警告模板
// 支持变量: title, message, timestamp, level
#let data = json(bytes(sys.inputs.at("data", default: "{}")))
#let title = data.at("title", default: "系统警告")
#let message = data.at("message", default: "检测到系统异常")
#let timestamp = data.at("timestamp", default: "刚刚")
#let level = data.at("level", default: "WARNING")

#set page(width: 560pt, height: auto, margin: 30pt, fill: rgb("#fff5f5"))
#set text(font: ("Noto Sans SC", "Noto Sans CJK SC", "Microsoft YaHei", "PingFang SC", "SimHei"), lang: "zh", region: "cn", size: 14pt)

#block(fill: white, radius: 12pt, stroke: 1.5pt + rgb("#f56565"), inset: (x: 26pt, y: 24pt))[
  #align(center)[#text(size: 40pt, weight: "bold", fill: rgb("#e53e3e"))[!]]
  #v(10pt)
  #align(center)[#text(size: 20pt, weight: "bold", fill: rgb("#c53030"))[#title]]
  #v(12pt)
  #align(center)[#text(size: 14pt, fill: rgb("#4a5568"))[#message]]
  #v(14pt)
  #line(length: 100%, stroke: 0.8pt + rgb("#fed7d7"))
  #v(10pt)
  #align(center)[#text(size: 10pt, fill: rgb("#a0aec0"))[#timestamp + " | 级别: " + level]]
]
