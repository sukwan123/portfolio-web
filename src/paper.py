# -*- coding: utf-8 -*-
"""제출용 이력서·자기소개서를 A4 PDF 로 굽는다.

    python3 src/paper.py                      # _paper/ 에 html 과 pdf
    SITE_URL=https://... python3 src/paper.py # 링크 주소를 박아 넣는다

웹 포트폴리오와 같은 내용을 쓰되, 종이에서 읽는 순서로 다시 세운다. 문서 안의
링크는 전부 눌러서 웹 문서로 넘어가게 둔다 — 이력서는 요약이고, 근거는 웹에 있다.

_paper/ 는 .gitignore 의 `_*/` 에 걸려 저장소에 올라가지 않는다. 특정 회사에
내려고 만든 개인 문서라 공개 저장소에 둘 이유가 없다.
"""
import html
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content as C                                        # noqa: E402
from build import dur_text, months_since                   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "_paper")
SITE = os.environ.get("SITE_URL", "").rstrip("/")
COMPANY = os.environ.get("COMPANY", "")


def e(s):
    return html.escape(str(s), quote=True)


def strip(s):
    return re.sub(r"<[^>]+>", "", str(s))


def link(page, label):
    """웹 문서로 나가는 링크. 주소를 아직 모르면 자리만 표시한다."""
    if not SITE:
        return '<span class="ln pend">%s</span>' % e(label)
    return '<a class="ln" href="%s/%s">%s</a>' % (SITE, page, e(label))


CAREER = dur_text(months_since(C.SITE["career_start"]))

CSS = """
@page { size: A4; margin: 16mm 15mm 14mm; }
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'NanumGothic',sans-serif;font-size:10pt;line-height:1.62;color:#14171C;
  word-break:keep-all}
a{color:inherit}
.ln{color:#6E4F27;text-decoration:none;border-bottom:.5pt solid #C9B48E;white-space:nowrap}
.ln::after{content:" \\2197";font-size:7.5pt}
.pend{color:#8E959E;border-bottom-style:dotted}

header{border-bottom:1.6pt solid #14171C;padding-bottom:9pt;margin-bottom:14pt}
h1{font-size:21pt;letter-spacing:-.02em;display:inline-block}
h1 small{font-size:10pt;font-weight:400;color:#6B727B;margin-left:8pt;letter-spacing:.02em}
.role{margin-top:3pt;font-size:10.5pt;color:#3C434B;font-weight:700}
.meta{margin-top:7pt;font-size:9pt;color:#4A5159}
.meta b{font-weight:700;color:#14171C}

h2{font-size:10.5pt;letter-spacing:.02em;margin:15pt 0 7pt;padding-bottom:3pt;
  border-bottom:.8pt solid #C7CCD3;color:#14171C}
h2:first-of-type{margin-top:0}
h3{font-size:10.5pt;margin:13pt 0 4pt;color:#14171C}
p{margin-bottom:6pt}
.lede{font-size:11pt;font-weight:700;line-height:1.55;margin-bottom:7pt}

.tiles{display:flex;gap:0;border:.8pt solid #C7CCD3;margin-bottom:4pt}
.tile{flex:1;padding:7pt 9pt;border-right:.8pt solid #C7CCD3}
.tile:last-child{border-right:0}
.tile b{display:block;font-size:14pt;letter-spacing:-.02em}
.tile span{font-size:8pt;color:#5A616A}

table{width:100%;border-collapse:collapse}
td{padding:5pt 0;vertical-align:top;border-bottom:.5pt solid #E1E5EA}
tr:last-child td{border-bottom:0}
td.when{width:26%;font-size:8.5pt;color:#4A5159;padding-right:8pt}
td.when b{display:block;font-size:9.5pt;color:#14171C}
td.what b{font-size:10.5pt}
td.what div{font-size:9pt;color:#4A5159;margin-top:1pt}
td.k{width:19%;font-size:9pt;font-weight:700;padding-right:8pt}
td.v{font-size:9pt;color:#3C434B}

ul{list-style:none}
li{position:relative;padding-left:9pt;margin-bottom:3pt;font-size:9.5pt}
li::before{content:"";position:absolute;left:0;top:6.5pt;width:3pt;height:3pt;
  background:#8A6636;border-radius:50%}
.kw{font-size:9pt;color:#3C434B}
.kw b{color:#14171C}

.sig{margin-top:16pt;padding-top:8pt;border-top:.8pt solid #C7CCD3;
  font-size:8.5pt;color:#6B727B;display:flex;justify-content:space-between}
.note{margin-top:10pt;padding:8pt 10pt;background:#F4F1EA;border-left:2pt solid #8A6636;
  font-size:9pt;color:#3C434B}
"""


