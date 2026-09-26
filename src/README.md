# src/ — 작업 소스

페이지를 다시 빌드할 때 쓰는 원본들. 배포 이미지에는 포함되지 않는다(Dockerfile 이 COPY 하지 않음).

| 파일 | 용도 |
|---|---|
| `shell.html` | 페이지 head + CSS |
| `body.html` | 페이지 본문 골격. `<!--REGIONS-->` `<!--SUBNAV-->` 자리표시자 포함 |
| `build.py` | 지역별 갤러리 마크업 생성 → `_regions.html` `_nav.html` |
| `optimize.py` | 원본 이미지 → 웹용 리샘플 (평면도 2800px / 그 외 1600px) |
| `notion_dump.md` | 노션 이력서·경력기술서·프로젝트 상세 원문 |
| `resume_v2026_draft.md` | 2026 최신화 원고 |
| `aura_report.md` | 아우라 R&D 리포트 본문 |

## 빌드

```
py -3 src/build.py
# shell + body(치환) 를 합쳐 index.html 생성
```
