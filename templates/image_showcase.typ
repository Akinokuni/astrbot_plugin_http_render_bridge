// 图片展示模板
// 支持变量: title, description, image, image0~image3（含各自 _filename）, qr_code, qr_text
#let data = json(bytes(sys.inputs.at("data", default: "{}")))
#let title = data.at("title", default: "图片展示")
#let description = data.at("description", default: "这里展示上传的图片内容")
#let main_uri = data.at("image", default: none)
#let main_filename = data.at("image_filename", default: none)
#let qr_uri = data.at("qr_code", default: none)
#let qr_text = data.at("qr_text", default: "扫码访问链接")

// 将hex字符串解码为图片字节（插件注入的图片数据为hex格式）
#let hex-to-bytes(s) = bytes(range(0, calc.floor(s.len() / 2)).map(i => int(s.slice(i * 2, i * 2 + 2), base: 16)))

#set page(width: 640pt, height: auto, margin: 30pt,
         fill: gradient.linear(rgb("#fdf2f8"), rgb("#fce7f3"), angle: 180deg))
#set text(font: ("Noto Sans SC", "Noto Sans CJK SC", "Microsoft YaHei", "PingFang SC", "SimHei"), lang: "zh", region: "cn", size: 14pt)

#let show-image(uri, filename) = align(center)[
  #image(hex-to-bytes(uri), width: 100%)
  #if filename != none and filename != "" [
    #v(4pt)
    #text(size: 9pt, fill: rgb("#888888"), style: "italic")[#filename]
  ]
]

#let extras = (
  (data.at("image0", default: none), data.at("image0_filename", default: none)),
  (data.at("image1", default: none), data.at("image1_filename", default: none)),
  (data.at("image2", default: none), data.at("image2_filename", default: none)),
  (data.at("image3", default: none), data.at("image3_filename", default: none)),
).filter(p => p.at(0) != none)

#block(fill: white, radius: 14pt, inset: (x: 28pt, y: 24pt))[
  #text(size: 22pt, weight: "bold", fill: rgb("#9d174d"))[#title]
  #v(8pt)
  #text(fill: rgb("#6b7280"))[#description]

  #if main_uri != none [
    #v(14pt)
    #show-image(main_uri, main_filename)
  ]

  #if extras.len() > 0 [
    #v(14pt)
    #grid(columns: (1fr, 1fr), column-gutter: 10pt, row-gutter: 10pt)[
      ..extras.map(p => show-image(p.at(0), p.at(1)))
    ]
  ]
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
