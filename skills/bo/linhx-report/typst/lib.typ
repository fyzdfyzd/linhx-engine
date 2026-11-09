// linhx-report: thư viện dàn trang báo cáo (Typst 0.15).
// Không viết nội dung ở đây. report.py dựng 10-bao-cao.json (IR khối đóng) rồi gọi:
//   #import "lib.typ": bao-cao
//   #bao-cao(json("bao-cao.json"))
// Mọi chữ đi vào dưới dạng chuỗi JSON nên không cần thoát ký tự Typst.

#let mm-of(x) = x * 1mm
#let pt-of(x) = x * 1pt

// ---------- Inline: runs ----------
// run: {"t": chữ} | {"b": đậm} | {"i": nghiêng} | {"fn": chú thích cuối trang} | {"bc": số nguồn}
#let runs(rs, th) = {
  // Nhiều mã nguồn liền nhau cách bằng dấu phẩy (11,12 chứ không phải 1112).
  let truoc = false
  for r in rs {
    if "bc" in r {
      super(text(fill: rgb(th.mau.nhan), size: 0.85em, (if truoc { "," } else { "" }) + str(r.bc)))
      truoc = true
    } else {
      truoc = false
      if "t" in r { r.t }
      else if "b" in r { strong(r.b) }
      else if "i" in r { emph(r.i) }
      else if "fn" in r { footnote(r.fn) }
    }
  }
}

// ---------- Khối ----------
#let nhan(s, th) = text(font: th.font.phu, size: pt-of(th.co.chu_thich + 0.5), weight: 600,
  tracking: 0.06em, fill: rgb(th.mau.nhan), upper(s))

