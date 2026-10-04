import zipfile, os, sys
from xml.sax.saxutils import escape as esc

FONTS = ['휴먼명조', 'HY헤드라인M', 'HY중고딕', '맑은 고딕']
LANGS = ['HANGUL','LATIN','HANJA','JAPANESE','OTHER','SYMBOL','USER']

def fontfaces():
    out = f'<hh:fontfaces itemCnt="{len(LANGS)}">'
    for l in LANGS:
        out += f'<hh:fontface lang="{l}" fontCnt="{len(FONTS)}">'
        for i, f in enumerate(FONTS):
            out += (f'<hh:font id="{i}" face="{f}" type="TTF" isEmbedded="0"><hh:typeInfo familyType="FCAT_MYUNGJO" '
                    'weight="6" proportion="4" contrast="0" strokeVariation="1" armStyle="1" letterform="1" midline="1" xHeight="1"/></hh:font>')
        out += '</hh:fontface>'
    return out + '</hh:fontfaces>'

def bf(i, l, r, t, b, fill=None):
    def side(tag, spec):
        typ, w = spec
        return f'<hh:{tag} type="{typ}" width="{w}" color="#000000"/>'
    s = (f'<hh:borderFill id="{i}" threeD="0" shadow="0" centerLine="NONE" breakCellSeparateLine="0">'
         '<hh:slash type="NONE" Crooked="0" isCounter="0"/><hh:backSlash type="NONE" Crooked="0" isCounter="0"/>'
         + side('leftBorder', l) + side('rightBorder', r) + side('topBorder', t) + side('bottomBorder', b))
    if fill:
        s += f'<hc:fillBrush><hc:winBrush faceColor="{fill}" hatchColor="#000000" alpha="0"/></hc:fillBrush>'
    return s + '</hh:borderFill>'

NO = ('NONE', '0.1 mm'); S3 = ('SOLID', '0.3 mm'); S1 = ('SOLID', '0.12 mm'); DOT = ('DOT', '0.12 mm')
BORDERS = [bf(1, NO, NO, NO, NO),
           bf(2, S3, S3, S3, S3, '#DAEEF3'),     # 제목 상자
           bf(3, NO, NO, DOT, NO),                 # 개요 상자(위쪽 점선)
           bf(4, S1, S1, S1, S1),                  # 표 칸
           bf(5, S1, S1, S1, S1, '#DAEEF3')]       # 표 머리칸

# (height 1/100pt, font index, bold)
CHARS = [(1500,0,0),(1500,0,1),(2400,1,0),(1600,1,0),(1600,0,1),(1200,2,0),(1500,2,0),(1200,2,0),(1200,2,1),(500,0,0),(1500,1,0)]
def charpr(i, h, f, b):
    bold = ' bold="1"' if b else ''
    return (f'<hh:charPr id="{i}" height="{h}" textColor="#000000" shadeColor="none" useFontSpace="0" useKerning="0" symMark="NONE" borderFillIDRef="1"{bold}>'
            f'<hh:fontRef hangul="{f}" latin="{f}" hanja="{f}" japanese="{f}" other="{f}" symbol="{f}" user="{f}"/>'
            '<hh:ratio hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100"/>'
            '<hh:spacing hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>'
            '<hh:relSz hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100"/>'
            '<hh:offset hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>'
            + ('<hh:bold/>' if b else '') + '</hh:charPr>')

# (align, left, hanging indent, prev, line%, borderFill)
PARAS = [('JUSTIFY',0,0,0,160,1),     #0 본문
         ('CENTER',0,0,0,160,1),      #1 가운데
         ('LEFT',0,0,1500,180,1),     #2 큰 제목
         ('JUSTIFY',3000,1500,500,160,1),   #3 원 항목
         ('JUSTIFY',4500,1500,500,160,1),   #4 하이픈 항목
         ('JUSTIFY',6000,1200,0,130,1),     #5 참고
         ('JUSTIFY',0,0,0,160,3),     #6 개요
         ('CENTER',0,0,0,130,1),      #7 표 가운데
         ('LEFT',0,0,0,130,1),        #8 표 왼쪽
         ('LEFT',0,0,1000,180,1),     #9 작은제목
         ('JUSTIFY',6000,1500,500,160,1),   #10 점 항목
         ('LEFT',0,0,0,100,1)]        #11 빈줄
