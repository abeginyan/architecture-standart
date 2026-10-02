"""Мини-библиотека: одно описание диаграммы -> файл draw.io (.drawio) + картинка (.png).

Нужна, чтобы диаграммы можно было пересобирать скриптом, а потом спокойно
доработать руками в https://app.diagrams.net (открыть .drawio).
"""
import html
import math
import os
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_cache = {}


def font(size, bold=False):
    key = (int(size), bold)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(FONTB if bold else FONT, int(size))
    return _cache[key]


def wrap_par(text, f, maxw):
    lines, cur = [], ""
    for word in text.split(" "):
        t = (cur + " " + word).strip()
        if f.getlength(t) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def layout_text(text, w, h, size, bold_first, bold_all, minsize=8, pad=6):
    """Подбирает размер шрифта, чтобы текст влез в блок. Возвращает (size, [(line, bold)])."""
    s = size
    while True:
        out = []
        for i, par in enumerate(text.split("\n")):
            b = bold_all or (bold_first and i == 0)
            for ln in wrap_par(par, font(s, b), w - 2 * pad):
                out.append((ln, b))
        if len(out) * s * 1.25 <= h - 2 * pad + 4 or s <= minsize:
            return s, out
        s -= 1


class Diagram:
    def __init__(self, name, width, height, bg="#ffffff"):
        self.name, self.W, self.H, self.bg = name, width, height, bg
        self.groups, self.boxes, self.edges, self.lines = [], [], [], []
        self.nodes = {}

    # ---------- элементы ----------
    def box(self, id, x, y, w, h, text="", fill="#dae8fc", stroke="#6c8ebf", color="#000000",
            size=12, bold=False, bold_first=False, dashed=False, shape="rect", align="center",
            valign="middle", noborder=False, rounded=True):
        n = dict(id=id, x=x, y=y, w=w, h=h, text=text, fill=fill, stroke=stroke, color=color, size=size,
                 bold=bold, bold_first=bold_first, dashed=dashed, shape=shape, align=align,
                 valign=valign, noborder=noborder, rounded=rounded, kind="box")
        self.boxes.append(n)
        self.nodes[id] = n
        return n

    def group(self, id, x, y, w, h, title, stroke="#666666", fill=None, color="#333333", size=13, dashed=True):
        n = dict(id=id, x=x, y=y, w=w, h=h, text=title, fill=fill, stroke=stroke, color=color, size=size,
                 bold=True, bold_first=False, dashed=dashed, shape="rect", align="left", valign="top",
                 noborder=False, rounded=True, kind="group")
        self.groups.append(n)
        self.nodes[id] = n
        return n

    def text(self, id, x, y, w, h, text, size=12, bold=False, color="#000000", align="left", valign="middle"):
        return self.box(id, x, y, w, h, text, fill=None, stroke=None, color=color, size=size, bold=bold,
                        align=align, valign=valign, noborder=True, shape="text")

    def edge(self, a, b, label="", dashed=False, color="#444444", bidir=False, via=None, size=10, width=1.5):
        self.edges.append(dict(a=a, b=b, label=label, dashed=dashed, color=color, bidir=bidir,
                               via=via or [], size=size, width=width))

    def line(self, x1, y1, x2, y2, dashed=True, color="#cc0000", width=2):
        self.lines.append(dict(p=(x1, y1, x2, y2), dashed=dashed, color=color, width=width))

    # ---------- draw.io ----------
    def _style_box(self, n):
        st = []
        if n["shape"] == "text":
            st.append("text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none")
        elif n["shape"] == "cylinder":
            st.append("shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=10;whiteSpace=wrap;html=1")
        elif n["shape"] == "chevron":
            st.append("shape=step;perimeter=stepPerimeter;fixedSize=1;size=18;whiteSpace=wrap;html=1")
        else:
            st.append("rounded=%d;arcSize=8;whiteSpace=wrap;html=1" % (1 if n["rounded"] else 0))
        if n["shape"] != "text":
            st.append("fillColor=%s" % (n["fill"] or "none"))
            st.append("strokeColor=%s" % (n["stroke"] or "none"))
        st.append("fontColor=%s;fontSize=%d" % (n["color"], n["size"]))
        st.append("align=%s;verticalAlign=%s" % (n["align"], n["valign"]))
        if n["align"] == "left":
            st.append("spacingLeft=8")
        if n["dashed"]:
            st.append("dashed=1")
        if n["bold"]:
            st.append("fontStyle=1")
        return ";".join(st) + ";"

    def _val(self, n):
        parts = html.escape(n["text"]).split("\n")
        if n["bold_first"] and len(parts) > 1:
            parts[0] = "<b>%s</b>" % parts[0]
        return "<br>".join(parts)

    def _group_style(self, n):
        st = ["rounded=1;arcSize=4;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;fontColor=%s;fontSize=%d;"
              "fontStyle=1;align=left;verticalAlign=top;spacingLeft=8;spacingTop=4"
              % (n["fill"] or "none", n["stroke"], n["color"], n["size"])]
        if n["dashed"]:
            st.append("dashed=1")
        return ";".join(st) + ";"

    def to_drawio(self, path):
        cid = {}
        out = ['<mxfile host="app.diagrams.net"><diagram name="%s" id="d1">' % html.escape(self.name),
               '<mxGraphModel dx="%d" dy="%d" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" '
               'arrows="1" fold="1" page="1" pageScale="1" pageWidth="%d" pageHeight="%d" math="0" shadow="0">'
               % (self.W, self.H, self.W, self.H), '<root><mxCell id="0"/><mxCell id="1" parent="0"/>']
        k = 2
        for n in self.groups + self.boxes:
            cid[n["id"]] = "c%d" % k
            k += 1
            style = self._style_box(n) if n["kind"] == "box" else self._group_style(n)
            out.append('<mxCell id="%s" value="%s" style="%s" vertex="1" parent="1"><mxGeometry x="%d" y="%d" '
                       'width="%d" height="%d" as="geometry"/></mxCell>'
                       % (cid[n["id"]], html.escape(self._val(n), quote=True), style, n["x"], n["y"], n["w"], n["h"]))
        for e in self.edges:
            st = ("endArrow=classic;html=1;rounded=0;strokeColor=%s;strokeWidth=%s;fontSize=%d;"
                  "labelBackgroundColor=#ffffff;" % (e["color"], e["width"], e["size"]))
            if e["bidir"]:
                st += "startArrow=classic;"
            if e["dashed"]:
                st += "dashed=1;"
            pts = ""
            if e["via"]:
                pts = '<Array as="points">%s</Array>' % "".join('<mxPoint x="%d" y="%d"/>' % p for p in e["via"])
            out.append('<mxCell id="c%d" value="%s" style="%s" edge="1" parent="1" source="%s" target="%s">'
                       '<mxGeometry relative="1" as="geometry">%s</mxGeometry></mxCell>'
                       % (k, html.escape(e["label"], quote=True), st, cid[e["a"]], cid[e["b"]], pts))
            k += 1
        for l in self.lines:
            x1, y1, x2, y2 = l["p"]
            out.append('<mxCell id="c%d" value="" style="endArrow=none;html=1;strokeColor=%s;strokeWidth=%s;%s" '
                       'edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="%d" y="%d" '
                       'as="sourcePoint"/><mxPoint x="%d" y="%d" as="targetPoint"/></mxGeometry></mxCell>'
                       % (k, l["color"], l["width"], "dashed=1;" if l["dashed"] else "", x1, y1, x2, y2))
            k += 1
        out.append("</root></mxGraphModel></diagram></mxfile>")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(out))

    # ---------- PNG ----------
    @staticmethod
    def _border_point(n, tx, ty):
        cx, cy = n["x"] + n["w"] / 2, n["y"] + n["h"] / 2
        dx, dy = tx - cx, ty - cy
        if dx == 0 and dy == 0:
            return cx, cy
        sx = (n["w"] / 2) / abs(dx) if dx else 1e9
        sy = (n["h"] / 2) / abs(dy) if dy else 1e9
        s = min(sx, sy)
        return cx + dx * s, cy + dy * s

    def to_png(self, path, scale=2):
        S = scale
        img = Image.new("RGB", (self.W * S, self.H * S), self.bg)
        d = ImageDraw.Draw(img)

        def dash_line(p1, p2, color, width, dashed):
            x1, y1, x2, y2 = [v * S for v in (*p1, *p2)]
            if not dashed:
                d.line((x1, y1, x2, y2), fill=color, width=max(1, int(width * S)))
                return
            L = math.hypot(x2 - x1, y2 - y1)
            if L == 0:
                return
            ux, uy = (x2 - x1) / L, (y2 - y1) / L
            pos = 0
            while pos < L:
                e = min(pos + 8 * S, L)
                d.line((x1 + ux * pos, y1 + uy * pos, x1 + ux * e, y1 + uy * e), fill=color,
                       width=max(1, int(width * S)))
                pos += 13 * S

        def draw_node(n):
            x, y, w, h = n["x"] * S, n["y"] * S, n["w"] * S, n["h"] * S
            if n["shape"] != "text":
                fill = n["fill"] or None
                stroke = n["stroke"] or None
                r = 8 * S if n["rounded"] else 0
                if n["shape"] == "cylinder":
                    d.rectangle((x, y + 8 * S, x + w, y + h - 8 * S), fill=fill, outline=stroke)
                    d.ellipse((x, y, x + w, y + 16 * S), fill=fill, outline=stroke)
                    d.ellipse((x, y + h - 16 * S, x + w, y + h), fill=fill, outline=stroke)
                    d.rectangle((x + 2, y + 8 * S, x + w - 2, y + h - 8 * S), fill=fill)
                elif n["shape"] == "chevron":
                    o = 18 * S
                    d.polygon([(x, y), (x + w - o, y), (x + w, y + h / 2), (x + w - o, y + h), (x, y + h),
                               (x + o, y + h / 2)], fill=fill, outline=stroke)
                elif n["dashed"] and n["kind"] == "group":
                    if fill:
                        d.rounded_rectangle((x, y, x + w, y + h), radius=r // 2, fill=fill)
                    for (a, b, c, e) in [(x, y, x + w, y), (x + w, y, x + w, y + h),
                                         (x + w, y + h, x, y + h), (x, y + h, x, y)]:
                        dash_line((a / S, b / S), (c / S, e / S), stroke, 1.2, True)
                else:
                    d.rounded_rectangle((x, y, x + w, y + h), radius=r, fill=fill, outline=stroke,
                                        width=int(1.3 * S))
            if not n["text"]:
                return
            size, lines = layout_text(n["text"], n["w"], n["h"], n["size"], n["bold_first"], n["bold"])
            lh = size * 1.25 * S
            total = lh * len(lines)
            ty = y + 6 * S if n["valign"] == "top" else y + (h - total) / 2
            for i, (ln, b) in enumerate(lines):
                f = font(size * S, b)
                tw = f.getlength(ln)
                if n["align"] == "center":
                    tx = x + (w - tw) / 2
                elif n["align"] == "left":
                    tx = x + 8 * S
                else:
                    tx = x + w - tw - 8 * S
                d.text((tx, ty + i * lh), ln, font=f, fill=n["color"])

        for g in self.groups:
            draw_node(g)
        for b in self.boxes:
            draw_node(b)
        for l in self.lines:
            dash_line(l["p"][:2], l["p"][2:], l["color"], l["width"], l["dashed"])
        labels = []
        for e in self.edges:
            A, B = self.nodes[e["a"]], self.nodes[e["b"]]
            via = e["via"]
            first_t = via[0] if via else (B["x"] + B["w"] / 2, B["y"] + B["h"] / 2)
            last_s = via[-1] if via else (A["x"] + A["w"] / 2, A["y"] + A["h"] / 2)
            p0 = self._border_point(A, *first_t)
            p1 = self._border_point(B, *last_s)
            pts = [p0] + list(via) + [p1]
            for i in range(len(pts) - 1):
                dash_line(pts[i], pts[i + 1], e["color"], e["width"], e["dashed"])

            def arrow(tip, frm, color=e["color"]):
                ang = math.atan2(tip[1] - frm[1], tip[0] - frm[0])
                L = 10 * S
                a1 = (tip[0] * S - L * math.cos(ang - 0.4), tip[1] * S - L * math.sin(ang - 0.4))
                a2 = (tip[0] * S - L * math.cos(ang + 0.4), tip[1] * S - L * math.sin(ang + 0.4))
                d.polygon([(tip[0] * S, tip[1] * S), a1, a2], fill=color)
            arrow(pts[-1], pts[-2])
            if e["bidir"]:
                arrow(pts[0], pts[1])
            if e["label"]:
                best = max(range(len(pts) - 1),
                           key=lambda i: math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]))
                mx, my = (pts[best][0] + pts[best + 1][0]) / 2, (pts[best][1] + pts[best + 1][1]) / 2
                labels.append((mx, my, e["label"], e["size"]))
        for mx, my, lab, sz in labels:
            f = font(sz * S)
            ls = []
            for par in lab.split("\n"):
                ls += wrap_par(par, f, 170 * S)
            wmax = max(f.getlength(x) for x in ls)
            hh = len(ls) * sz * 1.25 * S
            x0, y0 = mx * S - wmax / 2 - 3 * S, my * S - hh / 2 - 2 * S
            d.rectangle((x0, y0, x0 + wmax + 6 * S, y0 + hh + 4 * S), fill="#ffffff")
            for i, ln in enumerate(ls):
                d.text((mx * S - f.getlength(ln) / 2, y0 + 2 * S + i * sz * 1.25 * S), ln, font=f, fill="#222222")
        img.save(path)

    def save(self, folder, basename):
        os.makedirs(folder, exist_ok=True)
        self.to_drawio(os.path.join(folder, basename + ".drawio"))
        self.to_png(os.path.join(folder, basename + ".png"))