#let khoi-hinh(b, th) = {
  let c = rgb(th.mau.chinh)
  let body = block(width: 100%, breakable: false,
    stroke: if th.hinh.vach_tren { (top: 1.2pt + c) } else { none },
    inset: (top: 2.5mm), {
    set par(justify: false, first-line-indent: 0pt)
    set align(left)
    nhan(th.hinh.nhan + " " + str(b.so), th)
    v(0.8mm)
    text(font: th.font.tieu_de, size: pt-of(th.co.hinh_tieu_de), weight: 700, fill: c, b.tieu_de)
    if b.at("doi_tuong", default: none) != none {
      linebreak()
      text(font: th.font.phu, size: pt-of(th.co.chu_thich + 0.5), fill: rgb(th.mau.chu_phu), b.doi_tuong)
    }
    v(1.5mm)
    if b.at("svg", default: none) != none { image(b.svg, width: 100%) }
    else if b.at("bang", default: none) != none {
      let bg = b.bang
      set text(font: th.font.phu, size: pt-of(th.co.chu_thich + 1.5))
      table(columns: bg.cot.len(), stroke: (x, y) => (bottom: if y == 0 { 0.8pt + c } else { 0.4pt + rgb(th.mau.ke) }),
        inset: (x: 2mm, y: 1.8mm), align: (x, y) => if x > 0 and bg.dong.all(d => d.at(x).trim().len() > 0 and "0123456789".contains(d.at(x).trim().first())) and bg.dong.all(d => d.at(x).len() < 14) { right } else { left },
        fill: (x, y) => if y > 0 and calc.even(y) { rgb(th.mau.nen_phu).transparentize(40%) } else { none },
        ..bg.cot.map(h => text(weight: 700, fill: c, h)), ..bg.dong.flatten())
    }
    v(1mm)
    set text(font: th.font.phu, size: pt-of(th.co.chu_thich), fill: rgb(th.mau.chu_phu))
    if b.at("ghi_chu", default: none) != none { [Ghi chú: #b.ghi_chu] ; linebreak() }
    [Nguồn: #b.nguon]
  })
  if b.at("_ghep", default: false) { body }
  else if b.at("rong", default: "full") == "col" and th.cot == 1 { v(2mm); block(width: 58%, body); v(3mm) }
  else if b.at("rong", default: "full") == "full" and th.cot > 1 {
    place(top, float: true, scope: "parent", clearance: 6mm, body)
  } else { v(2mm); body; v(3mm) }
}

#let khoi-trich(b, th) = block(width: 100%, above: 4mm, below: 5mm, inset: (y: 3mm), breakable: false,
  stroke: (top: 2pt + rgb(th.mau.nhan), bottom: 0.5pt + rgb(th.mau.ke)), {
  set par(justify: false, leading: 0.45em)
  text(font: th.font.tieu_de, style: "italic", size: pt-of(th.co.than * 1.45), fill: rgb(th.mau.chinh), runs(b.r, th))
  if b.at("ai", default: none) != none {
    linebreak(); v(1mm)
    text(font: th.font.phu, size: pt-of(th.co.chu_thich + 0.5), fill: rgb(th.mau.chu_phu), b.ai)
  }
})

#let khoi-solon(b, th) = {
  let n = b.items.len()
  block(width: 100%, breakable: false, above: 3mm, below: 4mm, {
    grid(columns: (1fr,) * n, column-gutter: 5mm, ..b.items.map(it => block(width: 100%,
      stroke: (top: 2.5pt + rgb(th.mau.nhan)), inset: (top: 2.5mm), {
      set par(justify: false)
      block(below: 2mm, text(font: th.font.tieu_de, size: pt-of(if it.so.clusters().len() > 8 { th.co.so_lon * 0.78 } else { th.co.so_lon }),
        weight: 700, fill: rgb(th.mau.chinh), top-edge: "cap-height", bottom-edge: "baseline", it.so))
      block(above: 0pt, text(font: th.font.phu, size: pt-of(th.co.than - 1), fill: rgb(th.mau.chu), par(leading: 0.5em, it.giai_thich)))
    })))
    if b.at("nguon", default: none) != none {
      v(1mm); text(font: th.font.phu, size: pt-of(th.co.chu_thich), fill: rgb(th.mau.chu_phu))[Nguồn: #b.nguon]
    }
  })
}

#let khoi-khuyennghi(b, th) = {
  // Trang hành động (T20): mỗi việc một hàng, số lớn, việc in đậm cột trái, giải thích cột phải.
  for (i, it) in b.items.enumerate() {
    block(width: 100%, breakable: false, above: if i == 0 { 6mm } else { 0pt }, below: 0pt, inset: (y: 4.5mm),
      stroke: (top: if i == 0 { 1.4pt + rgb(th.mau.chinh) } else { 0.5pt + rgb(th.mau.ke) }),
      grid(columns: (14mm, 58mm, 1fr), column-gutter: 5mm,
        text(font: th.font.tieu_de, size: 28pt, weight: 700, fill: rgb(th.mau.nhan), top-edge: "cap-height", bottom-edge: "baseline", str(i + 1)),
        { set par(justify: false, leading: 0.45em)
          text(font: th.font.tieu_de, weight: 700, size: pt-of(th.co.than + 2), fill: rgb(th.mau.chinh), it.t) },
        { set par(justify: false); set text(size: pt-of(th.co.than - 0.3)); runs(it.r, th) }))
  }
}

#let khoi(b, th) = {
  let k = b.k
  if k == "p" { par(runs(b.r, th)) }
  else if k == "h2" {
    block(above: 1.3em, below: 0.6em, sticky: true, {
      set par(justify: false)
      text(font: th.font.tieu_de, size: pt-of(th.co.h2), weight: 700, fill: rgb(th.mau.chinh), b.t) })
  }
  else if k == "ul" { list(..b.items.map(it => runs(it, th))) }
  else if k == "hinh" { khoi-hinh(b, th) }
  else if k == "trich" { khoi-trich(b, th) }
  else if k == "so-lon" { khoi-solon(b, th) }
  else if k == "khuyen-nghi" { khoi-khuyennghi(b, th) }
  else if k == "sidebar" {
    block(width: 100%, fill: rgb(th.mau.nen_phu), inset: (x: 4mm, y: 3.5mm), breakable: false, above: 3mm, below: 4mm, {
      set text(font: th.font.phu, size: pt-of(th.co.than - 1.2))
      set par(justify: false)
      nhan(b.at("nhan", default: "Góc nhìn"), th); linebreak()
      text(weight: 700, size: pt-of(th.co.than + 0.5), fill: rgb(th.mau.chinh), b.t)
      v(1mm)
      for x in b.khoi { khoi(x, th) }
    })
  }
}