def parapr(i, a, l, h, p, ls, b):
    return (f'<hh:paraPr id="{i}" tabPrIDRef="0" condense="0" fontLineHeight="0" snapToGrid="0" suppressLineNumbers="0" checked="0" textDir="AUTO">'
            f'<hh:align horizontal="{a}" vertical="BASELINE"/><hh:heading type="NONE" idRef="0" level="0"/>'
            '<hh:breakSetting breakLatinWord="KEEP_WORD" breakNonLatinWord="BREAK_WORD" widowOrphan="0" keepWithNext="0" keepLines="0" pageBreakBefore="0" lineWrap="BREAK"/>'
            '<hh:autoSpacing eAsianEng="0" eAsianNum="0"/>'
            f'<hh:margin><hc:intent value="{-h}" unit="HWPUNIT"/><hc:left value="{l}" unit="HWPUNIT"/><hc:right value="0" unit="HWPUNIT"/>'
            f'<hc:prev value="{p}" unit="HWPUNIT"/><hc:next value="0" unit="HWPUNIT"/></hh:margin>'
            f'<hh:lineSpacing type="PERCENT" value="{ls}"/>'
            f'<hh:border borderFillIDRef="{b}" offsetLeft="0" offsetRight="0" offsetTop="0" offsetBottom="0" connect="0" ignoreMargin="0"/></hh:paraPr>')

def header():
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>'
        '<hh:head xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head" xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph" '
        'xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core" version="1.4" secCnt="1">'
        '<hh:beginNum page="1" footnote="1" endnote="1" pic="1" tbl="1" equation="1"/><hh:refList>'
        + fontfaces()
        + f'<hh:borderFills itemCnt="{len(BORDERS)}">' + ''.join(BORDERS) + '</hh:borderFills>'
        + f'<hh:charProperties itemCnt="{len(CHARS)}">' + ''.join(charpr(i, *c) for i, c in enumerate(CHARS)) + '</hh:charProperties>'
        + f'<hh:paraProperties itemCnt="{len(PARAS)}">' + ''.join(parapr(i, *p) for i, p in enumerate(PARAS)) + '</hh:paraProperties>'
        + '<hh:styles itemCnt="1"><hh:style id="0" type="PARA" name="바탕글" engName="Normal" paraPrIDRef="0" charPrIDRef="0" nextStyleIDRef="0" langID="1042" lockForm="0"/></hh:styles>'
        '</hh:refList><hh:compatibleDocument targetProgram="HWP2018"><hh:layoutCompatibility/></hh:compatibleDocument></hh:head>')

W = 48190   # 본문 폭(HWPUNIT): 210mm - 좌우 20mm
_id = [1000]
def P(text, pp, cp):
    return f'<hp:p paraPrIDRef="{pp}" styleIDRef="0"><hp:run charPrIDRef="{cp}"><hp:t>{esc(text)}</hp:t></hp:run></hp:p>'

def tbl(rows, widths, bfs, height=1500):
    _id[0] += 1
    tw = sum(widths)
    x = (f'<hp:tbl id="{_id[0]}" zOrder="0" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" '
         f'pageBreak="CELL" repeatHeader="0" rowCnt="{len(rows)}" colCnt="{len(widths)}" cellSpacing="0" borderFillIDRef="1" noShading="0">'
         f'<hp:sz width="{tw}" widthRelTo="ABSOLUTE" height="{height*len(rows)}" heightRelTo="ABSOLUTE" protect="0"/>'
         '<hp:pos treatAsChar="0" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
         '<hp:outMargin left="0" right="0" top="0" bottom="0"/><hp:inMargin left="510" right="510" top="141" bottom="141"/>')
    for r, row in enumerate(rows):
        x += '<hp:tr>'
        for c, t in enumerate(row):
            b, pp, cp = bfs(r, c)
            x += (f'<hp:tc name="" header="0" hasMargin="0" protect="0" editable="1" dirty="0" borderFillIDRef="{b}">'
                  '<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">'
                  + P(t, pp, cp) + '</hp:subList>'
                  f'<hp:cellAddr colAddr="{c}" rowAddr="{r}"/><hp:cellSpan colSpan="1" rowSpan="1"/><hp:cellSz width="{widths[c]}" height="{height}"/>'
                  '<hp:cellMargin left="141" right="141" top="141" bottom="141"/></hp:tc>')
        x += '</hp:tr>'
    return '<hp:p paraPrIDRef="0" styleIDRef="0"><hp:run charPrIDRef="0">' + x + '</hp:tbl></hp:run></hp:p>'

