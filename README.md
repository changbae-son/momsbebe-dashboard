# 신아인터네셔날 업무 대시보드

OneWMS · 네이버쇼핑 데이터를 통합한 일일 운영 대시보드 + 오늘 할일 보드.

## 주요 기능
- 🎯 **오늘 할일 보드** (`?mode=board`) — 시간대별 자동 우선순위 추천 (출근→송장→본 게임→마감)
- 🖥️ **메인 대시보드** — 실시간 매출/재고/경쟁사 워치/원인-대응 매트릭스
- ☁️ GitHub Gist 자동 백업으로 로컬·클라우드 데이터 동기화

## 듀얼 모니터 사용법

| 모니터 | URL |
|--------|-----|
| 왼쪽 (보드) | `<배포주소>/?mode=board` |
| 오른쪽 (대시보드) | `<배포주소>/` |

## 로컬 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud 배포
1. https://share.streamlit.io 에서 GitHub 로그인
2. **Create app** → 이 리포 선택, branch: `main`, file: `app.py`
3. **Settings → Secrets** 에 `.streamlit/secrets.toml.example` 형식으로 실제 키 입력
4. Deploy

자세한 안내는 사내 운영 매뉴얼 참고.
