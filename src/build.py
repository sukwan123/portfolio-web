# -*- coding: utf-8 -*-
import os, io, json, html
WEB = r"C:\Users\n-suk\ForClaude\_web"
IMG = os.path.join(WEB, "img")
files = sorted(os.listdir(IMG))

def pick(prefix):
    return [f for f in files if f.startswith(prefix)]

REGIONS = [
 dict(num="01", nav="최북단", title="최북단 · 라스트허스 / 레난스레스트", meta="필드 지역 · 챕터 1.1 · 2023",
   stat="서브밋 234건",
   role="인트로 튜토리얼 구간 · 평면도 · 레벨 기획서 · 목업 담당",
   desc="게임의 첫 지역. 이동 규칙과 필드 콘텐츠 5종을 학습시키는 구간으로, 플레이 시퀀스와 구간별 소요 시간까지 함께 설계했습니다.",
   caps={"1":"평면도 — 캐슬블랙~라스트하스~롱레이크 구간의 지역 경계·주 동선·콘텐츠 배치.",
         "2":"목업 전경 — 세부 지역별 목업을 각도별로 검증. 붉은 마킹은 배치·수정 대상 구역.",
         "3":"완성 화면 — 장벽·몰스 타운·라스트 하스 일대와 실내 공간."},
   yt="AsC8DTOZZI4", ytlab="출시 영상 — 레난스레스트 (공식 채널)"),
 dict(num="02", nav="올드타운", title="올드타운 (리치)", meta="필드 지역 · 챕터 2.1–2.2 · 2023",
   stat="서브밋 248건",
   role="평면도 · 레벨 기획서 · B구역 필드 목업 S1~S5 · 시타델 내부 목업 담당",
   desc="담당 지역 중 최대 규모. A~D 구역으로 쪼개고 콘텐츠마다 식별 코드를 부여해 목업·이슈·QA까지 같은 코드로 추적했습니다.",
   caps={"1":"평면도 — 시타델·항구를 축으로 한 도시 구조와 주변 필드, 이동 경로.",
         "2":"목업 전경 — 밀밭·마을·셉트·해안 절벽 등 세부 지역 목업. 색상 마킹으로 배치 대상을 구분.",
         "3":"완성 화면 — 시타델과 항구, 해안 절벽 시가지와 광장."},
   yt="b4sJzjbDA_U", ytlab="출시 영상 — 웨스테로스 탐험 · 올드타운 (공식 채널)"),
 dict(num="03", nav="하이가든", title="하이가든", meta="필드 지역 · 챕터 2.3 · 2023",
   stat="서브밋 138건",
   role="평면도 1차·최종 · 레벨 기획서 1차·최종 · 성·마을 목업 · 필드 목업 담당",
   desc="리치 남부의 정원 도시. 평면도·기획서를 1차 / 최종으로 나눠 개정하며 성·마을과 필드를 단계적으로 확정. 필드 콘텐츠로 세력 은신처와 위기의 성소를 배치했습니다.",
   caps={"1":"평면도 — 성채를 중심으로 한 필드 구성과 진입 동선.",
         "2":"목업 전경 — 성 입구·메인 광장·연회장·축제장·상점가·미로 정원.",
         "3":"완성 화면 — 성채와 정원, 연회장·축제장, 본성 영접실."},
   yt=None, ytlab=None),
 dict(num="04", nav="크로우즈네스트", title="크로우즈네스트 (스톰랜드)", meta="필드 지역 · 챕터 3.3 · 2023–2024",
   stat="서브밋 63건",
   role="평면도·기획서 리뉴얼 전 세트 재제작 · 세력 은신처 · 점령된 구역 담당",
   desc="초기 제작 후 리뉴얼이 결정되어 평면도부터 목업까지 전 세트를 다시 제작. 이후 점령된 구역(2024)과 소형 콘텐츠 배치(2026)까지 담당했습니다.",
   caps={"1":"평면도 — 메인(M)·서브(S) 콘텐츠 배치를 지도에 직접 표기.",
         "2":"목업 전경 — 숙영지·항구마을·약초밭·채석장 등 점령된 구역. 초록은 전투 구역, 붉은색은 배치 대상.",
         "3":"완성 화면 — 성채와 채석장, 항구마을, 숙영지 일대."},
   yt=None, ytlab=None),
 dict(num="TW", nav="트윈스", title="트윈스", meta="필드 지역 · 챕터 5.2 · 2026", stat="진행 중",
   role="지역 레벨디자인 · 목업 담당",
   desc="챕터5 넥 권역의 신규 지역. 늪지·수상 가옥 등 기존 지역과 무드가 달라 컨셉 단계를 별도로 세웠습니다.",
   caps={}, yt=None, ytlab=None, undisclosed="미공개 지역 — 아직 출시되지 않아 평면도·목업·완성 화면을 싣지 않았습니다."),
 dict(num="05", nav="그리핀 던전", title="그리핀 던전 (기억의 제단)", meta="던전 · 2022–2023",
   stat="Jira 42건 · 서브밋 118건",
   role="첫 던전 단독 전담 · 레벨 기획 + 기능 기획 · 6개 부서 발주",
   desc="입사 3개월차에 받은 첫 던전, 단독 전담. 레벨·기능 기획을 직접 하고 6개 부서에 발주. 기획 의도 전달용 인게임 장치(컨셉 쪽지 가젯)까지 설계했습니다.",
   caps={"1":"던전 구조 (Top View) — 스타트 포인트·진입로·전투 공간·공중 공간(직경 110m)과 덫 설치 지점을 치수와 함께 확정.",
         "2":"Perspective View — 나루터·진입로·전투 공간·숲길·피치 오염 지대를 블록아웃으로 세우고 등장 연출 위치를 표기.",
         "3":"완성 화면 — 나루터 진입부와 전투 공간, 갱도 구간."},
   yt="PTcLt2CsOfU", ytlab="플레이 영상 — 기억의 제단 · 그리핀 처치"),
 dict(num="06", nav="크라켄 던전", title="크라켄 던전 (기억의 제단 → 심연의 제단)", meta="던전 · 2023–2026",
   stat="서브밋 26건",
   role="레벨디자인 · 페이즈 동선",
   desc="해저 동굴 던전. 페이즈 전환 동선과 낙사 지점을 설계하고, 심연의 제단으로 이어지며 하드·관전 모드 이슈까지 대응했습니다.",
   caps={"1":"평면도 — 인트로부터 P1~P3-3까지 페이즈별 전투 구역과 이동 경로를 구역 설명과 함께 정리.",
         "2":"목업 전경 — 해안 요새·난파선·등대를 블록아웃으로 배치해 페이즈 간 동선을 검증.",
         "3":"완성 화면 — 해안 요새와 난파선, 페이즈별 전투 공간."},
   yt="pWnUNvTq0wU", ytlab="플레이 영상 — 심연의 제단 · 강철군도 해안의 크라켄"),
 dict(num="07", nav="장벽너머", title="장벽너머 던전 (일부)", meta="던전 · 2023–2024",
   stat="서브밋 28건",
   role="PvE 콘텐츠 목업 9/9 완주 · 밤의 경비대 구출 · 야인 거인 처치 구간",
   desc="PvE 콘텐츠의 일부 구간 담당. 목업 9회 완주, 밤의 경비대 구출·야인 거인 처치 구간의 밧줄 특수 이동과 스타팅 포인트 이슈를 정리했습니다.",
   caps={"1":"7구역 평면도 — 설원 전투 구역의 지형과 엄폐물 배치.",
         "3":"완성 화면 — 설원 협곡과 빙벽 전투 구역."},
   yt=None, ytlab=None),
 dict(num="08", nav="맘모스 던전", title="맘모스 던전 (심연의 제단)", meta="던전 · 2026", stat="진행 중",
   role="배경팀 전달용 레벨 기획서 작성 · 구역 분할 및 치수 확정 · 목업 OBJ 전달",
   desc="빙하 던전. 배경팀 전달용 레벨 기획서를 작성해 구역 분할·치수를 확정하고, 목업을 좌표계 맞춘 OBJ로 전달했습니다.",
   caps={"1":"평면도 — 스폰 지점부터 P1 빙하 평원 · P2 빙벽/동굴 · P3 빙하 끝단까지 페이즈별 구역과 요약 설명.",
         "2":"목업 전경 — 빙하 지형과 조우 공간을 블록아웃으로 세워 규모와 진입 실루엣을 확정."},
   yt=None, ytlab=None, partial="완성 화면 미공개 — 개발 진행 중인 콘텐츠입니다."),
 dict(num="09", nav="하렌홀", title="하렌홀 (PvEvP)", meta="던전 · 2026", stat="킥오프부터 참여",
   role="구현 기획서 · 레벨 기획서 · 목업 1차·2차(픽스) · 레벨 조정",
   desc="경쟁형 PvEvP 던전. 킥오프부터 참여해 구현·레벨 기획서를 쓰고 목업 1차·2차(픽스)까지 제작. 성채를 다층으로 나눠 진입 관문 → 중정 → 시가지 → 협곡 수로 동선을 화이트박스로 검증했습니다.",
   caps={"1":"평면도 — A~G 구역 분할, 층별 색 구분, 팀 A/B 스타팅·리스폰·인장 반납·문·기믹 위치.",
         "2":"목업 전경 — 흐름돌 마당·부서진 탑·지하 감옥 터널·정원 회랑·병영·내성 앞마당과 문 기믹 공간."},
   yt=None, ytlab=None, partial="완성 화면 미공개 — 미출시 콘텐츠입니다."),
]