def body(ops):
    out = ''
    for op in ops:
        k = op[0]
        a = op[1] if len(op) > 1 else None
        if k == 'title':   out += tbl([[a]], [W], lambda r, c: (2, 1, 2), 3000)
        elif k == 'gap':   out += P('', 11, 9)
        elif k == 'overview': out += tbl([[a]], [W], lambda r, c: (3, 6, 6), 1500)
        elif k == 'big':   out += P('□ ' + a, 2, 3)
        elif k == 'sm':    out += P(a, 9, 4)
        elif k == 'o':     out += P('○ ' + a, 3, 0)
        elif k == 'd':     out += P('- ' + a, 4, 0)
        elif k == 'dot':   out += P('• ' + a, 10, 0)
        elif k == 'n':     out += P('※ ' + a, 5, 5)
        elif k == 'plain': out += P(a, 0, 0)
        elif k == 'right': out += P(a, 1, 0)
        elif k == 'table':
            rows, widths = a, op[2]
            tot = sum(widths); widths = [round(w * W / tot) for w in widths]
            out += tbl(rows, widths, lambda r, c: (5 if r == 0 else 4, 7 if (r == 0 or c == 0) else 8, 8 if r == 0 else 7), 1500)
    return out

SEC = ('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>'
 '<hs:sec xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph">'
 '<hp:p paraPrIDRef="11" styleIDRef="0"><hp:run charPrIDRef="9">'
 '<hp:secPr textDirection="HORIZONTAL" spaceColumns="1134" tabStop="8000" outlineShapeIDRef="1" memoShapeIDRef="0" textVerticalWidthHead="0" masterPageCnt="0">'
 '<hp:grid lineGrid="0" charGrid="0" wonggojiFormat="0"/><hp:startNum pageStartsOn="BOTH" page="0" pic="0" tbl="0" equation="0"/>'
 '<hp:visibility hideFirstHeader="0" hideFirstFooter="0" hideFirstMasterPage="0" border="SHOW_ALL" fill="SHOW_ALL" hideFirstPageNum="0" hideFirstEmptyLine="0" showLineNumber="0"/>'
 '<hp:pagePr landscape="WIDELY" width="59528" height="84188" gutterType="LEFT_ONLY"><hp:margin header="2835" footer="2835" gutter="0" left="5669" right="5669" top="4252" bottom="2835"/></hp:pagePr>'
 '<hp:footNotePr><hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0"/><hp:noteLine length="-1" type="SOLID" width="0.12 mm" color="#000000"/><hp:noteSpacing betweenNotes="283" belowLine="567" aboveLine="850"/><hp:numbering type="CONTINUOUS" newNum="1"/><hp:placement place="EACH_COLUMN" beneathText="0"/></hp:footNotePr>'
 '<hp:endNotePr><hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0"/><hp:noteLine length="14692344" type="SOLID" width="0.12 mm" color="#000000"/><hp:noteSpacing betweenNotes="0" belowLine="567" aboveLine="850"/><hp:numbering type="CONTINUOUS" newNum="1"/><hp:placement place="END_OF_DOCUMENT" beneathText="0"/></hp:endNotePr></hp:secPr>'
 '<hp:ctrl><hp:colPr id="" type="NEWSPAPER" layout="LEFT" colCount="1" sameSz="1" sameGap="0"/></hp:ctrl>'
 '<hp:ctrl><hp:pageNum pos="BOTTOM_CENTER" formatType="DIGIT" sideChar="-"/></hp:ctrl><hp:t></hp:t></hp:run></hp:p>')

HPF = ('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?><opf:package xmlns:opf="http://www.idpf.org/2007/opf/" xmlns:hpf="http://www.hancom.co.kr/schema/2011/hpf" xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head">'
 '<opf:metadata><opf:meta name="generator" content="report-template"/></opf:metadata><opf:manifest>'
 '<opf:item id="header" href="Contents/header.xml" media-type="application/xml"/><opf:item id="section0" href="Contents/section0.xml" media-type="application/xml"/></opf:manifest>'
 '<opf:spine><opf:itemref idref="header" linear="no"/><opf:itemref idref="section0" linear="yes"/></opf:spine></opf:package>')
CONT = ('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?><ocf:container xmlns:ocf="urn:oasis:names:tc:opendocument:xmlns:container" xmlns:hpf="http://www.hancom.co.kr/schema/2011/hpf">'
 '<ocf:rootfiles><ocf:rootfile full-path="Contents/content.hpf" media-type="application/hwpml-package+xml"/></ocf:rootfiles></ocf:container>')