// ---------- Trang đặc biệt ----------
#let trang-bia(d, th) = page(margin: 0pt, header: none, footer: none, {
  let c = rgb(th.mau.chinh)
  if d.bia.at("anh", default: none) != none {
    place(image(d.bia.anh, width: 100%, height: 100%, fit: "cover"))
    place(rect(width: 100%, height: 100%, fill: gradient.linear(c.transparentize(100%), c.transparentize(15%), angle: 90deg)))
  } else {
    place(rect(width: 100%, height: 100%, fill: c))
    // Không có ảnh: mô-típ khối màu gợi một biểu đồ thanh, một thanh màu nhấn.
    let dai = (62, 118, 84, 146, 40, 101, 132, 73, 156, 90)
    for (k, w) in dai.enumerate() {
      place(top + right, dy: 22mm + k * 9.5mm, rect(width: w * 1mm, height: 5.2mm,
        fill: if k == 6 { rgb(th.mau.nhan) } else { white.transparentize(88% - calc.rem(k, 3) * 3%) }))
    }
    place(top + left, dx: 20mm, dy: 20mm, text(font: th.font.phu, size: 10pt, weight: 700, tracking: 0.1em, fill: white, upper(d.meta.don_vi)))
  }
  place(bottom + left, dx: 20mm, dy: -30mm, block(width: 160mm, {
    set text(fill: white, font: th.font.phu)
    set par(justify: false)
    text(size: 9pt, weight: 600, tracking: 0.08em, upper(d.meta.nhan_loat))
    v(5mm)
    text(font: th.font.tieu_de, size: pt-of(th.co.bia), weight: 700, par(leading: 0.28em, d.meta.tieu_de))
    v(5mm)
    block(width: 140mm, text(font: th.font.tieu_de, size: 14pt, style: "italic", d.meta.phu_de))
    v(12mm)
    line(length: 100%, stroke: 0.6pt + white.transparentize(40%))
    v(1mm)
    text(size: 8.5pt, [#d.meta.tac_gia · #d.meta.ngay])
  }))
})

#let mark-chuong(s) = [#metadata(s) <chuong>]

#let tieu-de-trang(s, th) = {
  set par(justify: false)
  text(font: th.font.tieu_de, size: pt-of(th.co.h1), weight: 700, fill: rgb(th.mau.chinh), s)
  v(4mm)
}

