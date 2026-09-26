# 손석완 · 레벨 디자이너 포트폴리오 (웹 배포용)

Caddy 정적 서버로 Railway 에 배포한다.

- `index.html` 페이지 본체
- `img/` 이미지 118장 (웹용 리샘플본)
- `vid/` 아우라 목업 플레이 영상 2편
- `Dockerfile` / `Caddyfile` 배포 설정
- `robots.txt` 검색엔진 전체 차단

원본 해상도 이미지와 작업 자료는 별도 저장소 `LevelDesign_Portfolio` 에 있다.

## 로컬 확인

```
docker build -t portfolio . && docker run --rm -p 8080:8080 portfolio
```