def save(path, ops):
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr(zipfile.ZipInfo('mimetype'), 'application/hwp+zip', zipfile.ZIP_STORED)
        z.writestr('META-INF/container.xml', CONT, zipfile.ZIP_DEFLATED)
        z.writestr('Contents/content.hpf', HPF, zipfile.ZIP_DEFLATED)
        z.writestr('Contents/header.xml', header(), zipfile.ZIP_DEFLATED)
        z.writestr('Contents/section0.xml', SEC + body(ops) + '</hs:sec>', zipfile.ZIP_DEFLATED)

T = lambda t: ('title', t)
OV = lambda t: ('overview', t)
G = ('gap',)
END = [('plain', '붙임  참고자료 1부.  끝.')]

TEMPLATES = {
'1_정책보고서': [T('정책보고서 제목 (20자 이내)'), G, OV('보고 목적과 요청사항을 2~3줄로 작성 (본문에 취지가 있으면 생략)'),
  ('big','사업개요'), ('o','(추진배경) 계기·조건·경과를 한두 줄로 작성 (한 문장 2줄 이내, ~했음)'), ('o','(추진목적) 취지와 필요성'),
  ('n','참고·용어설명·통계 출처'),
  ('big','현황 및 문제점'), ('o','(현황) 수치·고유명사 중심으로 구체적으로'), ('d','세부 내용'), ('o','(문제점·원인) 1차 원인이 아니라 원인의 원인까지 분석'), ('d','타 시·도 및 해외 유사 사례와 효과'),
  ('big','개선방안 및 기대효과'), ('o','(방안) 실행 가능한 방법'), ('o','(기대효과) 정량 효과 우선'),
  ('big','추진계획'), ('o','(일정) 2025. 1. 15.(수) 14:00 형식으로 기재'), ('o','(소요예산) 금1,000,000원(금일백만원)'), ('o','(홍보·점검) 홍보계획과 평가 방법'),
  ('big','행정사항'), ('o','관련 부서 협조사항, 결재권자가 조치할 사항')] + END,
'2_상황보고서': [T('상황보고서 제목 (구체적 사건·결과 중심)'), G, OV('상황을 보고드림 (누가·언제·어디서·무엇을 포함, 생략 가능)'),
  ('big','사업개요'), ('o','핵심 상황 요약 (6하원칙)'),
  ('big','현황(추진경과)'), ('o','구체적 사실관계와 실태, 중요한 사안을 앞에 배열'), ('d','시간 순서 또는 중요도 순서'),
  ('big','문제점 및 원인'), ('o','목표와 현실의 차이'), ('o','차이가 발생한 원인'),
  ('big','해결방안(대응 계획)'), ('o','평가·대책·조치의견'), ('n','결재권자에게 행동방책을 제시하는 경우 실현 가능한 세부 대안 제시'),
  ('big','향후계획'), ('o','후속 조치와 일정')],
'3_검토보고서': [T('검토보고서 제목 (검토 결과가 드러나게)'), G, OV('현안사항 및 검토 결과를 보고드림 (생략 가능)'),
  ('big','사업개요'), ('o','(검토 대상) 용역·계약·사업·요청 내용'),
  ('big','추진배경'), ('o','(배경) 검토를 하게 된 계기·조건·경과'), ('o','(목적) 검토 이유와 필요성'),
  ('big','검토내용'), ('o','(1안) 내용 / 장점 / 단점'), ('o','(2안) 내용 / 장점 / 단점'), ('n','통계, 여론조사, 현장조사 결과 등 입증 자료'),
  ('table', [['구분','1안','2안'],['내용','',''],['장점','',''],['단점','',''],['소요예산','','']], [2,5,5]),
  ('big','검토결과'), ('o','결과와 도출 이유'), ('o','결과에 따른 변화와 기대효과'),
  ('big','향후계획'), ('o','결과 관리·집행 계획')],
'4_회의개최보고서': [T('OO회의 개최 계획'), G, OV('회의에서 공유(의견수렴·의사결정)할 사안을 보고드림 (생략 가능)'),
  ('big','회의개요'), ('o','일시/장소 : 2025. 1. 15.(수) 14:00 / OO회의실'), ('o','주재자 : '), ('o','참석자 : '), ('o','회의목적 : 정보공유 / 의견수렴 / 의사결정'),
  ('big','회의안건'), ('o','안건 1 : 쟁점사항과 기존 논의 경과'), ('d','이해당사자 입장'), ('d','결정 방안별 예상 효과와 문제점'),
  ('big','진행순서'), ('table', [['시간','내용','비고'],['14:00~14:10','개회 및 안건 설명',''],['14:10~15:00','논의',''],['15:00~15:30','결론 정리','']], [3,6,3]),
  ('big','행정사항'), ('o','보안유지 등 유의사항, 예산, 향후계획'), ('plain','붙임  회의자료 1부.  끝.')],
'5_회의결과보고서': [T('OO회의 결과 보고'), G, OV('회의 개최 결과를 보고드림 (생략 가능)'),
  ('big','회의개요'), ('o','일시/장소 : '), ('o','참석자 : '), ('o','회의목적 : '),
  ('big','회의결과'), ('sm','㉮ 안건 1'), ('o','결론 : '), ('o','참석자별 주요 의견'), ('d','OOO : '), ('d','OOO : '),
  ('sm','㉯ 안건 2'), ('o','결론 : '), ('o','참석자별 주요 의견'), ('n','회의록이 아니므로 발언 순서가 아니라 주제별·발언자별로 요약'),
  ('big','향후계획'), ('o','조치가 필요한 사항과 담당·기한'), ('plain','붙임  회의록 1부.  끝.')],
'6_행사보고서': [T('OO행사 계획'), G,
  ('big','행사목적'), ('o','추진배경과 취지 (2~3줄)'), ('o','전달 메시지'),
  ('big','행사개요'), ('o','일시/장소 : '), ('o','주 관 : '), ('o','참석자 : '), ('o','공개 여부 : '),
  ('big','행사내용'), ('o','주요 프로그램'), ('d','세부 내용'), ('o','기대효과'),
  ('big','진행순서'), ('table', [['시간','내용','비고'],['','',''],['','',''],['','','']], [3,6,3]),
  ('big','행정사항'), ('o','관련 부서 협조사항'), ('n','말씀자료, 참석자 프로필, 예상 발언은 별첨으로 처리'), ('plain','붙임  말씀자료 1부.  끝.')],
'7_업무보고(메모보고)': [('table', [['보고선','□시장  □부시장  □실·국장   /   □상황보고  □사전보고  □사후보고'],['대외공개','□공개  □비공개     보도자료  □제공  □미제공     보고일  2025.   .   .'],['보고자','OOO담당관 OOO(0000) / OO담당 OOO(0000) / 주무관 OOO(0000)']], [2,10]),
  G, T('업무보고 제목 (20자 이내)'), G, OV('보고 배경 설명 (2~3줄, 불필요하면 생략). 전체 1장 이내, 현황과 세부자료는 참고자료로 첨부'),
  ('big','사업개요'), ('o','업무의 핵심 내용 (6하원칙)'), ('n','추가설명 필요시 사용'),
  ('big','추진계획'), ('o','일정·방법'),
  ('big','기대효과'), ('o','추진결과와 시사점'),
  ('big','행정사항'), ('o','추가 업무 내용 및 관련 부서 협조사항'),
  ('n','대외공개 : 보고 관련 행사일정·자료 등의 공개 여부 체크 / 보도자료 : 제공 여부 체크')],
'8_보도자료': [('table', [['보도 희망일','2025.   .   .(  ) 즉시','담당부서','OO과'],['작성자','OOO 주무관','연락처','032-000-0000']], [2,4,2,4]),
  G, T('주제목: 눈길을 끄는 카피 (15자 내외)'), ('right','- 부제목: 핵심 내용을 요약해서 전달 -'), G,
  ('plain','리드문(첫 문단): 인천시(시장 OOO)는 [누가·언제·어디서·무엇을·왜] 핵심 내용을 한두 문장 단문으로 쓴다. 제목의 내용을 그대로 반영한다.'),
  ('plain','둘째 문단: 리드문이 약속한 구체 내역(수치·고유명사)을 쓴다. 이 시점에 뉴스가 되는 계기를 밝힌다.'),
  ('plain','본문: 리드문과 가까운 순서로 문단을 배열한다. 배경, 경과, 용어설명은 뒤에 둔다. 문단은 3~4줄, 한 문장에 한 주제만 담는다.'),
  ('plain','인용: OOO 과장은 "전달할 주장 한 가지"라며 "시의 입장에서 강조할 의미·전망·계획"을 밝혔다.'),
  ('n','사진·도표·통계 등 시각 자료 첨부. 형용사·부사·전문용어는 쓰지 않음. 소리 내어 읽으며 퇴고'), ('plain','붙임  사진 1부.  끝.')],
}

if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for name, ops in TEMPLATES.items():
        save(os.path.join(out, name + '.hwpx'), ops)
    print(len(TEMPLATES))