// Mở chương dạng chữ lớn (P1) hoặc nửa trang màu (P4), rồi chảy nội dung.
#let chuong(ch, th) = {
  pagebreak(weak: true)
  mark-chuong("Chương " + str(ch.so) + " · " + ch.ten_ngan)
  let c = rgb(th.mau.chinh)
  if th.mo_chuong == "nua-trang" {
    // Mở chương nửa trang màu tràn lề, phủ cả đầu trang.
    let m = mm-of(th.le.ngoai)
    let t = mm-of(th.le.tren)
    block(width: 100%, height: 92mm - t, above: 0pt, below: 8mm, breakable: false, {
      place(top + left, dx: -m, dy: -t, rect(width: 100% + 2 * m, height: 92mm, fill: c))
      if ch.at("anh", default: none) != none {
        place(top + left, dx: -m, dy: -t, image(ch.anh, width: 100% + 2 * m, height: 92mm, fit: "cover"))
        place(top + left, dx: -m, dy: -t, rect(width: 100% + 2 * m, height: 92mm,
          fill: gradient.linear(c.transparentize(100%), c.transparentize(10%), angle: 90deg)))
      }
      place(top + left, dy: 2mm, text(font: th.font.tieu_de, size: 64pt, weight: 700, fill: rgb(th.mau.nhan_toi), str(ch.so)))
      place(bottom + left, dy: -6mm, block(width: 100%, {
        set par(justify: false)
        heading(level: 1, text(fill: white, ch.tieu_de))
      }))
    })
  } else {
    grid(columns: (auto, 1fr), column-gutter: 4mm, align: bottom,
      text(font: th.font.tieu_de, size: 54pt, weight: 700, fill: rgb(th.mau.nhan), top-edge: "cap-height", bottom-edge: "baseline",
        if ch.so < 10 { "0" + str(ch.so) } else { str(ch.so) }),
      { text(font: th.font.phu, size: 9pt, weight: 600, tracking: 0.08em, fill: rgb(th.mau.nhan), upper("Chương " + str(ch.so) + " · " + ch.ten_ngan))
        v(1.2mm); line(length: 100%, stroke: 0.6pt + rgb(th.mau.ke)) })
    v(5mm)
    heading(level: 1, ch.tieu_de)
    v(2mm)
  }
  if ch.at("sapo", default: none) != none {
    block(width: if th.le_treo > 0 { 100% } else { 88% }, below: 6mm,
      text(font: th.font.tieu_de, size: pt-of(th.co.sapo), fill: rgb(th.mau.chu_phu), par(justify: false, ch.sapo)))
  }
  let body = {
    for (i, b) in ch.khoi.enumerate() {
      if i == 0 and b.k == "p" and th.dropcap {
        let first = b.r.at(0).at("t", default: "")
        if first.len() > 0 {
          let cl = first.clusters()
          block(below: 0.65em, grid(columns: (auto, 1fr), column-gutter: 1.2mm,
            text(font: th.font.tieu_de, weight: 700, size: pt-of(th.co.than * 3.6), fill: rgb(th.mau.chinh),
              top-edge: "cap-height", bottom-edge: "baseline", cl.at(0)),
            par(runs(((t: cl.slice(1).join()),) + b.r.slice(1), th))))
        } else { khoi(b, th) }
      } else { khoi(b, th) }
    }
  }
  if th.cot > 1 { columns(th.cot, gutter: mm-of(th.ranh_cot), body) }
  else if th.le_treo > 0 {
    // Lề treo kiểu báo cáo chiến lược: chữ thụt vào cột phải, hình và số lớn trải toàn khổ.
    let bo-qua = ()
    for (i, b) in ch.khoi.enumerate() {
      let sau = if i + 1 < ch.khoi.len() { ch.khoi.at(i + 1) } else { none }
      if i in bo-qua { }
      else if b.k == "hinh" and b.at("rong", default: "full") == "col" and sau != none and (sau.k == "sidebar" or (sau.k == "hinh" and sau.at("rong", default: "full") == "col")) {
        // Hai khối hẹp đặt cạnh nhau: kiểu trang đôi hình hoặc hình kèm hộp bên lề.
        bo-qua.push(i + 1)
        block(breakable: false, above: 3mm, below: 4mm, grid(columns: (1fr, 1fr), column-gutter: 8mm,
          khoi-hinh(b + (_ghep: true), th),
          if sau.k == "hinh" { khoi-hinh(sau + (_ghep: true), th) } else { v(6mm); khoi(sau, th) }))
      }
      else if b.k in ("hinh", "so-lon", "khuyen-nghi") { khoi(b, th) }
      else if b.k == "h2" and sau != none and sau.k == "khuyen-nghi" {
        pagebreak(weak: true)
        block(sticky: true, below: 8mm, {
          text(font: th.font.phu, size: 9pt, weight: 600, tracking: 0.08em, fill: rgb(th.mau.nhan), upper("Khuyến nghị"))
          v(2mm)
          set par(justify: false, leading: 0.3em)
          text(font: th.font.tieu_de, size: pt-of(th.co.h1), weight: 700, fill: rgb(th.mau.chinh), b.t)
        })
      }
      else if b.k == "h2" {
        block(sticky: true, breakable: false, above: 1.2em, below: 0.5em, grid(columns: (th.le_treo * 100% - 4mm, 1fr), column-gutter: 4mm,
          box(stroke: (top: 1pt + rgb(th.mau.nhan)), inset: (top: 1.5mm), width: 100%,
            text(font: th.font.phu, size: pt-of(th.co.chu_thich + 0.5), weight: 600, fill: rgb(th.mau.nhan), tracking: 0.04em, upper("Mục " + str(ch.so) + "." + str(ch.khoi.slice(0, i + 1).filter(x => x.k == "h2").len())))),
          { set par(justify: false); text(font: th.font.tieu_de, size: pt-of(th.co.h2), weight: 700, fill: rgb(th.mau.chinh), b.t) }))
      }
      else { pad(left: th.le_treo * 100%, khoi(b, th)) }
    }
  }
  else { body }
}

