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
PHOTO = os.path.join(OUT, "photo.jpg")


def photo():
    """이력서용 증명사진. 원본을 3:4 로 가운데 크롭해 굽는다."""
    from PIL import Image
    src = os.path.join(ROOT, "src", "media", "profile.png")
    if not os.path.exists(src):
        src = os.path.join(ROOT, "img", "profile.webp")
    im = Image.open(src).convert("RGB")
    w, h = im.size
    if w / h > 3 / 4:
        nw = int(h * 3 / 4); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w * 4 / 3); im = im.crop((0, 0, w, nh))
    os.makedirs(OUT, exist_ok=True)
    im.resize((600, 800), Image.LANCZOS).save(PHOTO, "JPEG", quality=90)
    return PHOTO

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
header.with-photo{display:flex;justify-content:space-between;align-items:flex-start;gap:12pt}
.photo{width:28mm;height:37mm;object-fit:cover;border:.5pt solid #C7CCD3;flex-shrink:0}
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
h1.big .doc{font-size:10pt;font-weight:400;color:#6B727B;margin-left:8pt}
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
    return ('<header class="with-photo"><div><h1>%s<small>%s</small></h1>'
            '<div class="role">레벨 디자이너 · %s</div>'
            '<div class="meta"><b>%s</b> · <b>%s</b><br>%s</div></div>'
            '<img class="photo" src="file://%s" alt="증명사진"></header>'
            % (e(C.SITE["name"]), e(doc_name), e(career or CAREER),
               e(C.SITE["email"]), e(C.SITE["tel"]), site, photo()))


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
     [("필드", "지역 5곳(약 20㎢) 레벨디자인"),
      ("던전", "필드 던전 2종 · 파티 던전 2종 · 레이드 2종 · PvEvP 1종"),
      ("시스템", "레벨 기믹 시스템 전담"),
      ("AI", "평면도 제작 툴 + 언리얼 LLM 플러그인 Aura 목업 파이프라인 · "
             "Meshy AI를 활용한 목업으로 <b>제작 효율 50% 이상</b> 향상")],
     ("kingsroad.html", "상세")),
    ("너바나나", "2022.04 – 2022.08", "Project ZETA",
     "AAA 콘솔 액션 PvP · PS5·XBOX · UE5",
     "콘텐츠 기획팀 · 하이컨셉 단계 · 프로토타이핑 참여",
     [("기초 기획", "기초 룰 · 세계관 · 월드 · 캐릭터 · 핵심 시스템 · 캠페인의 기초 기획"),
      ("시나리오", "초기 시나리오 · 설정 전담"),
      ("레벨", "초기 메인 모드 레벨디자인")],
     ("p-zeta.html", "상세")),
    ("님블뉴런", "2020.04 – 2022.04", "나노레전드",
     "모바일 캐주얼 RTS · Unity · 자체 글로벌 퍼블리싱",
     "<b>팀 내 유일한 기획자</b> · 전투를 제외한 전 기획 전담 · 개발 시작부터 서비스 종료까지",
     [("성과", "iOS 매출 100위권 · 전략 카테고리 10위 중반권"),
      ("BM · 경제", "구독형 프리미엄 패스 · 패키지 · 가챠 · 광고 시청형 상품 · 경제 밸런싱 병행"),
      ("콘텐츠", "PvE 모드 · 레벨디자인 · 각종 모드 · 레이드 · 이벤트 콘텐츠"),
      ("시스템", "퀘스트 · 길드 · 시즌 이벤트 · 튜토리얼 · 운영 시스템 일체"),
      ("시나리오", "세계관 · 캐릭터 설정 · PvE 시나리오와 게임 내 모든 텍스트")],
     ("p-nanolegend.html", "상세")),
    ("님블뉴런", "2019.06 – 2020.04", "미니막스 타이니버스",
     "크로스플랫폼 RTS · PC(스팀)·모바일 · Unity · 자체 글로벌 퍼블리싱",
     "아웃게임 기획 담당 · 알파 버전부터 서비스 종료까지",
     [("BM", "구독형 배틀패스 · 상점 구조와 상품 갱신 · 유저 맞춤형 패키지 · 버프"),
      ("시스템", "퀘스트/업적 · 인벤토리 · 우편함 · 덱 저장/복사 · 커스텀 매치 등 일체"),
      ("밸런스", "유닛 성장 · 스탯 밸런싱과 경제 밸런싱"),
      ("시나리오", "세계관 · 캐릭터 컨셉 정립")],
     ("p-minimax.html", "상세")),
    ("블루사이드", "2018.06 – 2019.03", "Project KUFC",
     "콘솔 액션 RPG · 자체 엔진",
     "<b>콘텐츠 파트장</b> · 프로토타입부터 참여",
     [("총괄", "전체 콘텐츠 플로우 기획 · 시나리오 · 캐릭터 · 레벨디자인 총괄"),
      ("레벨", "핵심 미션 직접 제작 · 로비용 도시 기획")],
     ("p-kufc.html", "상세")),
    ("블루사이드", "2014.02 – 2018.06", "Kingdom Under Fire 2",
     "MMORPG + RTS · PC·콘솔 · 자체 엔진 · 글로벌 6개국 서비스",
     "레벨디자인 파트 · 레벨 디자이너 · 시나리오",
     [("레이드", "최종 · 최대 규모 레이드 '불꽃의 흉터' 메인 개발 · 소형 레이드 '극한미션' 2종"),
      ("PvP", "최고 인기 PvP 맵 '자유 경기장' · '격전의 도시' · 자유 PvP 매칭 시스템"),
      ("필드 · 월드", "PK 필드 · 월드맵과 도시"),
      ("미션", "미션 제작과 폴리싱 · 각종 모드 · 몬스터 밸런싱"),
      ("시나리오", "메인 시나리오 일부 · 서브 플롯 · <b>퀘스트 약 300개</b> · 대화형 컷신 40% 직접 제작"),
      ("기타", "2014 E3 소니 컨퍼런스 발표 영상 기획 · 확장팩 컨셉(설정 · 도시 · 미션 · NPC) 총괄")],
     ("p-kuf2.html", "상세")),
]