SLOT_LABEL = {"1":"평면도","2":"목업 전경","3":"완성 화면"}

def esc(s): return html.escape(s, quote=True)

SLOTNAME = {"1":"plan","2":"mock","3":"final"}
def grid(prefix, slot, cap, region_title):
    fs = pick("%s-%s" % (prefix, SLOTNAME[slot]))
    if not fs: return ""
    n = len(fs)
    cls = "g1" if n == 1 else ("g2" if n <= 4 else "g3")
    cells = []
    for i, f in enumerate(fs):
        alt = "%s %s %d" % (region_title, SLOT_LABEL[slot], i+1)
        cells.append(
          '<button class="shot" data-src="img/%s" data-cap="%s" aria-label="%s 확대">'
          '<img src="img/%s" alt="%s" loading="lazy" decoding="async"></button>'
          % (esc(f), esc(cap), esc(alt), esc(f), esc(alt)))
    return ('<div class="slot"><div class="slot-head"><span class="slot-tag">%s</span>'
            '<p class="slot-cap">%s</p></div><div class="grid %s">%s</div></div>'
            % (SLOT_LABEL[slot], esc(cap), cls, "".join(cells)))

def region_html(r):
    parts = []
    parts.append('<article class="region" id="r-%s">' % r["num"].lower())
    parts.append('<header class="region-head">')
    parts.append('<div class="region-id">%s</div>' % esc(r["num"]))
    parts.append('<div class="region-title"><h3>%s</h3>'
                 '<p class="region-meta">%s<span class="dot">·</span><b>%s</b></p></div></header>'
                 % (esc(r["title"]), esc(r["meta"]), esc(r["stat"])))
    parts.append('<p class="region-role">%s</p>' % esc(r["role"]))
    parts.append('<p class="region-desc">%s</p>' % esc(r["desc"]))
    if r.get("undisclosed"):
        parts.append('<p class="undisclosed">%s</p>' % esc(r["undisclosed"]))
    for slot in ("1","2","3"):
        if slot in r["caps"]:
            parts.append(grid(r["num"], slot, r["caps"][slot], r["title"]))
    if r.get("partial"):
        parts.append('<p class="undisclosed">%s</p>' % esc(r["partial"]))
    if r.get("yt"):
        parts.append('<div class="slot"><div class="slot-head"><span class="slot-tag">영상</span>'
          '<p class="slot-cap">실제 플레이 영상입니다. 유튜브에서 새 탭으로 열립니다.</p></div>'
          '<a class="ytlink" href="https://www.youtube.com/watch?v=%s" target="_blank" rel="noopener noreferrer">'
          '<span class="ico">&#9654;</span><span class="txt"><b>%s</b>'
          '<em>youtube.com/watch?v=%s</em></span></a></div>'
          % (esc(r["yt"]), esc(r["ytlab"]), esc(r["yt"])))
    parts.append('</article>')
    return "".join(parts)

regions_html = "\n".join(region_html(r) for r in REGIONS)
nav_regions = "\n".join('<a href="#r-%s">%s</a>' % (r["num"].lower(), esc(r["nav"])) for r in REGIONS)

io.open(os.path.join(WEB, "_regions.html"), "w", encoding="utf-8").write(regions_html)
io.open(os.path.join(WEB, "_nav.html"), "w", encoding="utf-8").write(nav_regions)
print("regions html:", len(regions_html), "chars")
print("image refs:", regions_html.count('<img '))
