# -*- coding: utf-8 -*-
"""index.html 생성기.

src/style.css + 아래 콘텐츠 데이터를 합쳐 단일 파일 페이지를 만든다.
랜딩에서 큰 카드로 진입하는 해시 라우팅 구조(뒤로가기·URL 공유 가능).

    py -3 src/build.py
"""
import io, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
IMG = os.path.join(ROOT, "img")

def e(s):
    return html.escape(s, quote=True)

files = sorted(os.listdir(IMG))
SLOT = {"plan": "평면도", "mock": "목업 전경", "final": "완성 화면"}


# ────────────────────────────────── 킹스로드 담당 콘텐츠

REGIONS = [
 dict(num="01", nav="최북단", title="최북단 · 라스트허스 / 레난스레스트",
   meta="필드 지역 · 챕터 1.1 · 2023", stat="서브밋 234건",
   role="인트로 튜토리얼 구간 · 평면도 · 레벨 기획서 · 목업 담당",
   desc="게임의 첫 지역. 이동 규칙과 필드 콘텐츠 5종을 학습시키는 구간으로, 플레이 시퀀스와 구간별 소요 시간까지 함께 설계했습니다.",
   caps={"plan":"캐슬블랙~라스트하스~롱레이크 구간의 지역 경계·주 동선·콘텐츠 배치.",
         "mock":"세부 지역별 목업을 각도별로 검증. 붉은 마킹은 배치·수정 대상 구역.",
         "final":"장벽·몰스 타운·라스트 하스 일대와 실내 공간."},
   yt="AsC8DTOZZI4", ytlab="출시 영상 · 레난스레스트"),

 dict(num="02", nav="올드타운", title="올드타운 (리치)",
   meta="필드 지역 · 챕터 2.1–2.2 · 2023", stat="서브밋 248건",
   role="평면도 · 레벨 기획서 · B구역 필드 목업 S1~S5 · 시타델 내부 목업 담당",
   desc="담당 지역 중 최대 규모. A~D 구역으로 쪼개고 콘텐츠마다 식별 코드를 부여해 목업·이슈·QA까지 같은 코드로 추적했습니다.",
   caps={"plan":"시타델·항구를 축으로 한 도시 구조와 주변 필드, 이동 경로.",
         "mock":"밀밭·마을·셉트·해안 절벽 등 세부 지역 목업. 색상 마킹으로 배치 대상을 구분.",
         "final":"시타델과 항구, 해안 절벽 시가지와 광장."},
   yt="b4sJzjbDA_U", ytlab="출시 영상 · 웨스테로스 탐험 · 올드타운"),

 dict(num="03", nav="하이가든", title="하이가든",
   meta="필드 지역 · 챕터 2.3 · 2023", stat="서브밋 138건",
   role="평면도 1차·최종 · 레벨 기획서 1차·최종 · 성·마을 목업 · 필드 목업 담당",
   desc="리치 남부의 정원 도시. 평면도·기획서를 1차 / 최종으로 나눠 개정하며 성·마을과 필드를 단계적으로 확정했습니다. 필드 콘텐츠로 세력 은신처와 위기의 성소를 배치했습니다.",
   caps={"plan":"성채를 중심으로 한 필드 구성과 진입 동선.",
         "mock":"성 입구·메인 광장·연회장·축제장·상점가·미로 정원.",
         "final":"성채와 정원, 연회장·축제장, 본성 영접실."}),

 dict(num="04", nav="크로우즈네스트", title="크로우즈네스트 (스톰랜드)",
   meta="필드 지역 · 챕터 3.3 · 2023–2024", stat="서브밋 63건",
   role="평면도·기획서 리뉴얼 전 세트 재제작 · 세력 은신처 · 점령된 구역 담당",
   desc="초기 제작 후 리뉴얼이 결정되어 평면도부터 목업까지 전 세트를 다시 제작했습니다. 이후 점령된 구역(2024)과 소형 콘텐츠 배치(2026)까지 담당했습니다. 2025년 6월 첫 대형 업데이트로 출시된 지역입니다.",
   caps={"plan":"메인(M)·서브(S) 콘텐츠 배치를 지도에 직접 표기.",
         "mock":"숙영지·항구마을·약초밭·채석장 등 점령된 구역. 초록은 전투 구역, 붉은색은 배치 대상.",
         "final":"성채와 채석장, 항구마을, 숙영지 일대."}),

 dict(num="05", nav="트윈스", title="트윈스",
   meta="필드 지역 · 챕터 5.2 · 2026", stat="진행 중",
   role="지역 레벨디자인 · 목업 담당",
   desc="챕터5 넥 권역의 신규 지역. 늪지·수상 가옥 등 기존 지역과 무드가 달라 컨셉 단계를 별도로 세웠습니다.",
   caps={}, hide="미공개 지역 — 아직 출시되지 않아 평면도·목업·완성 화면을 싣지 않았습니다."),

 dict(num="06", nav="그리핀 던전", title="그리핀 던전 (기억의 제단)",
   meta="던전 · 2022–2023", stat="Jira 42건 · 서브밋 118건",
   role="첫 던전 단독 전담 · 레벨 기획 + 기능 기획 · 6개 부서 발주",
   desc="입사 3개월차에 받은 첫 던전, 단독 전담. 레벨·기능 기획을 직접 하고 6개 부서에 발주했습니다. 기획 의도 전달용 인게임 장치(컨셉 쪽지 가젯)까지 설계했습니다.",
   caps={"plan":"Top View — 스타트 포인트·진입로·전투 공간·공중 공간(직경 110m)과 덫 설치 지점을 치수와 함께 확정.",
         "mock":"Perspective View — 나루터·진입로·전투 공간·숲길·피치 오염 지대를 블록아웃으로 세우고 등장 연출 위치를 표기.",
         "final":"나루터 진입부와 전투 공간, 갱도 구간."},
   yt="PTcLt2CsOfU", ytlab="플레이 영상 · 기억의 제단 · 그리핀 처치"),

 dict(num="07", nav="크라켄 던전", title="크라켄 던전 (기억의 제단 → 심연의 제단)",
   meta="던전 · 2023–2026", stat="서브밋 26건",
   role="레벨디자인 · 페이즈 동선",
   desc="해저 동굴 던전. 페이즈 전환 동선과 낙사 지점을 설계하고, 심연의 제단으로 이어지며 하드·관전 모드 이슈까지 대응했습니다.",
   caps={"plan":"인트로부터 P1~P3-3까지 페이즈별 전투 구역과 이동 경로를 구역 설명과 함께 정리.",
         "mock":"해안 요새·난파선·등대를 블록아웃으로 배치해 페이즈 간 동선을 검증.",
         "final":"해안 요새와 난파선, 페이즈별 전투 공간."},
   yt="pWnUNvTq0wU", ytlab="플레이 영상 · 심연의 제단 · 강철군도 해안의 크라켄"),

 dict(num="08", nav="장벽너머", title="장벽너머 던전 (일부)",
   meta="던전 · 2023–2024", stat="서브밋 28건",
   role="PvE 콘텐츠 목업 9/9 완주 · 밤의 경비대 구출 · 야인 거인 처치 구간",
   desc="PvE 콘텐츠의 일부 구간 담당. 목업 9회 완주, 밤의 경비대 구출·야인 거인 처치 구간의 밧줄 특수 이동과 스타팅 포인트 이슈를 정리했습니다.",
   caps={"plan":"7구역 평면도 — 설원 전투 구역의 지형과 엄폐물 배치.",
         "final":"설원 협곡과 빙벽 전투 구역."}),

 dict(num="09", nav="맘모스 던전", title="맘모스 던전 (심연의 제단)",
   meta="던전 · 2026", stat="진행 중",
   role="배경팀 전달용 레벨 기획서 작성 · 구역 분할 및 치수 확정 · 목업 OBJ 전달",
   desc="빙하 던전. 배경팀 전달용 레벨 기획서를 작성해 구역 분할·치수를 확정하고, 목업을 좌표계 맞춘 OBJ로 전달했습니다.",
   caps={"plan":"스폰 지점부터 P1 빙하 평원 · P2 빙벽/동굴 · P3 빙하 끝단까지 페이즈별 구역과 요약 설명.",
         "mock":"빙하 지형과 조우 공간을 블록아웃으로 세워 규모와 진입 실루엣을 확정."},
   tail="완성 화면 미공개 — 개발 진행 중인 콘텐츠입니다."),

 dict(num="10", nav="하렌홀", title="하렌홀 (PvEvP)",
   meta="던전 · 2026", stat="킥오프부터 참여",
   role="구현 기획서 · 레벨 기획서 · 목업 1차·2차(픽스) · 레벨 조정",
   desc="경쟁형 PvEvP 던전. 킥오프부터 참여해 구현·레벨 기획서를 쓰고 목업 1차·2차(픽스)까지 제작했습니다. 성채를 다층으로 나눠 진입 관문 → 중정 → 시가지 → 협곡 수로 동선을 화이트박스로 검증했습니다.",
   caps={"plan":"A~G 구역 분할, 층별 색 구분, 팀 A/B 스타팅·리스폰·인장 반납·문·기믹 위치.",
         "mock":"흐름돌 마당·부서진 탑·지하 감옥 터널·정원 회랑·병영·내성 앞마당과 문 기믹 공간."},
   tail="완성 화면 미공개 — 미출시 콘텐츠입니다."),
]