# 업계 외 — 이력서에서는 묶어서 세 줄로 (사이트의 키워드 나열과 다르다)
OFFINDUSTRY = ("오디오드라마 <b>집필 · 연출 · 제작</b> (현재)<br>"
               "시나리오 보조작가 — 어린이 드라마 · 만화 · 애니메이션 대본 · 글콘티<br>"
               "독립영화 연출부 · 제작부 · 영화 전공")


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
    b.append('<tr><td class="k">업계 외</td><td class="v kw">%s</td></tr>' % OFFINDUSTRY)
    b.append('</table>')
    return page("손석완 이력서", "".join(b))


# ─────────────────────────────────────────────────────── 자기소개서
def letter():
    """웹 포트폴리오 첫 화면(한 줄 소개 · 요약)과 강점 카드 세 장을 그대로 옮긴다.
    덧붙인 문장은 없다. 사이트 문안이 바뀌면 여기도 같이 바뀐다."""
    years = months_since(C.SITE["career_start"]) // 12 + 1
    b = ['<header class="hl"><h1 class="big">%s<small class="doc">자기소개서</small></h1>'
         '<div class="who">레벨 디자이너 · %d년 차 (Since %s)</div></header>'
         % (e(C.SITE["name"]), years, C.SITE["career_start"][:4])]
    b.append('<p class="lede">%s</p>' % e(C.HOME["lede"]))
    b.append('<p>%s</p>' % C.HOME["sub"].replace("{{career}}", "<b>%s</b>" % CAREER))
    for _, title, text in C.HOME["feats"]:
        b.append('<h2>%s</h2>' % e(title))
        b.append('<p>%s</p>' % text)
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