// ---------- Toàn bộ báo cáo ----------
#let bao-cao(d) = {
  let th = d.theme
  let c = rgb(th.mau.chinh)
  set document(title: d.meta.tieu_de, author: d.meta.tac_gia)
  set text(font: th.font.than, size: pt-of(th.co.than), lang: "vi", fill: rgb(th.mau.chu), hyphenate: false)
  set par(justify: th.can_deu, leading: (th.gian_dong - 0.75) * 1em, spacing: (th.gian_dong - 0.3) * 1em)
  // Chú thích cuối trang đánh chữ (a, b, c) để không lẫn với số nguồn đánh số.
  set footnote(numbering: "a")
  set footnote.entry(separator: line(length: 25%, stroke: 0.5pt + rgb(th.mau.ke)))
  // Nhãn suy luận: nhỏ, xám, không chen ngang câu.
  show "[SUY LUẬN]": text(size: 0.72em, weight: 600, tracking: 0.04em, fill: rgb(th.mau.chu_phu), "[SUY LUẬN]")
  show footnote.entry: set text(font: th.font.phu, size: pt-of(th.co.chu_thich), fill: rgb(th.mau.chu_phu))
  show footnote.entry: set par(justify: false)
  show heading.where(level: 1): set text(font: th.font.tieu_de, size: pt-of(th.co.h1), weight: 700, fill: c)
  show heading.where(level: 1): set par(justify: false, leading: 0.3em)
  show heading.where(level: 1): set block(below: 0.5em)
  show list: set list(marker: text(fill: rgb(th.mau.nhan), "■"), indent: 1mm, body-indent: 2.5mm)

  trang-bia(d, th)

  let running = context {
    let pg = here().page()
    let on = query(<chuong>).filter(m => m.location().page() == pg)
    let prev = query(selector(<chuong>).before(here()))
    let lab = if on.len() > 0 { on.first().value } else if prev.len() > 0 { prev.last().value } else { "" }
    set text(font: th.font.phu, size: 7.5pt, fill: rgb(th.mau.chu_phu))
    grid(columns: (1fr, auto), upper(text(weight: 600, tracking: 0.05em, lab)), d.meta.tieu_de_ngan)
    v(-1.5mm)
    line(length: 100%, stroke: 0.5pt + rgb(th.mau.ke))
  }
  let foot = context {
    set text(font: th.font.phu, size: 7.5pt, fill: rgb(th.mau.chu_phu))
    grid(columns: (1fr, auto), d.meta.chan_trang, text(weight: 700, fill: c, counter(page).display()))
  }
  set page(paper: th.kho, margin: (top: mm-of(th.le.tren), bottom: mm-of(th.le.duoi), x: mm-of(th.le.ngoai)),
    header: running, footer: foot, header-ascent: 35%, footer-descent: 40%)
  counter(page).update(2)

  // Mục lục + tóm tắt điều hành
  mark-chuong("Mục lục")
  tieu-de-trang("Mục lục", th)
  show outline.entry: it => {
    set text(font: th.font.tieu_de, size: 12.5pt, weight: 600, fill: c)
    block(below: 0pt, inset: (y: 3mm), stroke: (bottom: 0.5pt + rgb(th.mau.ke)), width: 100%,
      link(it.element.location(), it.indented(none, [#it.body() #box(width: 1fr) #text(font: th.font.phu, size: 10pt, weight: 700, fill: rgb(th.mau.nhan), it.page())])))
  }
  outline(title: none, depth: 1)
  if d.meta.at("luan_de", default: none) != none {
    // Trang lót luận đề gộp vào nửa dưới mục lục: câu trả lời của cả báo cáo trong một câu.
    place(bottom + left, dx: -mm-of(th.le.ngoai), dy: 0mm, block(width: 100% + 2 * mm-of(th.le.ngoai), height: 112mm, fill: c,
      inset: (x: mm-of(th.le.ngoai), top: 14mm, bottom: 12mm), {
      set par(justify: false, leading: 0.42em)
      text(font: th.font.phu, size: 8.5pt, weight: 700, tracking: 0.1em, fill: rgb(th.mau.nhan_toi), upper(d.meta.at("luan_de_nhan", default: "Câu trả lời ngắn")))
      v(5mm)
      block(width: 88%, text(font: th.font.tieu_de, size: 21pt, weight: 600, fill: white, d.meta.luan_de))
      if d.meta.at("luan_de_phu", default: none) != none {
        v(6mm)
        block(width: 80%, text(font: th.font.phu, size: 9.5pt, fill: white.transparentize(20%), d.meta.luan_de_phu))
      }
    }))
  }
  pagebreak()

  let tt = d.tom_tat
  mark-chuong(tt.tieu_de)
  heading(level: 1, tt.tieu_de)
  if tt.at("mo", default: none) != none {
    block(width: 100%, below: 5mm, text(font: th.font.tieu_de, size: pt-of(th.co.sapo), fill: rgb(th.mau.chu_phu), par(justify: false, tt.mo)))
  }
  if tt.at("kpi", default: ()).len() > 0 { khoi-solon((items: tt.kpi, nguon: tt.at("kpi_nguon", default: none)), th) }
  for (i, it) in tt.diem.enumerate() {
    block(width: 100%, breakable: false, below: 0pt, stroke: (top: 0.5pt + rgb(th.mau.ke)), inset: (y: 5mm),
      grid(columns: (14mm, 1fr), column-gutter: 3mm,
        text(font: th.font.tieu_de, size: 24pt, weight: 700, fill: rgb(th.mau.nhan), top-edge: "cap-height", bottom-edge: "baseline", str(i + 1)),
        { set par(justify: false, leading: 0.55em)
          block(below: 1.8mm, text(font: th.font.tieu_de, weight: 700, fill: c, size: pt-of(th.co.than + 2.2), runs(it.y, th)))
          runs(it.chi_tiet, th) }))
  }

  for ch in d.chuong { chuong(ch, th) }

  // Phương pháp, nguồn, tác giả
  if d.at("phuong_phap", default: ()).len() > 0 {
    pagebreak(weak: true)
    set page(fill: rgb(th.mau.nen_phu))
    mark-chuong("Phương pháp")
    heading(level: 1, "Về nghiên cứu này")
    v(4mm)
    block(width: 86%, for b in d.phuong_phap { khoi(b, th) })
    pagebreak()
    set page(fill: none)
  }
  if d.at("nguon", default: ()).len() > 0 {
    pagebreak(weak: true)
    mark-chuong("Nguồn")
    heading(level: 1, "Nguồn trích dẫn")
    v(2mm)
    set text(font: th.font.phu, size: pt-of(th.co.chu_thich), fill: rgb(th.mau.chu))
    set par(justify: false, spacing: 0.55em, leading: 0.5em)
    columns(2, gutter: 6mm, for (i, n) in d.nguon.enumerate() {
      grid(columns: (6mm, 1fr), text(weight: 700, fill: rgb(th.mau.nhan), str(i + 1)), n.mo_ta)
    })
  }
  // Bìa sau
  page(margin: 0pt, header: none, footer: none, {
    place(rect(width: 100%, height: 100%, fill: c))
    place(bottom + left, dx: 20mm, dy: -25mm, block(width: 170mm, {
      set text(fill: white, font: th.font.phu, size: 8.5pt)
      set par(justify: false)
      text(size: 12pt, weight: 700, d.meta.don_vi); linebreak(); v(2mm)
      d.meta.ban_quyen
    }))
  })
}