def page(title, body):
    return ("<!doctype html><html lang=\"ko\"><head><meta charset=\"utf-8\">"
            "<title>%s</title><style>%s</style></head><body>%s"
            "<div class=\"sig\"><span>%s · 레벨 디자이너</span><span>%s</span></div>"
            "</body></html>") % (e(title), CSS, body, e(C.SITE["name"]),
                                 e(C.SITE["updated"]))


def header(doc_name):
    site = ('<b>포트폴리오</b> %s' % link("index.html", SITE.replace("https://", "")
                                      if SITE else "웹 포트폴리오"))
    return ('<header><h1>%s<small>%s</small></h1>'
            '<div class="role">레벨 디자이너 · %s</div>'
            '<div class="meta"><b>%s</b> · <b>%s</b><br>%s</div></header>'
            % (e(C.SITE["name"]), e(doc_name), e(CAREER),
               e(C.SITE["email"]), e(C.SITE["tel"]), site))


# ─────────────────────────────────────────────────────────────── 이력서
PAGES = {p["slug"]: p.get("page") for p in C.PROJECTS}
CAREER_LINK = {
    "왕좌의 게임: 킹스로드": ("kingsroad.html", "담당 콘텐츠 10종"),
    "Project ZETA": ("p-zeta.html", "상세"),
    "나노레전드 · 미니막스 타이니버스": ("p-nanolegend.html", "상세"),
    "Project KUFC": ("p-kufc.html", "상세"),
    "Kingdom Under Fire 2": ("p-kuf2.html", "상세"),
}


def resume():
    b = [header("이력서")]

    b.append('<h2>요약</h2>')
    b.append('<p class="lede">%s</p>' % e(C.HOME["lede"]))
    b.append('<p>%s</p>' % C.HOME["sub"].replace("{{career}}", "<b>%s</b>" % CAREER))

    tiles = "".join('<div class="tile"><b>%s</b><span>%s</span></div>'
                    % (e(CAREER if "{{" in n else n), e(lab))
                    for n, lab in C.HOME["stats"])
    b.append('<div class="tiles">%s</div>' % tiles)

    b.append('<h2>경력</h2><table>')
    for when, co, title, pos in C.HOME["career"]:
        ln = CAREER_LINK.get(title)
        more = ('<br>%s' % link(ln[0], ln[1])) if ln else ""
        b.append('<tr><td class="when"><b>%s</b>%s</td>'
                 '<td class="what"><b>%s</b><div>%s%s</div></td></tr>'
                 % (e(co), e(when), e(title), pos, more))
    b.append('</table>')

    b.append('<h2>보유 기술</h2><table>')
    for k, v in C.HOME["skills"]:
        b.append('<tr><td class="k">%s</td><td class="v">%s</td></tr>' % (e(k), v))
    b.append('</table>')

    b.append('<h2>개인 작업</h2><table>')
    for w in C.PERSONAL["own"]:
        if w.get("draft"):
            continue
        b.append('<tr><td class="k">%s</td><td class="v"><b>%s</b> — %s<br>%s</td></tr>'
                 % (e(w["year"]), e(w["title"]), strip(w["meta"]),
                    link(w["page"], "웹에서 보기")))
    b.append('</table>')

    b.append('<h2>학력 · 기타</h2><table>')
    for k, v in C.HOME["edu"]:
        b.append('<tr><td class="k">%s</td><td class="v">%s</td></tr>' % (e(k), v))
    b.append('<tr><td class="k">업계 외</td><td class="v kw">%s</td></tr>'
             % " · ".join(C.HOME["offindustry"]))
    b.append('</table>')
    return page("손석완 이력서", "".join(b))


