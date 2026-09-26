# src/ — 작업 소스

페이지를 다시 빌드할 때 쓰는 원본들. 배포 이미지에는 포함되지 않는다(Dockerfile 이 COPY 하지 않음).

| 파일 | 용도 |
|---|---|
| `content.py` | 페이지 내용 원본 — 프로젝트 · 지역/던전 · 경력 · 리포트 본문 |
| `build.py` | `content.py` 를 읽어 루트에 HTML 19장 생성 |
| `covers.py` | 카드·히어로용 커버 이미지 생성 (`img/` → `img/cov/*.webp`) |
| `optimize.py` | 원본 이미지 → 웹용 리샘플 (평면도 2800px / 그 외 1600px) |
| `notion_dump.md` | 노션 이력서·경력기술서·프로젝트 상세 원문 |
| `resume_v2026_draft.md` | 2026 최신화 원고 |
| `aura_report.md` | 아우라 R&D 리포트 본문 |
| `rename_map.json` | 원본 파일명 → 배포 파일명 매핑 |
| `mockups/` | 2026.09 디자인 시안 3종 (반려) |

스타일과 스크립트는 생성물이 아니라 직접 고치는 파일이다 — `assets/style.css`, `assets/app.js`.

## 빌드

```
python3 src/build.py          # HTML 다시 생성
python3 src/covers.py         # 커버 이미지 다시 굽기 (Pillow 필요)
```

## 페이지 구조

```
index.html                 랜딩 — 프로젝트 6개 카드
├─ kingsroad.html          대표 프로젝트 허브
│  ├─ kr-last-hearth / oldtown / highgarden / crows-nest / twins      필드 5
│  ├─ kr-griffin / kraken / beyond-wall / mammoth / harrenhal         던전 5
│  ├─ kr-systems.html      레벨 기능 · 기믹 기획
│  └─ aura.html            AI 목업 파이프라인 (R&D)
└─ p-zeta / p-nanolegend / p-minimax / p-kufc / p-kuf2                이전 프로젝트 5
```

내용을 고칠 때는 `content.py` 만 고치고 `build.py` 를 다시 돌린다. 루트의 `*.html` 은 전부 생성물이라
직접 고치면 다음 빌드에서 덮어쓴다.
