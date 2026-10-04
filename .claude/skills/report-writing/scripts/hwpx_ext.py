"""HWPX 생성 확장: 표지·목차·대제목·쪽나눔·AS-IS/TO-BE 표·간트표 (9번 종합보고서 서식용)
사용: from hwpx_ext import *  → ops 리스트를 만든 뒤 gen.save(경로, ops)
"""
import sys, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hwpx_lib as gen
from hwpx_lib import P, W, esc, _id

# ---- 추가 글자/문단 모양 -------------------------------------------------
gen.CHARS += [(3200, 1, 0),   # 11 표지 제목
              (1800, 1, 0),   # 12 대제목(Ⅰ.)
              (2000, 1, 0),   # 13 표지 기관명
              (1300, 2, 0)]   # 14 표 안 작은 글씨
gen.PARAS += [('CENTER', 0, 0, 0, 160, 1),     # 12 가운데 + 쪽나눔
              ('LEFT', 0, 0, 0, 180, 1),       # 13 대제목 + 쪽나눔
              ('LEFT', 0, 0, 1500, 180, 1),    # 14 대제목(쪽나눔 없음)
              ('CENTER', 0, 0, 3000, 160, 1)]  # 15 가운데 + 위 간격

_orig_header = gen.header
def header():
    h = _orig_header()
    for pid in (12, 13):
        m = re.search(r'<hh:paraPr id="%d".*?</hh:paraPr>' % pid, h, re.S)
        blk = m.group(0).replace('pageBreakBefore="0"', 'pageBreakBefore="1"')
        h = h.replace(m.group(0), blk)
    return h
gen.header = header

# ---- 셀 안에 여러 줄/칸별 모양을 쓸 수 있는 표 -----------------------------
def tbl2(rows, widths, bfs, height=1500):
    gen._id[0] += 1
    x = (f'<hp:tbl id="{gen._id[0]}" zOrder="0" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" '
         f'pageBreak="CELL" repeatHeader="0" rowCnt="{len(rows)}" colCnt="{len(widths)}" cellSpacing="0" borderFillIDRef="1" noShading="0">'
         f'<hp:sz width="{sum(widths)}" widthRelTo="ABSOLUTE" height="{height*len(rows)}" heightRelTo="ABSOLUTE" protect="0"/>'
         '<hp:pos treatAsChar="0" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
         '<hp:outMargin left="0" right="0" top="0" bottom="0"/><hp:inMargin left="510" right="510" top="141" bottom="141"/>')
    for r, row in enumerate(rows):
        x += '<hp:tr>'
        for c, t in enumerate(row):
            b, pp, cp = bfs(r, c)
            paras = ''.join(P(line, pp, cp) for line in str(t).split('\n'))
            x += (f'<hp:tc name="" header="0" hasMargin="0" protect="0" editable="1" dirty="0" borderFillIDRef="{b}">'
                  '<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">'
                  + paras + '</hp:subList>'
                  f'<hp:cellAddr colAddr="{c}" rowAddr="{r}"/><hp:cellSpan colSpan="1" rowSpan="1"/><hp:cellSz width="{widths[c]}" height="{height}"/>'
                  '<hp:cellMargin left="141" right="141" top="141" bottom="141"/></hp:tc>')
        x += '</hp:tr>'
    return '<hp:p paraPrIDRef="0" styleIDRef="0"><hp:run charPrIDRef="0">' + x + '</hp:tbl></hp:run></hp:p>'

def scale(ws, total=W):
    t = sum(ws)
    return [round(w * total / t) for w in ws]

HEAD, LEFT, CEN = 8, 8, 7   # (charPr 8 = 표 머리 굵게)

def grid(rows, ws, first_col_head=True, small=False):
    cp = 14 if small else 7
    return tbl2(rows, scale(ws),
                lambda r, c: (5 if (r == 0 or (first_col_head and c == 0)) else 4,
                              7 if (r == 0 or c == 0) else 8,
                              8 if (r == 0 or (first_col_head and c == 0)) else cp))

_orig_body = gen.body
def body(ops):
    out = ''
    for op in ops:
        k = op[0]; a = op[1] if len(op) > 1 else None
        if k == 'approval':
            out += tbl2(a, scale([2, 2, 2, 2]), lambda r, c: (5 if r == 0 else 4, 7, 8 if r == 0 else 7), 1800)
        elif k == 'space':    out += P('', 11, 9) * a
        elif k == 'ctitle':   out += P(a, 1, 11)
        elif k == 'csub':     out += P(a, 1, 3)
        elif k == 'corg':     out += P(a, 15, 13)
        elif k == 'sumsub':   out += P(a, 12, 3)
        elif k == 'tochead':  out += P(a, 12, 11)
        elif k == 'h1pb':     out += P(a, 13, 12)
        elif k == 'h1':       out += P(a, 14, 12)
        elif k == 'conclude': out += tbl2([[a]], [W], lambda r, c: (5, 1, 1), 1500)
        elif k == 'grid':     out += grid(a, op[2], True)
        elif k == 'grid_nohead': out += grid(a, op[2], False)
        elif k == 'gantt':
            rows, ws, marks = a, op[2], op[3]
            out += tbl2(rows, scale(ws), lambda r, c: (5 if (r == 0 or c == 0 or (r, c) in marks) else 4, 7 if (r == 0 or 0 < c < len(ws) - 1) else 8, 8 if (r == 0 or c == 0) else 7))
        elif k == 'toc':
            out += tbl2(a, scale([1]), lambda r, c: (1, 8, 0), 1700)
        else:
            out += _orig_body([op])
    return out
gen.body = body

