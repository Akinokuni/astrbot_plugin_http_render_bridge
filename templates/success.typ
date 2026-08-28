// 成功消息模板
// 支持变量: title, message, timestamp, qr_code, qr_text
#let data = json(bytes(sys.inputs.at("data", default: "{}")))
#let title = data.at("title", default: "操作成功")
#let message = data.at("message", default: "操作已成功完成")
#let timestamp = data.at("timestamp", default: "刚刚")
#let qr_uri = data.at("qr_code", default: none)
#let qr_text = data.at("qr_text", default: "扫码访问链接")

// 将hex字符串解码为图片字节（插件注入的图片数据为hex格式）
#let hex-to-bytes(s) = bytes(range(0, calc.floor(s.len() / 2)).map(i => int(s.slice(i * 2, i * 2 + 2), base: 16)))

#set page(width: 580pt, height: auto, margin: 28pt,
         fill: gradient.linear(rgb("#f0fff4"), rgb("#c6f6d5"), angle: 135deg))
#set text(font: ("Noto Sans SC", "Noto Sans CJK SC", "Microsoft YaHei", "PingFang SC", "SimHei"), lang: "zh", region: "cn", size: 14pt)

#block(fill: white, radius: 15pt, inset: (x: 30pt, y: 28pt))[
  #align(center)[
    #block(width: 56pt, height: 56pt, fill: rgb("#c6f6d5"), radius: 50%)[
      #align(center + horizon)[#text(size: 30pt, fill: rgb("#276749"))[✓]]
    ]
  ]
  #v(14pt)
  #align(center)[#text(size: 22pt, weight: "bold", fill: rgb("#22543d"))[#title]]
  #v(12pt)
  #align(center)[#text(size: 14pt, fill: rgb("#4a5568"))[#message]]
  #v(14pt)
  #line(length: 100%, stroke: 0.8pt + rgb("#e6fffa"))
  #v(10pt)
  #align(center)[#text(size: 10pt, fill: rgb("#a0aec0"))[#timestamp]]
]

// 二维码（hex 字符串注入），绝对定位到页面右上角
#if qr_uri != none [
  #place(top + right, dx: 24pt, dy: 24pt)[
    #block(fill: white, radius: 10pt, inset: 8pt)[
      #image(hex-to-bytes(qr_uri), width: 100pt)
      #v(4pt)
      #align(center)[#text(size: 9pt, fill: rgb("#888888"))[#qr_text]]
    ]
  ]
]
