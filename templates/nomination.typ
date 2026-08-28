// 提名展示模板
// 支持变量: header, name, title1~title3, evaluate1~evaluate3, qr_code, qr_text
#let data = json(bytes(sys.inputs.at("data", default: "{}")))
#let header = data.at("header", default: "十二器：提名")
#let name = data.at("name", default: "匿名")
#let title1 = data.at("title1", default: "")
#let evaluate1 = data.at("evaluate1", default: "暂无推荐语")
#let title2 = data.at("title2", default: "")
#let evaluate2 = data.at("evaluate2", default: "暂无推荐语")
#let title3 = data.at("title3", default: "")
#let evaluate3 = data.at("evaluate3", default: "暂无推荐语")
#let qr_uri = data.at("qr_code", default: none)
#let qr_text = data.at("qr_text", default: "扫码参与")

// 将hex字符串解码为图片字节（插件注入的图片数据为hex格式）
#let hex-to-bytes(s) = bytes(range(0, calc.floor(s.len() / 2)).map(i => int(s.slice(i * 2, i * 2 + 2), base: 16)))

#set page(width: 640pt, height: auto, margin: 30pt, fill: rgb("#f4f6f8"))
#set text(font: ("Noto Sans SC", "Microsoft YaHei"), lang: "zh", region: "cn", size: 15pt)

#let nomination-item(label, title, evaluate) = [
  #v(14pt)
  #line(length: 100%, stroke: 0.8pt + rgb("#eaeef2"))
  #v(14pt)
  #grid(columns: (90pt, 1fr), row-gutter: 10pt)[
    #text(fill: rgb("#4a6fa5"), weight: "bold")[#label]
    #text(size: 17pt, weight: "bold")[#title]
    #text(fill: rgb("#4a6fa5"), weight: "bold")[推荐语:]
    #text(fill: rgb("#555555"))[#evaluate]
  ]
]

#block(fill: white, radius: 12pt, stroke: 1pt + rgb("#e0e0e0"), inset: (x: 36pt, y: 32pt))[
  #text(size: 22pt, weight: "bold", fill: rgb("#4a6fa5"))[#header]
  #v(6pt)
  #line(length: 100%, stroke: 1.5pt + rgb("#4a6fa5"))
  #v(18pt)
  #grid(columns: (90pt, 1fr), row-gutter: 14pt)[
    #text(fill: rgb("#4a6fa5"), weight: "bold")[推荐人:]
    #text(weight: "bold")[#name]
  ]

  #if title1 != "" [
    #nomination-item("作品一:", title1, evaluate1)
  ]
  #if title2 != "" [
    #nomination-item("作品二:", title2, evaluate2)
  ]
  #if title3 != "" [
    #nomination-item("作品三:", title3, evaluate3)
  ]
]

// 二维码（hex 字符串注入），绝对定位到页面右上角
#if qr_uri != none [
  #place(top + right, dx: 24pt, dy: 24pt)[
    #block(fill: white, radius: 10pt, inset: 8pt, stroke: 1pt + rgb("#e0e0e0"))[
      #image(hex-to-bytes(qr_uri), width: 100pt)
      #v(4pt)
      #align(center)[#text(size: 9pt, fill: rgb("#888888"))[#qr_text]]
    ]
  ]
]