# ─────────────────────────────────────────────────────── 자기소개서
def letter():
    co = COMPANY or "귀사"
    b = [header("자기소개서")]

    b.append('<h2>레벨에 필요한 모든 것을 직접 만듭니다</h2>')
    b.append('<p>공간을 설계하는 데서 멈추지 않습니다. 시나리오 · 기믹 · PC와 몬스터의 액션 · '
             '각종 연출까지, 그 레벨에 담길 것을 함께 기획합니다. 레벨은 결국 유저가 마지막에 '
             '겪는 경험이고, 그 경험을 이루는 재료를 남에게 맡겨 두면 의도한 대로 서지 않기 '
             '때문입니다.</p>')
    b.append('<p>범위를 넓혀 본 경험도 있습니다. <b>나노레전드</b>에서는 팀 내 유일한 기획자로 '
             '전투를 제외한 전 영역 — 인게임 · 아웃게임 · BM · 운영 — 을 전담했고, 출시와 '
             '라이브, 서비스 종료까지 겪었습니다. 지표를 보고 콘텐츠를 고치는 감각은 그때 '
             '생겼습니다. 현재 넷마블네오에서는 <b>왕좌의 게임: 킹스로드</b>의 필드 지역과 '
             '던전을 맡아 프로토타입 직후부터 글로벌 출시와 라이브 서비스까지 같은 프로젝트를 '
             '이어오고 있습니다.</p>')
    b.append('<p class="kw">담당한 지역과 던전, 그때 쓴 평면도와 목업: %s</p>'
             % link("kingsroad.html", "왕좌의 게임: 킹스로드"))

    b.append('<h2>감으로 정하지 않고, 재서 정합니다</h2>')
    b.append('<p>“이게 더 재미있다”는 말은 근거가 되지 못한다고 생각합니다. 개인 작업으로 만들고 '
             '있는 웹 게임에서 “그래프가 느리다”는 지적을 받았을 때, 변동성을 올려 푸는 대신 '
             '체감 속도를 만드는 요소를 축 · 스케일 · 틱 주기 셋으로 갈라 각각 쟀습니다. 범인은 '
             '변동성이 아니라 <b>x축의 시간 폭</b>이었습니다.</p>')
    b.append('<p>재고 나서 버린 것도 있습니다. 수집형 가챠를 등급 · 확률 공시 · 합성까지 다 만들고 '
             '20만 회를 돌려 공시 확률과 실제를 대조한 뒤에 통째로 걷어냈습니다. 그 게임이 '
             '목표하는 것은 수집이 아니라 <b>애착</b>이었고, 사람이 많아질수록 한 명당 분량이 '
             '얇아져 목표와 어긋났기 때문입니다. 공들여 만든 것을 버리는 판단도 설계의 일부라고 '
             '봅니다.</p>')
    b.append('<p class="kw">그 과정을 정리한 문서: %s</p>'
             % link("pw-maedonyeo.html", "개인 작품 · 매도녀"))

    b.append('<h2>AI를 실무 파이프라인으로 올립니다</h2>')
    b.append('<p>레벨 디자이너가 시간을 가장 많이 쓰는 일은 목업 제작이고, 만든 목업이 재미 검증에서 '
             '탈락하면 고치는 데 처음보다 더 걸립니다. 그래서 평면도 제작 툴을 직접 만들어 언리얼 '
             'LLM 플러그인 Aura와 연결했습니다. <b>목업 제작 시간을 31% 줄였고</b>, Meshy AI로 '
             '뽑은 메시를 밑그림으로 쓰는 제작법으로는 <b>효율을 50% 이상</b> 올렸습니다. 언리얼 '
             '에디터의 반복 작업은 MCP를 연결해 스크립트 한 번으로 처리합니다.</p>')
    b.append('<p>도구를 만드는 것 자체가 목적은 아닙니다. 같은 시간에 <b>검증을 몇 번 더 돌릴 수 '
             '있느냐</b>가 레벨의 완성도를 정하기 때문에, 앞단을 기계에 넘기고 사람은 판단에 '
             '남는 구조를 만드는 것이 목적입니다.</p>')
    b.append('<p class="kw">파이프라인 구성과 실측치: %s</p>'
             % link("aura.html", "AI 목업 파이프라인"))

    b.append('<h2>연출이 강한 레벨을 만듭니다</h2>')
    b.append('<p>영화를 전공하고 시나리오 작가로 일했습니다. 지금도 오디오드라마를 집필 · 연출 · '
             '제작하며 작품 활동을 이어가고 있습니다. 그래서 공간을 세울 때 정보를 어디에 놓고 '
             '시선을 어디로 끌지를 먼저 생각합니다. <b>환경 스토리텔링, 시선 유도, 컷신 연출</b>로 '
             '설명 없이 전달하는 레벨에 특화되어 있습니다.</p>')
    b.append('<p>레벨에 필요한 시스템을 직접 기획하는 것도 같은 이유입니다. 첫 던전을 단독으로 맡았을 '
             '때 레벨 기획과 함께 그 던전에 필요한 기능까지 설계했고, 기획 의도를 전달하는 인게임 '
             '장치도 직접 만들었습니다.</p>')

    b.append('<h2>지원 동기</h2>')
    b.append('<p>%s</p>' % C.HOME["contact_p"].replace("<br>", " "))
    if COMPANY:
        b.append('<p><b>%s</b>에 지원하는 이유도 같습니다. 만들려는 경험이 분명한 팀에서, 그 경험을 '
                 '공간으로 옮기는 일을 맡고 싶습니다. 지금까지 맡아 온 필드와 던전, 그리고 회사 밖에서 '
                 '혼자 끝까지 만들어 본 게임들이 그 준비 과정이었다고 생각합니다.</p>' % e(co))
    else:
        b.append('<p>만들려는 경험이 분명한 팀에서, 그 경험을 공간으로 옮기는 일을 맡고 싶습니다. '
                 '지금까지 맡아 온 필드와 던전, 그리고 회사 밖에서 혼자 끝까지 만들어 본 게임들이 '
                 '그 준비 과정이었다고 생각합니다.</p>')
    b.append('<div class="note">이 문서에 적은 내용의 근거 — 담당 레벨의 평면도와 목업, 실제 플레이 '
             '영상, 개인 작업의 기획서는 웹 포트폴리오에 있습니다. %s · %s · %s</div>'
             % (link("index.html", "홈"), link("index.html#projects", "프로젝트"),
                link("personal.html", "개인 작품")))
    return page("손석완 자기소개서", "".join(b))


def main():
    os.makedirs(OUT, exist_ok=True)
    made = [("이력서", "resume.html", resume()), ("자기소개서", "letter.html", letter())]
    for name, fn, text in made:
        p = os.path.join(OUT, fn)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        print("%-6s %s" % (name, p))
    if not SITE:
        print("\nSITE_URL 이 없어 링크 자리를 회색으로 비워 뒀다."
              "\n    SITE_URL=https://... python3 src/paper.py")
    subprocess.run([sys.executable, os.path.join(ROOT, "src", "topdf.py")], check=True)


if __name__ == "__main__":
    main()
