// 通用通知模板
// 支持变量: title, content, timestamp, image, image_filename, qr_code, qr_text
#let data = json(bytes(sys.inputs.at("data", default: "{}")))
#let title = data.at("title", default: "通知")
#let content = data.at("content", default: "这是一条通知消息")
#let timestamp = data.at("timestamp", default: "刚刚")
#let image_uri = data.at("image", default: none)
#let image_filename = data.at("image_filename", default: none)
#let qr_uri = data.at("qr_code", default: none)
#let qr_text = data.at("qr_text", default: "扫码访问链接")

// 将hex字符串解码为图片字节（插件注入的图片数据为hex格式）
#let hex-to-bytes(s) = bytes(range(0, calc.floor(s.len() / 2)).map(i => int(s.slice(i * 2, i * 2 + 2), base: 16)))

#set page(width: 600pt, height: auto, margin: 28pt,
         fill: gradient.linear(rgb("#667eea"), rgb("#764ba2"), angle: 135deg))
#set text(font: ("Noto Sans SC", "Noto Sans CJK SC", "Microsoft YaHei", "PingFang SC", "SimHei"), lang: "zh", region: "cn", size: 14pt)

#block(fill: white, radius: 15pt, inset: (x: 28pt, y: 26pt))[
  #align(center)[#text(size: 22pt, weight: "bold", fill: rgb("#333333"))[#title]]
  #v(16pt)
  #text(fill: rgb("#666666"))[#content]

  #if image_uri != none [
    #v(14pt)
    #align(center)[
      #image(hex-to-bytes(image_uri), width: 80%)
      #if image_filename != none [
        #v(6pt)
        #text(size: 10pt, fill: rgb("#888888"), style: "italic")[#image_filename]
      ]
    ]
  ]

  #v(16pt)
  #line(length: 100%, stroke: 0.8pt + rgb("#eeeeee"))
  #v(12pt)
  #align(center)[#text(size: 10pt, fill: rgb("#999999"))[#timestamp]]
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
