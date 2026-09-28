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
SITE = os.environ.get("SITE_URL", "https://portfolio-web-production-8817.up.railway.app").rstrip("/")
COMPANY = os.environ.get("COMPANY", "")        # 예: ㈜에이버튼
PROJECT = os.environ.get("PROJECT", "")        # 예: Project EA
POSITION = os.environ.get("POSITION", "레벨 디자이너")


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

.proj{margin-bottom:11pt;break-inside:avoid}
.ph{display:flex;justify-content:space-between;align-items:baseline;gap:8pt}
.ph b{font-size:11pt}
.ph span{font-size:8.5pt;color:#4A5159;white-space:nowrap}
.pg{font-size:8.5pt;color:#6B727B;margin-top:1pt}
.pr{font-size:9pt;color:#3C434B;margin:2pt 0 4pt}
.proj td{padding:3pt 0}
.proj td.k{width:15%;font-size:8.5pt;color:#6E4F27}
.proj td.v{font-size:9pt}
header.hl{border-bottom:1.6pt solid #14171C;padding-bottom:10pt;margin-bottom:14pt}
h1.big{font-size:19pt;line-height:1.3;letter-spacing:-.02em;display:block}
.who{margin-top:6pt;font-size:10pt;color:#3C434B}
.who b{font-size:11pt;color:#14171C}
.note b{color:#14171C}
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


def header(doc_name, career=None):
    site = ('<b>포트폴리오</b> %s' % link("index.html", SITE.replace("https://", "")
                                      if SITE else "웹 포트폴리오"))
    return ('<header><h1>%s<small>%s</small></h1>'
            '<div class="role">레벨 디자이너 · %s</div>'
            '<div class="meta"><b>%s</b> · <b>%s</b><br>%s</div></header>'
            % (e(C.SITE["name"]), e(doc_name), e(career or CAREER),
               e(C.SITE["email"]), e(C.SITE["tel"]), site))


def headline(title, career):
    """자기소개서 머리글. 이 사람을 한 마디로 말하는 제목이 먼저, 이름은 그 아래.
    연락처와 포트폴리오 주소는 여기 두지 않는다 — 맨 아래 한 번이면 된다."""
    return ('<header class="hl"><h1 class="big">%s</h1>'
            '<div class="who"><b>%s</b> · 레벨 디자이너 · %s</div></header>'
            % (title, e(C.SITE["name"]), e(career)))


def contact_note():
    """맨 아래 — 포트폴리오 링크 하나와 연락처."""
    return ('<div class="note">만든 레벨과 플레이 영상은 웹 포트폴리오에 있습니다. %s'
            '<br><b>%s</b> · %s · %s</div>'
            % (link("index.html", SITE.replace("https://", "") if SITE else "웹 포트폴리오"),
               e(C.SITE["name"]), e(C.SITE["email"]), e(C.SITE["tel"])))


# ─────────────────────────────────────────────────────────────── 경력 상세
# 2022.06 경력기술서(엑셀)와 웹 포트폴리오에서 옮겼다. 위일수록 최근이다.
# (회사, 기간, 프로젝트, 장르·플랫폼, 역할, [(분류, 내용)], (웹 문서, 링크 글자))
DETAIL = [
    ("넷마블네오", "2022.08 – 재직 중", "왕좌의 게임: 킹스로드",
     "오픈월드 액션 RPG · PC·모바일 · UE5 · 글로벌 출시 · 라이브",
     "기획팀 레벨디자인 파트 · 프로토타입 직후 합류",
     [("필드", "지역 5곳 레벨디자인 · 목업(블록아웃) — 라스트허스(인트로 튜토리얼) · 올드타운 · "
               "하이가든(1차 · 최종 개정) · 크로우즈네스트(리뉴얼로 전 세트 재제작) · "
               "트윈스(챕터 5, 진행 중)"),
      ("던전", "5종 — 그리핀 던전 <b>단독 전담</b>(레벨 + 기능 기획) · 크라켄(페이즈 동선 · 낙사 "
               "지점) · 장벽너머 일부(목업 9회) · 맘모스(배경팀 전달용 레벨 기획서, 구역 · 치수 "
               "확정, OBJ 목업) · 하렌홀 PvEvP(다층 성채 동선 화이트박스 검증, 목업 1 · 2차)"),
      ("시스템", "레벨에 필요한 기능 · 기믹을 직접 기획해 사양 문서로 확정"),
      ("AI", "평면도 제작 툴 + 언리얼 LLM 플러그인 Aura 목업 파이프라인 — "
             "<b>목업 제작 시간 31% 절감</b>, Meshy 밑그림 방식으로 <b>효율 50% 이상</b>")],
     ("kingsroad.html", "담당 콘텐츠 10종")),
    ("너바나나", "2022.04 – 2022.08", "Project ZETA",
     "AAA 콘솔 액션 PvP · PS5·XBOX · UE5",
     "콘텐츠 기획팀 · 하이컨셉 단계부터 참여",
     [("기초 기획", "기초 룰 · 세계관 · 월드 · 캐릭터 · 핵심 시스템 · 캠페인의 기초 기획"),
      ("시나리오", "시나리오 · 설정 전담"),
      ("레벨", "PvE 컨셉과 메인 모드 레벨디자인 기획 참여")],
     ("p-zeta.html", "상세")),
    ("님블뉴런", "2020.04 – 2022.04", "나노레전드",
     "모바일 캐주얼 RTS · Unity · 자체 글로벌 퍼블리싱",
     "<b>팀 내 유일한 기획자</b> · 전투를 제외한 전 기획 전담 · 개발 시작부터 서비스 종료까지",
     [("성과", "iOS 매출 100위권 · 전략 카테고리 10위 중반권"),
      ("BM · 경제", "구독형 프리미엄 패스 · 패키지 · 가챠 · 광고 시청형 상품, 경제 밸런싱 병행"),
      ("콘텐츠", "튜토리얼 겸 세계관 전달용 PvE '모험' · 이벤트 / 일일 도전 / 레이드 모드"),
      ("시스템", "길드(레이드 · 길드 배틀패스) · 데이터만으로 운영하는 시즌 이벤트 · "
                "아웃게임 튜토리얼 · 운영 시스템 일체"),
      ("시나리오", "세계관 · 캐릭터 설정 · PvE 시나리오와 게임 내 모든 텍스트")],
     ("p-nanolegend.html", "상세")),
    ("님블뉴런", "2019.06 – 2020.04", "미니막스 타이니버스",
     "크로스플랫폼 RTS · PC(스팀)·모바일 · Unity · 자체 글로벌 퍼블리싱",
     "아웃게임 기획 담당 · 알파 버전부터 서비스 종료까지",
     [("BM", "구독형 배틀패스(UI · 데이터 구조 · 임무 · 보상 · 관리) · 상점 구조와 상품 갱신 · "
             "유저 맞춤형 패키지 · 버프"),
      ("시스템", "퀘스트/업적 · 인벤토리 · 우편함 · 덱 저장/복사 · 커스텀 매치 등 일체"),
      ("밸런스", "유닛 성장 · 스탯 밸런싱과 경제 밸런싱"),
      ("시나리오", "기존 러프 시나리오를 구체화해 세계관 · 캐릭터 컨셉 정립")],
     ("p-minimax.html", "상세")),
    ("블루사이드", "2018.06 – 2019.03", "Project KUFC",
     "콘솔 액션 RPG · 자체 엔진",
     "<b>콘텐츠 파트장</b> · 프로토타입부터 참여",
     [("총괄", "전체 콘텐츠 플로우 기획 · 시나리오 · 캐릭터 · 레벨디자인 총괄"),
      ("레벨", "플레이 플로우의 핵심 미션 직접 제작 · 로비 역할의 도시 기획")],
     ("p-kufc.html", "상세")),
    ("블루사이드", "2014.02 – 2018.06", "Kingdom Under Fire 2",
     "MMORPG + RTS · PC·콘솔 · 자체 엔진 · 글로벌 6개국 서비스",
     "레벨디자인 파트 · 레벨 디자이너 · 시나리오 작업 약 1년(파견)",
     [("레이드", "최종 · 최대 규모 레이드 '불꽃의 흉터' 메인 개발 · 소형 레이드 '극한미션' 2종"),
      ("PvP", "최고 인기 PvP 맵 '자유 경기장' · '격전의 도시' · 자유 PvP 매칭 시스템"),
      ("필드 · 월드", "엔드 콘텐츠 PK 필드 · 월드맵과 도시 · 지도를 심리스 방식으로 전환"),
      ("미션", "미션 제작과 폴리싱 · 토벌 모드 맵 4종 · 확장팩 컨셉(설정 · 도시 · 미션 · NPC) 총괄 · "
               "몬스터 밸런싱 · 레벨 사운드"),
      ("시나리오", "메인 시나리오 후반 분기 · 서브 플롯 · <b>퀘스트 약 300개</b> · "
                  "대화형 컷신 40% 직접 제작"),
      ("기타", "중국 · 대만 CBT/OBT 지표 분석과 개선안 보고 · 2014 E3 소니 컨퍼런스 발표 영상 기획")],
     ("p-kuf2.html", "상세")),
]


# ─────────────────────────────────────────────────────────────── 이력서
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
        b.append('<tr><td class="when"><b>%s</b>%s</td>'
                 '<td class="what"><b>%s</b><div>%s</div></td></tr>'
                 % (e(co), e(when), e(title), pos))
    b.append('</table>')

    b.append('<h2>경력 상세</h2>')
    for co, when, title, genre, role, items, ln in DETAIL:
        rows = "".join('<tr><td class="k">%s</td><td class="v">%s</td></tr>' % (e(k), v)
                       for k, v in items)
        b.append('<div class="proj"><div class="ph"><b>%s</b><span>%s · %s</span></div>'
                 '<div class="pg">%s</div><div class="pr">%s · %s</div>'
                 '<table>%s</table></div>'
                 % (e(title), e(co), e(when), e(genre), role, link(ln[0], ln[1]), rows))

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
    """본인이 직접 다듬은 문안(2026.09.28)이 기준이다. 두 절, 570자. 프로젝트 이름은 일부러
    쓰지 않는다 — 이력서와 포트폴리오가 맡는다. 여기서 고친 것은 표기 둘뿐이다."""
    years = months_since(C.SITE["career_start"]) // 12 + 1
    target = " ".join(x for x in (COMPANY, PROJECT) if x)
    b = [headline("모든 것을 알아야 해서,<br>모든 것을 해 본 레벨 디자이너입니다",
                  "%d년 차 (Since %s)" % (years, C.SITE["career_start"][:4]))]

    b.append('<h2>지원 동기</h2>')
    b.append('<p>%s%s 직무에 지원합니다. %d년 동안 주로 실사풍 백뷰 액션 게임을 만들어 왔습니다. '
             '귀사의 프로젝트는 제가 여태껏 열심히 쌓아온 경험이 가장 잘 쓰일 수 있는 곳이라고 '
             '생각했습니다.</p>'
             % (("%s의 " % e(target)) if target else "", e(POSITION), years))

    b.append('<h2>레벨은 모든 것이 모이는 자리입니다</h2>')
    b.append('<p>게임업에 종사하기 전에는 드라마 보조작가로서 전문 작가의 길을 걸었고, 이를 바탕으로 '
             '업계 입문 후에는 시나리오와 퀘스트 업무를 병행했습니다. 팀에 기획자가 저 하나뿐이던 '
             '프로젝트에서는 시스템과 밸런싱, BM, 운영까지 모두 직접 하였습니다. 전 레벨디자이너가 '
             '단순히 평면도를 그리고 예쁜 목업만 만드는 직업이라고 생각하지 않습니다.</p>')
    b.append('<p>레벨은 각 조직에서 공들여 만든 모든 요소들이 한데 모이는 자리입니다. 레벨 디자이너의 '
             '일은 각 요소들이 잘 어우러지게 하여 유저가 겪을 경험 하나로 묶는 것이라고 생각합니다. '
             '그래서 레벨 디자이너는 모든 것을 깊게 알아야 하는 올라운더여야 하고, 저는 그 모든 것을 '
             '직접 경험을 통해 습득했기에 보다 좋은 레벨을 설계하고 완성시킬 수 있다고 자부합니다.</p>')

    b.append(contact_note())
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