# 파일 접두사: 트윈스가 05로 끼어들어 이미지 번호와 어긋나므로 명시 매핑
PREFIX = {"01":"01","02":"02","03":"03","04":"04","05":None,
          "06":"05","07":"06","08":"07","09":"08","10":"09"}


def gallery(prefix, slot, cap, title):
    fs = [f for f in files if f.startswith("%s-%s" % (prefix, slot))]
    if not fs:
        return ""
    n = len(fs)
    cls = "g1" if n == 1 else ("g2" if n <= 4 else "g3")
    cells = []
    for i, f in enumerate(fs):
        alt = "%s %s %d" % (title, SLOT[slot], i + 1)
        cells.append(
            '<button class="shot" data-src="img/%s" data-cap="%s" aria-label="%s 확대">'
            '<img src="img/%s" alt="%s" loading="lazy" decoding="async"></button>'
            % (e(f), e(cap), e(alt), e(f), e(alt)))
    return ('<div class="slot"><span class="slab">%s</span><p class="scap">%s</p>'
            '<div class="grid %s">%s</div></div>'
            % (SLOT[slot], e(cap), cls, "".join(cells)))


def region_html(r):
    p = [ '<article class="region" id="r-%s">' % r["num"] ]
    p.append('<div class="region-top"><span class="rnum">%s</span><div>'
             '<h3 class="h-md">%s</h3>'
             '<p class="rmeta">%s &nbsp;·&nbsp; <b>%s</b></p></div></div>'
             % (e(r["num"]), e(r["title"]), e(r["meta"]), e(r["stat"])))
    p.append('<p class="rrole">%s</p>' % e(r["role"]))
    p.append('<p class="body narrow">%s</p>' % e(r["desc"]))
    if r.get("hide"):
        p.append('<p class="note">%s</p>' % e(r["hide"]))
    pre = PREFIX[r["num"]]
    if pre:
        for slot in ("plan", "mock", "final"):
            if slot in r["caps"]:
                p.append(gallery(pre, slot, r["caps"][slot], r["title"]))
    if r.get("tail"):
        p.append('<p class="note">%s</p>' % e(r["tail"]))
    if r.get("yt"):
        p.append('<div class="slot"><span class="slab">플레이 영상</span>'
                 '<p class="scap">%s</p><div class="vid">'
                 '<iframe src="https://www.youtube-nocookie.com/embed/%s" title="%s" '
                 'loading="lazy" allowfullscreen '
                 'allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture">'
                 '</iframe></div></div>' % (e(r["ytlab"]), e(r["yt"]), e(r["ytlab"])))
    p.append('</article>')
    return "".join(p)


REGIONS_HTML = "\n".join(region_html(r) for r in REGIONS)

# ────────────────────────────────── 조립

css = io.open(os.path.join(SRC, "style.css"), encoding="utf-8").read()
body = io.open(os.path.join(SRC, "body.html"), encoding="utf-8").read()
body = body.replace("<!--REGIONS-->", REGIONS_HTML)

out = (
    '<title>손석완 레벨 디자인</title>\n'
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=Gothic+A1:wght@400;500;700;800;900&display=swap">\n'
    '<style>\n' + css + '\n</style>\n' + body
)

path = os.path.join(ROOT, "index.html")
io.open(path, "w", encoding="utf-8", newline="").write(out)
print("index.html  %.1f KB" % (len(out.encode("utf-8")) / 1024))
print("  지역 %d개 / 이미지 %d장 / 영상 %d편"
      % (len(REGIONS), out.count("<img "), out.count("<iframe")))
