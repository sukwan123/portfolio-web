# 손석완 · 레벨 디자이너 포트폴리오 (웹 배포용)

Caddy 정적 서버로 Railway 에 배포한다.

- `index.html` 외 루트의 `*.html` 19장 — `src/build.py` 가 생성한다. 직접 고치지 않는다
- `assets/` 스타일시트와 스크립트 (직접 고치는 파일)
- `img/` 이미지 118장 (웹용 리샘플본) + `img/cov/` 카드·히어로 커버
- `vid/` 아우라 목업 플레이 영상 2편
- `src/` 내용 원본과 빌드 스크립트 — 배포 이미지에는 들어가지 않는다
- `Dockerfile` / `Caddyfile` 배포 설정
- `robots.txt` + `X-Robots-Tag` 헤더로 검색엔진 전체 차단

원본 해상도 이미지와 작업 자료는 별도 저장소 `LevelDesign_Portfolio` 에 있다.

## 구조

```
index.html                 랜딩 — 프로젝트 6개 카드
├─ kingsroad.html          왕좌의 게임: 킹스로드 (허브)
│  ├─ kr-*.html            담당 지역 5 · 던전 5
│  ├─ kr-systems.html      레벨 기능 · 기믹 기획
│  └─ aura.html            AI 목업 파이프라인 (R&D)
└─ p-*.html                이전 프로젝트 5종
```

## 내용 수정

```
python3 src/build.py       # src/content.py 를 고친 뒤 실행
```

## 로컬 확인

```
python3 -m http.server 8080          # 정적 확인
docker build -t portfolio . && docker run --rm -p 8080:8080 portfolio
```
