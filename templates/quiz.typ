// 入群答题结果模板
// 支持变量: qq_number, score, threshold, pass_status（可选）, non_qq_subjective_text, submitted_at
#let data = json(bytes(sys.inputs.at("data", default: "{}")))
#let qq = data.at("qq_number", default: "未知QQ")
#let score_text = data.at("score", default: "0")
#let threshold_text = data.at("threshold", default: "0")
#let non_qq_subjective_text = data.at("non_qq_subjective_text", default: "无内容")
#let submitted_at = data.at("submitted_at", default: "-")

// 分数与达标线转为整数，达标状态优先取传入值，否则按分数判定
#let score = int(score_text)
#let threshold = int(threshold_text)
#let pass_status = if "pass_status" in data {
  data.at("pass_status")
} else if score >= threshold {
  "pass"
} else {
  "fail"
}

#set page(width: 600pt, height: auto, margin: 28pt,
         fill: gradient.linear(rgb("#fdfbfb"), rgb("#ebedee"), angle: 135deg))
#set text(font: ("Noto Sans SC", "Noto Sans CJK SC", "Microsoft YaHei", "PingFang SC", "SimHei"), lang: "zh", region: "cn", size: 13pt)

#block(fill: white, radius: 14pt, stroke: 1pt + rgb("#e5e7eb"), inset: (x: 26pt, y: 24pt))[
  #text(size: 20pt, weight: "bold", fill: rgb("#111827"))[#qq 入群答题]
  #v(16pt)
  #grid(columns: (150pt, 1fr), column-gutter: 16pt)[
    // 左侧：客观题分数面板
    #block(fill: rgb("#f9fafb"), radius: 10pt, inset: (x: 14pt, y: 14pt))[
      #text(size: 10pt, fill: rgb("#6b7280"))[客观题总分]
      #v(6pt)
      #text(size: 24pt, weight: "bold", fill: rgb("#111827"))[#score]
      #v(6pt)
      #if pass_status == "pass" [
        #block(fill: rgb("#dcfce7"), radius: 8pt, inset: (x: 10pt, y: 4pt))[
          #text(size: 10pt, fill: rgb("#166534"))[已达标]
        ]
      ] else [
        #block(fill: rgb("#fef3c7"), radius: 8pt, inset: (x: 10pt, y: 4pt))[
          #text(size: 10pt, fill: rgb("#92400e"))[未达标]
        ]
      ]
      #v(6pt)
      #text(size: 10pt, fill: rgb("#6b7280"))[达标线：#threshold]
    ]
    // 右侧：简答题面板
    #block(inset: (x: 14pt, y: 14pt))[
      #text(size: 10pt, fill: rgb("#6b7280"))[简答题]
      #v(6pt)
      #text(fill: rgb("#374151"))[#non_qq_subjective_text]
    ]
  ]
  #v(14pt)
  #line(length: 100%, stroke: 0.8pt + rgb("#e5e7eb"))
  #v(10pt)
  #align(center)[#text(size: 10pt, fill: rgb("#9ca3af"))[提交时间：#submitted_at]]
]
