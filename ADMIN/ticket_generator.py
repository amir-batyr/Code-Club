#!/usr/bin/env python3
"""Generate printable, numbered, snake-themed club tickets: 10 per A4 page.

Examples:
    python ticket_generator.py
    python ticket_generator.py --club "Coding Club" --day "Thursday" \
        --time "3:30pm" --room "Room 12" --count 30
    python ticket_generator.py --count 25 --start 101 --qr https://example.com/join

Output: tickets.pdf (change with --out). If --count is not a multiple of 10,
the last page is only partly filled. Needs: pip install reportlab
"""
import argparse
import math

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

# ---- DEFAULTS (or pass them on the command line) -----------------------------
CLUB = "[CLUB NAME]"
TITLE = "Build Your Own Snake Game"
DAY = "[DAY]"
TIME = "[TIME]"
ROOM = "[ROOM]"
# -----------------------------------------------------------------------------

PAGE_W, PAGE_H = A4
COLS, ROWS = 2, 5
TW, TH = 95 * mm, 54 * mm          # ticket size
STUB = 22 * mm                     # tear-off stub width
MW = TW - STUB                     # main part width
MARGIN_X = (PAGE_W - COLS * TW) / 2
MARGIN_Y = (PAGE_H - ROWS * TH) / 2
PER_PAGE = COLS * ROWS

DARK = colors.HexColor("#0C140F")
LIME = colors.HexColor("#8BFF5A")
PAPER = colors.HexColor("#F3F8F3")
INK = colors.HexColor("#14211A")
MUTED = colors.HexColor("#4C6354")
LINE = colors.HexColor("#7A9A82")
SNAKE = colors.HexColor("#2E7D32")
HEAD = colors.HexColor("#1B5E20")
FOOD = colors.HexColor("#E53935")


def draw_qr(c, url, x, y, size):
    widget = qr.QrCodeWidget(url)
    x0, y0, x1, y1 = widget.getBounds()
    d = Drawing(size, size, transform=[size / (x1 - x0), 0, 0, size / (y1 - y0), 0, 0])
    d.add(widget)
    renderPDF.draw(d, c, x, y)


def draw_ticket(c, x, y, label, cfg):
    # background and dashed cut line
    c.setFillColor(PAPER)
    c.rect(x, y, TW, TH, stroke=0, fill=1)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.setDash(2, 2)
    c.rect(x, y, TW, TH, stroke=1, fill=0)
    c.line(x + MW, y, x + MW, y + TH)          # perforation before the stub
    c.setDash()

    # header band
    band = 9 * mm
    c.setFillColor(DARK)
    c.rect(x, y + TH - band, MW, band, stroke=0, fill=1)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(LIME)
    c.drawString(x + 5 * mm, y + TH - 5.8 * mm, cfg.club)
    c.setFillColor(colors.HexColor("#E8F3EA"))
    c.drawRightString(x + MW - 5 * mm, y + TH - 5.8 * mm, "ADMIT ONE")

    # title (up to two lines)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 14)
    lines = simpleSplit(cfg.title, "Helvetica-Bold", 14, MW - 10 * mm)[:2]
    ty = y + TH - band - 7.5 * mm
    for line in lines:
        c.drawString(x + 5 * mm, ty, line)
        ty -= 5.6 * mm

    # the snake: five body segments, a head, and something to eat
    sx, sy, seg, gap = x + 5 * mm, y + 22.5 * mm, 3.6 * mm, 0.8 * mm
    c.setFillColor(SNAKE)
    for i in range(5):
        c.rect(sx + i * (seg + gap), sy, seg, seg, stroke=0, fill=1)
    hx = sx + 5 * (seg + gap)
    c.setFillColor(HEAD)
    c.rect(hx, sy, seg, seg, stroke=0, fill=1)
    c.setFillColor(FOOD)
    c.circle(hx + seg + 3.5 * mm + seg / 2, sy + seg / 2, seg / 2, stroke=0, fill=1)

    # when and where
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x + 5 * mm, y + 14 * mm, f"{cfg.day}  |  {cfg.time}")
    c.setFont("Helvetica", 10)
    c.drawString(x + 5 * mm, y + 9 * mm, cfg.room)

    if cfg.qr:
        draw_qr(c, cfg.qr, x + MW - 5 * mm - 18 * mm, y + 4 * mm, 18 * mm)

    # stub
    cx = x + MW + STUB / 2
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 6.5)
    c.drawCentredString(cx, y + TH - 12 * mm, "No.")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(cx, y + TH / 2 - 3 * mm, label)
    c.setFont("Helvetica", 7)
    c.drawCentredString(cx, y + 12 * mm, "Bring")
    c.drawCentredString(cx, y + 8.5 * mm, "a friend")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--club", default=CLUB)
    ap.add_argument("--title", default=TITLE)
    ap.add_argument("--day", default=DAY)
    ap.add_argument("--time", default=TIME)
    ap.add_argument("--room", default=ROOM)
    ap.add_argument("--count", type=int, default=PER_PAGE,
                    help="number of tickets (default 10 = one page)")
    ap.add_argument("--start", type=int, default=1, help="first ticket number")
    ap.add_argument("--qr", default="", help="optional URL to print as a QR code")
    ap.add_argument("--out", default="tickets.pdf")
    cfg = ap.parse_args()

    if cfg.count < 1:
        raise SystemExit("--count must be at least 1")

    width = max(2, len(str(cfg.start + cfg.count - 1)))
    pages = math.ceil(cfg.count / PER_PAGE)

    c = canvas.Canvas(cfg.out, pagesize=A4)
    c.setTitle("Club tickets")
    n = 0
    for _ in range(pages):
        for slot in range(PER_PAGE):
            if n >= cfg.count:
                break
            col, row = slot % COLS, slot // COLS
            x = MARGIN_X + col * TW
            y = PAGE_H - MARGIN_Y - (row + 1) * TH
            draw_ticket(c, x, y, str(cfg.start + n).zfill(width), cfg)
            n += 1
        c.setFont("Helvetica", 7)
        c.setFillColor(MUTED)
        c.drawCentredString(PAGE_W / 2, 6 * mm, "Cut along the dashed lines.")
        c.showPage()
    c.save()
    print(f"{cfg.count} tickets on {pages} page(s) -> {cfg.out}")


if __name__ == "__main__":
    main()
