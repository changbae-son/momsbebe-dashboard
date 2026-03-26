"""
신아인터네셔날(ShinA International) 실시간 가격 모니터링 및 업무 대시보드
=======================================================
- 네이버 쇼핑 실시간 가격 크롤링
- 원싱크(OneSync) API 연동 구조 (Placeholder)
- 업무 일지(Daily Log) 입력 및 저장
- CEO 지시 사항 섹션
"""

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# 페이지 기본 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="신아인터네셔날 업무 대시보드",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# 커스텀 CSS (다크/라이트 모드 호환)
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* ── 전역 스타일 ── */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');

    .block-container { padding-top: 1rem; max-width: 1200px; }

    /* ── 헤더 배너 ── */
    .header-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.8rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1.2rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
    }
    .header-banner .logo {
        font-size: 2.8rem;
        line-height: 1;
    }
    .header-banner h1 {
        margin: 0; font-size: 1.7rem; font-weight: 700; letter-spacing: -0.5px;
    }
    .header-banner p {
        margin: 0.2rem 0 0 0; font-size: 0.9rem; opacity: 0.85;
    }
    .header-right {
        margin-left: auto;
        text-align: right;
        font-size: 0.8rem;
        opacity: 0.8;
    }
    .header-right .date { font-size: 1.1rem; font-weight: 600; opacity: 1; }

    /* ── CEO 지시사항 박스 ── */
    .ceo-strategy-box {
        background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
        color: #2d1b1b;
        padding: 1.3rem 1.6rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
        position: relative;
        box-shadow: 0 4px 20px rgba(255, 154, 158, 0.2);
    }
    .ceo-strategy-box .badge {
        display: inline-block;
        background: rgba(255,255,255,0.5);
        color: #c0392b;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        margin-bottom: 0.5rem;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .ceo-strategy-box h3 {
        margin: 0 0 0.6rem 0;
        font-size: 1.15rem;
        font-weight: 700;
        color: #7b2d26;
    }
    .ceo-strategy-box .content {
        font-size: 0.95rem;
        line-height: 1.7;
        color: #3d1a1a;
    }
    .ceo-strategy-box .meta {
        margin-top: 0.6rem;
        font-size: 0.75rem;
        opacity: 0.6;
    }
    .ceo-empty {
        background: rgba(128,128,128,0.06);
        border: 2px dashed rgba(128,128,128,0.2);
        color: inherit;
        padding: 1.2rem 1.5rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
        text-align: center;
        opacity: 0.6;
    }

    /* ── KPI 메트릭 카드 ── */
    .kpi-card {
        padding: 1.2rem 1.4rem;
        border-radius: 14px;
        border: 1px solid rgba(128,128,128,0.12);
        background: rgba(128,128,128,0.03);
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    }
    .kpi-card .icon { font-size: 1.6rem; margin-bottom: 0.3rem; }
    .kpi-card .label { font-size: 0.78rem; opacity: 0.6; margin-bottom: 0.3rem; }
    .kpi-card .value { font-size: 1.6rem; font-weight: 800; }
    .kpi-card .sub { font-size: 0.7rem; opacity: 0.5; margin-top: 0.2rem; }
    .kpi-card.pending .value { opacity: 0.35; font-size: 1.1rem; }

    /* ── 섹션 헤더 ── */
    .section-title {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1.15rem;
        font-weight: 700;
        margin: 2rem 0 0.8rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(102, 126, 234, 0.3);
    }
    .section-title .icon { font-size: 1.3rem; }

    /* ── 업무 일지 카드 ── */
    .log-entry {
        padding: 1rem 1.2rem;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.1);
        background: rgba(128,128,128,0.03);
        margin-bottom: 0.6rem;
    }
    .log-entry .log-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .log-entry .role-badge {
        display: inline-block;
        padding: 0.15rem 0.5rem;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 700;
    }
    .role-md { background: #dbeafe; color: #1e40af; }
    .role-cs { background: #dcfce7; color: #166534; }
    .role-ceo { background: #fef3c7; color: #92400e; }
    .role-etc { background: #f3e8ff; color: #6b21a8; }
    .log-entry .log-item {
        font-size: 0.85rem;
        line-height: 1.6;
        margin: 0.25rem 0;
        padding-left: 0.8rem;
        border-left: 2px solid rgba(128,128,128,0.15);
    }
    .log-entry .log-label {
        font-weight: 600;
        font-size: 0.75rem;
        opacity: 0.7;
    }

    /* ── 사이드바 ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(102,126,234,0.05) 0%, rgba(118,75,162,0.05) 100%);
    }
    [data-testid="stSidebar"] [data-testid="stMarkdown"] h1 {
        font-size: 1.3rem;
    }

    /* ── 푸터 ── */
    .footer {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
        font-size: 0.75rem;
        opacity: 0.4;
    }

    /* ── 검색 결과 테이블 가격 하이라이트 ── */
    .price-highlight {
        font-weight: 700;
        color: #667eea;
    }

    /* ── 빈 상태 박스 ── */
    .empty-state {
        text-align: center;
        padding: 2rem 1rem;
        opacity: 0.5;
    }
    .empty-state .icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
    .empty-state p { font-size: 0.9rem; }

    /* ── 상품 카드 ── */
    .product-card {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.9rem 1.2rem;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.1);
        background: rgba(128,128,128,0.02);
        margin-bottom: 0.5rem;
        transition: all 0.2s;
    }
    .product-card:hover {
        border-color: rgba(102, 126, 234, 0.3);
        background: rgba(102, 126, 234, 0.04);
        transform: translateX(3px);
    }
    .product-card .rank {
        font-size: 1.3rem;
        font-weight: 800;
        color: #667eea;
        min-width: 2rem;
        text-align: center;
    }
    .product-card .rank.top1 { color: #f5576c; }
    .product-card .info { flex: 1; min-width: 0; }
    .product-card .name {
        font-size: 0.92rem;
        font-weight: 600;
        margin-bottom: 0.2rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .product-card .name a {
        color: inherit;
        text-decoration: none;
    }
    .product-card .name a:hover {
        color: #667eea;
        text-decoration: underline;
    }
    .product-card .meta-row {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 0.78rem;
        opacity: 0.6;
    }
    .product-card .mall-badge {
        display: inline-block;
        padding: 0.1rem 0.45rem;
        border-radius: 8px;
        font-size: 0.7rem;
        font-weight: 600;
        background: rgba(102, 126, 234, 0.1);
        color: #667eea;
    }
    .product-card .price {
        font-size: 1.15rem;
        font-weight: 800;
        color: #667eea;
        white-space: nowrap;
    }
    .product-card .price.lowest {
        color: #f5576c;
    }

    /* ── 가격 요약 카드 ── */
    .price-summary {
        display: flex;
        gap: 1rem;
        margin-top: 0.8rem;
    }
    .price-summary-item {
        flex: 1;
        padding: 0.8rem 1rem;
        border-radius: 12px;
        text-align: center;
    }
    .price-summary-item.lowest {
        background: rgba(245, 87, 108, 0.08);
        border: 1px solid rgba(245, 87, 108, 0.2);
    }
    .price-summary-item.highest {
        background: rgba(128,128,128,0.05);
        border: 1px solid rgba(128,128,128,0.12);
    }
    .price-summary-item.average {
        background: rgba(102, 126, 234, 0.08);
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    .price-summary-item .label { font-size: 0.75rem; opacity: 0.6; }
    .price-summary-item .value { font-size: 1.3rem; font-weight: 800; }
    .price-summary-item .sub { font-size: 0.72rem; opacity: 0.5; margin-top: 0.15rem; }
    .price-summary-item.lowest .value { color: #f5576c; }
    .price-summary-item.average .value { color: #667eea; }

    /* ── 우리 매장 하이라이트 ── */
    .product-card.ours {
        border: 2px solid #f59e0b;
        background: rgba(245, 158, 11, 0.06);
    }
    .product-card.ours:hover {
        border-color: #f59e0b;
        background: rgba(245, 158, 11, 0.10);
    }
    .product-card .ours-badge {
        display: inline-block;
        padding: 0.1rem 0.45rem;
        border-radius: 8px;
        font-size: 0.68rem;
        font-weight: 700;
        background: #f59e0b;
        color: white;
        margin-left: 0.3rem;
    }

    /* 우리 매장 요약 박스 */
    .our-store-summary {
        padding: 1.2rem 1.5rem;
        border-radius: 14px;
        border: 2px solid rgba(245, 158, 11, 0.3);
        background: rgba(245, 158, 11, 0.05);
        margin-bottom: 1rem;
    }
    .our-store-summary h4 {
        margin: 0 0 0.8rem 0;
        font-size: 1rem;
        color: #b45309;
    }
    .our-store-row {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(245, 158, 11, 0.1);
    }
    .our-store-row:last-child { border-bottom: none; }
    .our-store-row .rank-num {
        font-size: 1.2rem;
        font-weight: 800;
        color: #f59e0b;
        min-width: 3rem;
        text-align: center;
    }
    .our-store-row .store-name {
        font-weight: 600;
        font-size: 0.9rem;
        flex: 1;
    }
    .our-store-row .store-price {
        font-size: 1.1rem;
        font-weight: 800;
        color: #b45309;
    }
    .our-store-row .store-product {
        font-size: 0.78rem;
        opacity: 0.6;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 250px;
    }
    .our-not-found {
        padding: 0.8rem 1.2rem;
        border-radius: 12px;
        background: rgba(128,128,128,0.05);
        border: 1px dashed rgba(128,128,128,0.2);
        text-align: center;
        font-size: 0.85rem;
        opacity: 0.6;
        margin-bottom: 1rem;
    }

    /* ── 순위 분석 카드 ── */
    .analysis-card {
        padding: 1rem 1.3rem;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.1);
        background: rgba(128,128,128,0.02);
        margin-bottom: 0.6rem;
    }
    .analysis-card .analysis-title {
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 0.4rem;
    }
    .analysis-card .analysis-body {
        font-size: 0.85rem;
        line-height: 1.7;
    }
    .action-item {
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
        padding: 0.6rem 0;
        border-bottom: 1px solid rgba(128,128,128,0.08);
        font-size: 0.85rem;
        line-height: 1.6;
    }
    .action-item:last-child { border-bottom: none; }
    .action-item .priority {
        display: inline-block;
        padding: 0.1rem 0.4rem;
        border-radius: 6px;
        font-size: 0.68rem;
        font-weight: 700;
        white-space: nowrap;
        min-width: 2.5rem;
        text-align: center;
    }
    .priority-high { background: #fef2f2; color: #dc2626; }
    .priority-mid { background: #fffbeb; color: #d97706; }
    .priority-low { background: #f0fdf4; color: #16a34a; }

    /* ── 리뷰 카드 ── */
    .review-card {
        padding: 0.9rem 1.2rem;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.1);
        background: rgba(128,128,128,0.02);
        margin-bottom: 0.5rem;
    }
    .review-card .rv-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.4rem;
        font-size: 0.82rem;
    }
    .review-card .rv-product {
        font-weight: 600;
        font-size: 0.85rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .review-card .rv-pros {
        font-size: 0.82rem;
        line-height: 1.6;
        padding: 0.3rem 0 0.3rem 0.8rem;
        border-left: 3px solid #22c55e;
        margin: 0.3rem 0;
    }
    .review-card .rv-cons {
        font-size: 0.82rem;
        line-height: 1.6;
        padding: 0.3rem 0 0.3rem 0.8rem;
        border-left: 3px solid #ef4444;
        margin: 0.3rem 0;
    }

    /* ── 우리 매장 상세 분석 ── */
    .detail-analysis-card {
        padding: 1.2rem 1.4rem;
        border-radius: 14px;
        border: 2px solid rgba(255, 154, 0, 0.2);
        background: linear-gradient(135deg, rgba(255,154,0,0.04) 0%, rgba(255,200,80,0.04) 100%);
        margin-bottom: 1rem;
    }
    .detail-analysis-card .da-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    .detail-analysis-card .da-thumb {
        width: 100px;
        height: 100px;
        border-radius: 10px;
        object-fit: cover;
        border: 1px solid rgba(128,128,128,0.15);
        flex-shrink: 0;
    }
    .detail-analysis-card .da-info h4 {
        margin: 0 0 0.3rem 0;
        font-size: 1rem;
    }
    .detail-analysis-card .da-info .da-meta {
        font-size: 0.8rem;
        opacity: 0.6;
        line-height: 1.5;
    }
    .detail-analysis-card .da-section {
        margin-top: 0.8rem;
        padding-top: 0.6rem;
        border-top: 1px solid rgba(128,128,128,0.1);
    }
    .detail-analysis-card .da-section h5 {
        margin: 0 0 0.4rem 0;
        font-size: 0.88rem;
        font-weight: 700;
    }
    .da-issue {
        display: flex;
        align-items: flex-start;
        gap: 0.4rem;
        font-size: 0.82rem;
        line-height: 1.6;
        margin-bottom: 0.2rem;
    }
    .da-issue .icon-warn { color: #ef4444; }
    .da-issue .icon-tip { color: #22c55e; }
    .da-issue .icon-info { color: #3b82f6; }
    .da-unit-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.8rem;
        margin-top: 0.5rem;
    }
    .da-unit-table th {
        text-align: left;
        padding: 0.35rem 0.5rem;
        background: rgba(128,128,128,0.06);
        font-weight: 600;
        border-bottom: 1px solid rgba(128,128,128,0.12);
    }
    .da-unit-table td {
        padding: 0.3rem 0.5rem;
        border-bottom: 1px solid rgba(128,128,128,0.06);
    }
    .da-unit-table tr.highlight td {
        background: rgba(255,154,0,0.08);
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 데이터 저장 경로
# ─────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

CEO_MSG_FILE = os.path.join(DATA_DIR, "ceo_message.json")
DAILY_LOG_FILE = os.path.join(DATA_DIR, "daily_logs.json")
SEARCH_HISTORY_FILE = os.path.join(DATA_DIR, "search_history.json")


# ─────────────────────────────────────────────
# 유틸 함수
# ─────────────────────────────────────────────
def load_json(filepath, default=None):
    if default is None:
        default = {}
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# 우리 매장명 목록
OUR_STORES = ["키니비니", "맘스베베", "키니비니 공식"]


def is_our_store(mall_name: str) -> bool:
    """판매처가 우리 매장인지 확인합니다."""
    if not mall_name:
        return False
    name_lower = mall_name.strip()
    return any(store in name_lower for store in OUR_STORES)


def format_won(value):
    """숫자를 한국 원화 형식으로 포맷합니다."""
    if value >= 100_000_000:
        return f"{value / 100_000_000:.1f}억원"
    elif value >= 10_000:
        return f"{value / 10_000:.0f}만원"
    return f"{value:,.0f}원"


# ─────────────────────────────────────────────
# 1. 네이버 쇼핑 검색 (API 우선 → 데모 폴백)
# ─────────────────────────────────────────────
def get_naver_api_keys() -> tuple:
    """st.secrets에서 네이버 API 키를 가져옵니다."""
    try:
        client_id = st.secrets["naver"]["client_id"]
        client_secret = st.secrets["naver"]["client_secret"]
        return client_id, client_secret
    except (KeyError, FileNotFoundError):
        return "", ""


@st.cache_data(ttl=300, show_spinner=False)
def search_naver_shopping_api(keyword: str, top_n: int = 5) -> pd.DataFrame:
    """네이버 쇼핑 검색 API를 사용하여 상품을 검색합니다."""
    client_id, client_secret = get_naver_api_keys()
    if not client_id:
        return pd.DataFrame()

    url = "https://openapi.naver.com/v1/search/shop.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }
    params = {"query": keyword, "display": min(top_n, 100), "sort": "sim"}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        st.error(f"네이버 API 요청 실패: {e}")
        return pd.DataFrame()

    products = []
    for i, item in enumerate(data.get("items", [])[:top_n], 1):
        # HTML 태그 제거
        title = item.get("title", "").replace("<b>", "").replace("</b>", "")
        products.append({
            "순위": i,
            "상품명": title[:60],
            "가격(원)": int(item.get("lprice", 0)),
            "판매처": item.get("mallName", "네이버쇼핑"),
            "링크": item.get("link", ""),
            "이미지": item.get("image", ""),
            "원본상품명": item.get("title", "").replace("<b>", "").replace("</b>", ""),
        })

    return pd.DataFrame(products) if products else pd.DataFrame()


def get_demo_data(keyword: str) -> pd.DataFrame:
    """API 키가 없을 때 데모 데이터를 반환합니다."""
    import random
    random.seed(hash(keyword) % 2**32)

    demo_products = {
        "피셔프라이스 아기체육관": [
            ("피셔프라이스 디럭스 아기 체육관 플레이매트", 45900, "쿠팡"),
            ("피셔프라이스 피아노 아기체육관 블루", 52000, "네이버쇼핑"),
            ("피셔프라이스 레인포레스트 디럭스 체육관", 48500, "11번가"),
            ("피셔프라이스 센서리 디럭스 짐 플레이매트", 55900, "G마켓"),
            ("피셔프라이스 뉴본 디럭스 아기체육관", 41200, "스마트스토어"),
        ],
        "도루코 면도기": [
            ("도루코 페이스 6플러스 면도기 세트", 12900, "쿠팡"),
            ("도루코 페이스 7 프로 면도기", 15800, "네이버쇼핑"),
            ("도루코 페이스 6 면도기 본체+리필 4개", 18500, "11번가"),
            ("도루코 클래식 양날 면도기 세트", 9900, "G마켓"),
            ("도루코 페이스 5 면도기 리필 8개입", 14200, "스마트스토어"),
        ],
        "유아 물티슈": [
            ("베베숲 시그니처 물티슈 캡형 80매 10팩", 15900, "쿠팡"),
            ("궁중비책 프리미엄 물티슈 80매 10팩", 17500, "네이버쇼핑"),
            ("보솜이 리얼코튼 물티슈 72매 10팩", 13800, "11번가"),
            ("마더케이 퓨어 물티슈 80매 10팩", 16200, "G마켓"),
            ("그린핑거 퓨어오가닉 물티슈 70매 10팩", 14500, "스마트스토어"),
        ],
        "아기 기저귀": [
            ("하기스 매직컴포트 밴드 3단계 66매", 23900, "쿠팡"),
            ("팸퍼스 베이비드라이 밴드 3단계 56매", 21500, "네이버쇼핑"),
            ("보솜이 리얼코튼 밴드 3단계 52매", 19800, "11번가"),
            ("하기스 네이처메이드 밴드 3단계 42매", 27500, "G마켓"),
            ("마미포코 에어핏 밴드 3단계 58매", 20900, "스마트스토어"),
        ],
    }

    if keyword in demo_products:
        items = demo_products[keyword]
    else:
        # 임의 키워드에 대한 동적 데모 데이터
        base_price = random.randint(8000, 80000)
        malls = ["쿠팡", "네이버쇼핑", "11번가", "G마켓", "스마트스토어"]
        items = []
        for i in range(5):
            variation = random.randint(-int(base_price * 0.2), int(base_price * 0.3))
            items.append((
                f"{keyword} 인기상품 {chr(65+i)}",
                base_price + variation,
                malls[i],
            ))

    products = []
    for i, (name, price, mall) in enumerate(items, 1):
        products.append({
            "순위": i,
            "상품명": name,
            "가격(원)": price,
            "판매처": mall,
            "링크": "#",
        })

    return pd.DataFrame(products)


def search_products(keyword: str) -> tuple:
    """
    네이버 API로 최대 100개 검색 → 실패 시 데모 데이터 반환.
    Returns: (DataFrame, is_demo: bool)
    """
    # 1) 네이버 API 시도 (최대 100개)
    df = search_naver_shopping_api(keyword, 100)
    if not df.empty:
        return df, False

    # 2) 데모 데이터 폴백
    return get_demo_data(keyword), True


# ─────────────────────────────────────────────
# 2. 원싱크(OneWMS) API 연동
# ─────────────────────────────────────────────
def get_onewms_keys() -> dict:
    """st.secrets에서 OneWMS API 키를 가져옵니다."""
    try:
        return {
            "partner_key": st.secrets["onewms"]["partner_key"],
            "domain_key": st.secrets["onewms"]["domain_key"],
            "api_url": st.secrets["onewms"]["api_url"],
        }
    except (KeyError, FileNotFoundError):
        return {}


def call_onewms_api(func_name: str, params: dict = None) -> dict:
    """OneWMS API를 호출합니다."""
    keys = get_onewms_keys()
    if not keys:
        return {"error": "API 키 미등록"}

    payload = {
        "partner_key": keys["partner_key"],
        "domain_key": keys["domain_key"],
        "action": func_name,
        "type": "product",
    }
    if params:
        payload.update(params)

    try:
        resp = requests.get(keys["api_url"], params=payload, timeout=15)
        resp.raise_for_status()
        result = resp.json()
        # 디버그: API 응답 구조 확인용 (st.session_state에 저장)
        if "onewms_debug" not in st.session_state:
            st.session_state["onewms_debug"] = {}
        st.session_state["onewms_debug"][func_name] = result
        return result
    except requests.RequestException as e:
        return {"error": str(e)}


def get_onesync_api_key() -> str:
    """OneWMS API 키 존재 여부를 확인합니다 (하위 호환)."""
    keys = get_onewms_keys()
    return keys.get("partner_key", "")


@st.cache_data(ttl=300, show_spinner=False)
def fetch_yesterday_sales() -> dict:
    """OneWMS API(get_order_info)로 어제 매출 데이터를 조회합니다."""
    keys = get_onewms_keys()
    if not keys:
        return {"total_sales": 0, "order_count": 0, "status": "미연동"}

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    day_before = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

    # 어제 주문 조회
    data = call_onewms_api("get_order_info", {
        "start_date": yesterday,
        "end_date": yesterday,
    })

    if data.get("error"):
        return {"total_sales": 0, "order_count": 0, "status": f"오류: {data['error']}"}

    orders = data.get("data", data.get("list", []))
    if not isinstance(orders, list):
        orders = []

    total_sales = 0
    order_count = len(orders)
    for order in orders:
        price = order.get("total_price", order.get("order_price", order.get("price", 0)))
        try:
            total_sales += int(float(str(price)))
        except (ValueError, TypeError):
            pass

    # 전일(그제) 주문 조회 (전일 대비 계산용)
    prev_data = call_onewms_api("get_order_info", {
        "start_date": day_before,
        "end_date": day_before,
    })
    prev_orders = prev_data.get("data", prev_data.get("list", []))
    if not isinstance(prev_orders, list):
        prev_orders = []
    prev_sales = 0
    prev_count = len(prev_orders)
    for order in prev_orders:
        price = order.get("total_price", order.get("order_price", order.get("price", 0)))
        try:
            prev_sales += int(float(str(price)))
        except (ValueError, TypeError):
            pass

    return {
        "total_sales": total_sales,
        "order_count": order_count,
        "prev_sales": prev_sales,
        "prev_count": prev_count,
        "status": "연동 완료",
    }


@st.cache_data(ttl=300, show_spinner=False)
def fetch_product_names() -> dict:
    """OneWMS API로 상품 ID → 상품명 매핑을 가져옵니다."""
    keys = get_onewms_keys()
    if not keys:
        return {}
    name_map = {}
    page = 1
    while True:
        data = call_onewms_api("get_product_info", {"type": "product", "page": str(page), "limit": "100"})
        if not isinstance(data, dict) or data.get("error"):
            break
        items = data.get("data", [])
        if not items:
            break
        for item in items:
            pid = item.get("product_id", "")
            name = item.get("name", pid)
            name_map[pid] = name
        if page * 100 >= int(data.get("total", 0)):
            break
        page += 1
    return name_map


@st.cache_data(ttl=300, show_spinner=False)
def fetch_current_inventory() -> dict:
    """OneWMS API(get_stock_tx_info)로 현재 재고 데이터를 조회합니다."""
    keys = get_onewms_keys()
    if not keys:
        return {"total_sku": 0, "low_stock_count": 0, "items": [], "low_items": [], "status": "미연동"}

    data = call_onewms_api("get_stock_tx_info", {"type": "product"})

    if isinstance(data, dict) and data.get("error"):
        return {"total_sku": 0, "low_stock_count": 0, "items": [], "low_items": [], "status": f"오류: {data['error']}"}

    # get_stock_tx_info 응답: {product_id: {warehouse: [[{job, job_type, qty}, ...]]}}
    all_items = []
    low_items = []
    for product_id, warehouses in data.items():
        if not isinstance(warehouses, dict):
            continue
        for wh_id, entries in warehouses.items():
            if not isinstance(entries, list) or not entries:
                continue
            for entry_group in entries:
                if not isinstance(entry_group, list):
                    continue
                stock_qty = 0
                trans_qty = 0
                for item in entry_group:
                    if item.get("job") == "stock":
                        try:
                            stock_qty = int(float(str(item.get("qty", 0))))
                        except (ValueError, TypeError):
                            pass
                    elif item.get("job") == "trans":
                        try:
                            trans_qty = int(float(str(item.get("qty", 0))))
                        except (ValueError, TypeError):
                            pass
                all_items.append({"product_id": product_id, "stock_qty": stock_qty, "trans_qty": trans_qty})
                if stock_qty <= 10:
                    low_items.append({"product_id": product_id, "stock_qty": stock_qty, "trans_qty": trans_qty})

    return {
        "total_sku": len(all_items),
        "low_stock_count": len(low_items),
        "items": all_items,
        "low_items": low_items,
        "status": "연동 완료",
    }


# ─────────────────────────────────────────────
# 2-1. 판매 인사이트 분석 (판매 대응 필요 상품 감지)
# ─────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_sales_insight() -> dict:
    """최근 5영업일 출고 패턴 분석 → 이상 징후 감지."""
    from collections import defaultdict
    keys = get_onewms_keys()
    if not keys:
        return {"anomalies": [], "daily_sellers": [], "status": "미연동"}

    today = datetime.now()
    # 최근 7일 범위 (주말 포함해서 넉넉하게)
    start = (today - timedelta(days=8)).strftime("%Y-%m-%d")
    yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")

    # 과거 출고 이력 수집
    all_trans = []
    for page in range(1, 30):
        data = call_onewms_api("get_stock_tx_detail_info", {
            "type": "product",
            "start_date": start,
            "end_date": yesterday,
            "limit": "100",
            "page": str(page),
        })
        items = data.get("data", [])
        if not items:
            break
        for item in items:
            if item.get("job") == "trans":
                all_trans.append(item)

    if not all_trans:
        return {"anomalies": [], "daily_sellers": [], "status": "데이터 없음"}

    # 영업일 추출 (실제 출고가 있었던 날)
    active_dates = sorted(set(item["crdate"][:10] for item in all_trans))
    # 최근 5영업일만
    work_days = active_dates[-5:] if len(active_dates) >= 5 else active_dates

    # 상품별 일별 출고 집계
    product_daily = defaultdict(lambda: defaultdict(int))
    for item in all_trans:
        product_daily[item["product_id"]][item["crdate"][:10]] += int(item.get("qty", 0))

    # 오늘 출고 상품
    today_data = call_onewms_api("get_stock_tx_info", {"type": "product"})
    today_products = set()
    if isinstance(today_data, dict):
        for pid, val in today_data.items():
            if isinstance(val, dict):
                today_products.add(pid)

    # 이상 징후: 최근 영업일 70%+ 출고했지만 오늘 미출고
    threshold = max(len(work_days) * 0.7, 2)
    anomalies = []
    daily_sellers = []
    for pid, days in product_daily.items():
        active_count = sum(1 for d in work_days if days.get(d, 0) > 0)
        total_qty = sum(days.get(d, 0) for d in work_days)
        avg_qty = total_qty / len(work_days) if work_days else 0

        daily_sellers.append({
            "product_id": pid,
            "active_days": active_count,
            "total_days": len(work_days),
            "total_qty": total_qty,
            "avg_qty": round(avg_qty, 1),
            "today_shipped": pid in today_products,
        })

        if active_count >= threshold and pid not in today_products:
            anomalies.append({
                "product_id": pid,
                "active_days": active_count,
                "total_days": len(work_days),
                "avg_qty": round(avg_qty, 1),
                "total_qty": total_qty,
            })

    anomalies.sort(key=lambda x: -x["avg_qty"])
    daily_sellers.sort(key=lambda x: (-x["active_days"], -x["avg_qty"]))

    return {
        "anomalies": anomalies,
        "daily_sellers": daily_sellers,
        "work_days": work_days,
        "today_count": len(today_products),
        "total_tracked": len(product_daily),
        "status": "분석 완료",
    }


# ─────────────────────────────────────────────
# 3. 순위 경쟁력 분석
# ─────────────────────────────────────────────
def analyze_ranking(df: pd.DataFrame, our_df: pd.DataFrame, keyword: str) -> list:
    """우리 매장의 순위 경쟁력을 분석하고 액션 아이템을 생성합니다."""
    actions = []
    top7 = df.head(7)
    top7_avg = top7["가격(원)"].mean()
    top7_min = top7["가격(원)"].min()
    overall_avg = df["가격(원)"].mean()

    if our_df.empty:
        actions.append({
            "priority": "high",
            "title": "상위 노출 미달",
            "body": f"'{keyword}' 검색 시 상위 100개 결과에 우리 매장이 없습니다. "
                    f"상위 7개 평균가는 {top7_avg:,.0f}원입니다. "
                    f"이 가격대에 맞는 상품 등록 및 키워드 최적화가 필요합니다.",
        })
        actions.append({
            "priority": "high",
            "title": "상품명 키워드 최적화",
            "body": f"상위 노출 상품들의 공통 키워드를 분석하세요. "
                    f"상품명에 '{keyword}' 핵심 키워드를 포함하고, "
                    f"'무료배송', '당일발송' 같은 혜택 키워드를 추가하세요.",
        })
        actions.append({
            "priority": "mid",
            "title": "초기 판매량 확보 전략",
            "body": f"네이버 쇼핑 순위는 판매 실적이 가장 중요합니다. "
                    f"초기 2~4주간 최저가({top7_min:,.0f}원) 이하로 가격을 설정하고, "
                    f"네이버 쇼핑 라이브나 기획전을 활용해 판매량을 빠르게 쌓으세요.",
        })
        actions.append({
            "priority": "mid",
            "title": "리뷰 확보 캠페인",
            "body": "포토/동영상 리뷰 작성 시 적립금(500~1,000원)을 제공하세요. "
                    "리뷰 50개 이상이면 검색 순위에 유의미한 영향을 줍니다. "
                    "특히 '한달사용기' 같은 장문 리뷰가 효과적입니다.",
        })
    else:
        for _, row in our_df.iterrows():
            rank = int(row["순위"])
            price = int(row["가격(원)"])
            store = row["판매처"]

            # 가격 경쟁력 분석
            price_diff = price - top7_avg
            if rank <= 7:
                actions.append({
                    "priority": "low",
                    "title": f"✅ {store} — {rank}위 (상위 노출 중)",
                    "body": f"현재 가격 {price:,.0f}원으로 상위 7위 안에 있습니다. "
                            f"현재 순위를 유지하면서 마진율을 점검하세요.",
                })
            elif rank <= 20:
                actions.append({
                    "priority": "mid",
                    "title": f"⬆️ {store} — {rank}위 → 상위 7위 진입 가능",
                    "body": f"현재 {price:,.0f}원 (상위 7개 평균 {top7_avg:,.0f}원). "
                            f"{'가격을 ' + format(top7_avg, ',.0f') + '원대로 낮추면 순위 상승 가능합니다.' if price_diff > 0 else '가격은 경쟁력 있습니다. 리뷰 수와 판매량을 늘리세요.'} "
                            f"네이버 쇼핑 광고(파워링크)도 병행하면 효과적입니다.",
                })
            else:
                actions.append({
                    "priority": "high",
                    "title": f"🔺 {store} — {rank}위 (순위 개선 시급)",
                    "body": f"현재 {price:,.0f}원으로 {rank}위입니다. "
                            f"상위 7개 최저가는 {top7_min:,.0f}원입니다. "
                            f"{'가격 경쟁력이 부족합니다. 최소 ' + format(int(top7_avg), ',.0f') + '원 이하로 조정을 검토하세요.' if price_diff > 0 else '가격은 낮지만 판매 실적과 리뷰가 부족할 수 있습니다.'} ",
                })

        # 공통 액션
        if our_df["순위"].min() > 7:
            actions.append({
                "priority": "mid",
                "title": "판매량 부스팅 전략",
                "body": f"네이버 쇼핑라이브 진행, 타임딜/쿠폰 이벤트, SNS 유입을 통해 "
                        f"단기 판매량을 집중적으로 올리세요. 판매 실적이 순위에 가장 큰 영향을 줍니다.",
            })
            actions.append({
                "priority": "low",
                "title": "상세페이지 품질 개선",
                "body": "상품 상세페이지에 사용 후기 사진, 비교표, FAQ를 추가하세요. "
                        "체류시간이 길어지면 네이버 알고리즘에서 긍정적으로 평가됩니다.",
            })

    return actions


# ─────────────────────────────────────────────
# 3-2. 우리 매장 상세 분석
# ─────────────────────────────────────────────
def analyze_product_title(title: str) -> dict:
    """상품명을 분석하여 문제점과 개선안을 제시합니다."""
    issues = []
    suggestions = []

    # 길이 체크
    if len(title) > 50:
        issues.append("상품명이 너무 깁니다 (50자 초과) — 검색결과에서 잘릴 수 있음")
    elif len(title) < 15:
        issues.append("상품명이 너무 짧습니다 — 검색 노출 키워드가 부족할 수 있음")

    # 관련 없는 키워드 스터핑 체크
    unrelated_patterns = [
        ("쉐이빙젤", "면도기"), ("쉐이빙폼", "면도기"), ("클렌징폼", "면도기"),
        ("로션", "면도기"), ("스킨", "면도기"), ("화장품", "기저귀"),
    ]
    for keyword, product_type in unrelated_patterns:
        if keyword in title and product_type in title.lower():
            issues.append(f"'{keyword}' — 실제 미포함 키워드 의심. 네이버 SEO 패널티 위험")

    # 스펙 정보 포함 여부
    has_count = any(c.isdigit() for c in title) and any(u in title for u in ["개", "입", "P", "EA", "매"])
    if not has_count:
        suggestions.append("수량 정보(예: 24개입)를 명시하면 클릭률 향상")

    spec_keywords = ["중날", "3중", "4중", "5중", "6중", "7중", "스테인리스", "윤활밴드"]
    has_spec = any(sk in title for sk in spec_keywords)
    if not has_spec:
        suggestions.append("제품 스펙(예: 3중날, 윤활밴드)을 추가하면 차별화 가능")

    usage_keywords = ["휴대용", "여행용", "업소용", "호텔용", "대용량"]
    has_usage = any(uk in title for uk in usage_keywords)
    if not has_usage:
        suggestions.append("용도 키워드(휴대용, 여행용 등)를 추가하면 타겟 검색 노출 증가")

    return {"issues": issues, "suggestions": suggestions}


def analyze_price_competitiveness(our_price: int, our_title: str, all_df) -> dict:
    """가격 경쟁력을 상세 분석합니다."""
    result = {}

    # 개당 가격 추산 시도
    count = extract_quantity(our_title)
    if count and count > 0:
        unit_price = our_price / count
        result["우리_개당가격"] = round(unit_price)
        result["우리_수량"] = count

        # 경쟁사 개당 가격 비교
        competitors = []
        for _, row in all_df.iterrows():
            if not is_our_store(row["판매처"]):
                comp_count = extract_quantity(row.get("원본상품명", row["상품명"]))
                if comp_count and comp_count > 0:
                    comp_unit = int(row["가격(원)"]) / comp_count
                    competitors.append({
                        "판매처": row["판매처"],
                        "가격": int(row["가격(원)"]),
                        "수량": comp_count,
                        "개당가격": round(comp_unit),
                        "순위": int(row["순위"]),
                    })
        result["경쟁사"] = sorted(competitors, key=lambda x: x["개당가격"])[:5]
    else:
        result["우리_개당가격"] = None

    return result


def extract_quantity(title: str) -> int:
    """상품명에서 수량을 추출합니다."""
    import re
    # "100개", "24개입", "10입", "40개", "17입" 등
    patterns = [
        r'(\d+)\s*개입',
        r'(\d+)\s*개',
        r'(\d+)\s*입',
        r'(\d+)\s*P\b',
        r'(\d+)\s*EA',
        r'(\d+)\s*매',
        r'X\s*(\d+)',
    ]
    quantities = []
    for p in patterns:
        matches = re.findall(p, title, re.IGNORECASE)
        for m in matches:
            q = int(m)
            if 1 < q <= 1000:
                quantities.append(q)
    # 가장 큰 수량 반환 (보통 총 수량)
    return max(quantities) if quantities else 0


def generate_thumbnail_analysis(image_url: str, product_name: str, rank: int) -> dict:
    """썸네일 이미지 URL 기반으로 분석 포인트를 생성합니다."""
    issues = []
    suggestions = []

    # 이미지 URL에서 힌트 추출
    if not image_url:
        issues.append("썸네일 이미지가 없음 — 클릭률에 매우 부정적")
        return {"issues": issues, "suggestions": ["고품질 대표 이미지 등록 필수"]}

    # 일반적인 썸네일 개선 가이드 (순위 기반)
    if rank > 30:
        issues.append("검색 순위가 낮아 노출 기회가 적음 — 썸네일 클릭률이 더욱 중요")
        suggestions.append("경쟁사 상위 상품 썸네일 스타일을 벤치마킹하세요")

    suggestions.append("제품 스펙 텍스트(수량, 중날수 등)를 이미지에 삽입")
    suggestions.append("흰색 배경 + 제품 확대 구도가 네이버 쇼핑에서 클릭률 최고")
    suggestions.append("패키지 사진보다 '제품 본체 + 스펙 텍스트' 조합이 효과적")

    return {"issues": issues, "suggestions": suggestions}


# ─────────────────────────────────────────────
# 3-3. ScraperAPI 기반 상세페이지 분석
# ─────────────────────────────────────────────
import re


def get_scraperapi_key() -> str:
    """st.secrets에서 ScraperAPI 키를 가져옵니다."""
    try:
        return st.secrets["scraperapi"]["api_key"]
    except (KeyError, FileNotFoundError):
        return ""


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_smartstore_detail(product_url: str) -> dict:
    """ScraperAPI를 통해 스마트스토어 상세페이지 데이터를 가져옵니다."""
    api_key = get_scraperapi_key()
    if not api_key:
        return {"error": "ScraperAPI 키 미등록"}

    api_url = f"http://api.scraperapi.com?api_key={api_key}&url={product_url}&country_code=kr"
    try:
        resp = requests.get(api_url, timeout=60)
        if resp.status_code != 200:
            return {"error": f"HTTP {resp.status_code}"}

        html = resp.text
        # __PRELOADED_STATE__ 파싱
        m = re.search(r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?)\s*</script>', html, re.DOTALL)
        if not m:
            return {"error": "페이지 데이터 추출 실패"}

        raw = m.group(1).rstrip().rstrip(';')
        raw = re.sub(r'\bundefined\b', 'null', raw)
        data = json.loads(raw)

        result = {}
        # 상품 기본 정보
        sp = data.get("simpleProductForDetailPage", {}).get("A", {})
        if sp:
            result["name"] = sp.get("name", "")
            result["id"] = sp.get("id", "")
            cat = sp.get("category", {})
            result["category"] = cat.get("wholeCategoryName", "") if cat else ""
            result["status"] = sp.get("channelProductDisplayStatusType", "")

        # 스토어 정보
        ch = data.get("channel", {})
        if ch:
            result["store_name"] = ch.get("channelName", "")
            result["store_url"] = ch.get("url", "")
            result["store_domain"] = ch.get("customDomain", "")
            imgs = ch.get("representImageInfoList", [])
            result["store_image"] = imgs[0].get("imageUrl", "") if imgs else ""

        # 리뷰 상태
        rv_summary = data.get("productReviewSummary", {}).get("A", {})
        result["review_display_type"] = rv_summary.get("reviewThumbnailDisplayType", "")

        # 리뷰 데이터
        rv = data.get("productReviews", {}).get("A", {})
        result["review_status"] = rv.get("status", "")

        return result
    except json.JSONDecodeError:
        return {"error": "JSON 파싱 실패"}
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# 4. 리뷰 분석 (네이버 블로그 검색 API 활용)
# ─────────────────────────────────────────────


@st.cache_data(ttl=600, show_spinner=False)
def fetch_blog_reviews(product_name: str, top_n: int = 5) -> list:
    """네이버 블로그 검색 API로 상품 리뷰를 가져옵니다."""
    client_id, client_secret = get_naver_api_keys()
    if not client_id:
        return []

    query = f"{product_name} 후기 리뷰"
    url = "https://openapi.naver.com/v1/search/blog.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }
    params = {"query": query, "display": top_n, "sort": "sim"}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            results = []
            for item in data.get("items", [])[:top_n]:
                title = item.get("title", "").replace("<b>", "").replace("</b>", "")
                desc = item.get("description", "").replace("<b>", "").replace("</b>", "")
                link = item.get("link", "")
                results.append({"title": title, "description": desc, "link": link})
            return results
    except Exception:
        pass
    return []


def analyze_blog_reviews(blog_results: list) -> dict:
    """블로그 리뷰 텍스트에서 장단점을 추출합니다."""
    pros = []
    cons = []

    positive_keywords = ["좋아", "만족", "추천", "최고", "훌륭", "편리", "가성비", "빠른", "깔끔",
                         "튼튼", "부드러", "좋은", "잘 ", "예쁘", "괜찮", "마음에", "가격대비",
                         "부드럽", "매끈", "시원", "깨끗", "든든", "확실", "놀라"]
    negative_keywords = ["별로", "아쉬", "불편", "느린", "비싸", "약한", "떨어", "부족", "냄새",
                         "고장", "하자", "실망", "불량", "얇은", "작은", "단점", "아프", "따가",
                         "무거", "불만", "문제"]

    for blog in blog_results:
        text = blog["title"] + " " + blog["description"]
        # 문장 분리
        sentences = re.split(r'[.!?~]\s*', text)
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 8 or len(sent) > 100:
                continue
            is_pro = any(kw in sent for kw in positive_keywords)
            is_con = any(kw in sent for kw in negative_keywords)
            if is_con and len(cons) < 3 and sent not in cons:
                cons.append(sent[:80])
            elif is_pro and len(pros) < 3 and sent not in pros:
                pros.append(sent[:80])

    review_count = len(blog_results)
    return {"pros": pros, "cons": cons, "count": review_count}


# ─────────────────────────────────────────────
# 검색 이력 관리
# ─────────────────────────────────────────────
def load_search_history() -> list:
    """검색 이력을 불러옵니다."""
    data = load_json(SEARCH_HISTORY_FILE, {"history": []})
    return data.get("history", [])


def save_search_history(history: list):
    """검색 이력을 저장합니다. 최대 20개 유지."""
    save_json(SEARCH_HISTORY_FILE, {"history": history[:20]})


def add_to_search_history(keyword: str):
    """키워드를 검색 이력 맨 앞에 추가합니다 (중복 제거)."""
    history = load_search_history()
    keyword = keyword.strip()
    if not keyword:
        return
    # 기존에 있으면 제거 후 맨 앞에 추가
    history = [h for h in history if h != keyword]
    history.insert(0, keyword)
    save_search_history(history[:20])


def remove_from_search_history(keyword: str):
    """키워드를 검색 이력에서 삭제합니다."""
    history = load_search_history()
    history = [h for h in history if h != keyword]
    save_search_history(history)


# ─────────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────────

# 세션 상태 초기화
if "active_keyword" not in st.session_state:
    st.session_state.active_keyword = None
if "delete_target" not in st.session_state:
    st.session_state.delete_target = None

# 삭제 처리 (콜백에서 플래그 세팅 → rerun 전에 처리)
if st.session_state.delete_target:
    remove_from_search_history(st.session_state.delete_target)
    st.session_state.delete_target = None

# ─────────────────────────────────────────────
# 브랜드 추출 유틸
# ─────────────────────────────────────────────
def extract_brand(product_name: str) -> str:
    """상품명에서 브랜드 추출 (첫 '-' 이전 텍스트)."""
    if "-" in product_name:
        return product_name.split("-")[0].strip()
    return "기타"


# ─────────────────────────────────────────────
# 판매처별 매출 조회
# ─────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_shop_list() -> dict:
    """판매처 목록을 가져옵니다."""
    data = call_onewms_api("get_etc_info", {"type": "product", "search_type": "shop"})
    if isinstance(data, dict) and data.get("error") == 0:
        return {item["code"]: item["name"] for item in data.get("data", [])}
    return {}


@st.cache_data(ttl=300, show_spinner=False)
def fetch_orders_by_date(date_str: str) -> list:
    """특정 날짜의 주문 데이터를 가져옵니다."""
    all_orders = []
    for page in range(1, 30):
        data = call_onewms_api("get_order_info", {
            "type": "product",
            "start_date": date_str,
            "end_date": date_str,
            "date_type": "order_date",
            "limit": "100",
            "page": str(page),
        })
        if not isinstance(data, dict) or data.get("error"):
            break
        orders = data.get("data", [])
        if not orders:
            break
        all_orders.extend(orders)
        if page * 100 >= int(data.get("total", 0)):
            break
    return all_orders


with st.sidebar:
    st.markdown("# 👶 신아인터네셔날")
    st.caption("ShinA International 업무 대시보드")
    st.markdown("---")

    # ── 메뉴 네비게이션 ──
    menu_items = {
        "📊 대시보드": "dashboard",
        "🚨 판매 대응": "sales_action",
        "📦 재고 현황": "inventory",
        "🛒 가격 모니터링": "price_monitor",
        "📝 업무 일지": "daily_log",
    }

    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"

    for label, page_id in menu_items.items():
        is_active = st.session_state.current_page == page_id
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, key=f"nav_{page_id}", use_container_width=True, type=btn_type):
            st.session_state.current_page = page_id
            st.rerun()

    st.markdown("---")

    # ── API 상태 ──
    st.markdown("#### 📡 연동 상태")
    naver_id, _ = get_naver_api_keys()
    if naver_id:
        st.caption("✅ 네이버 API")
    else:
        st.caption("🔸 네이버 API — 데모")

    onewms_keys = get_onewms_keys()
    if onewms_keys:
        st.caption("✅ 원싱크(OneWMS)")
    else:
        st.caption("🔸 원싱크 — 미연동")

    st.markdown("---")
    now = datetime.now()
    st.caption(f"📅 {now.strftime('%Y년 %m월 %d일')}  ⏰ {now.strftime('%H:%M')}")


# ─────────────────────────────────────────────
# 상세분석 팝업 (Dialog)
# ─────────────────────────────────────────────
@st.dialog("🔬 우리 매장 상품 상세 분석", width="large")
def show_detail_analysis(data: dict, all_df):
    """우리 매장 상품의 상세 분석을 팝업으로 표시합니다."""
    our_rank = data["rank"]
    our_price = data["price"]
    our_name = data["name"]
    our_image = data["image"]
    our_link = data["link"]
    our_mall = data["mall"]

    # 분석 실행
    title_analysis = analyze_product_title(our_name)
    price_analysis = analyze_price_competitiveness(our_price, our_name, all_df)
    thumb_analysis = generate_thumbnail_analysis(our_image, our_name, our_rank)

    # ScraperAPI로 상세페이지 추가 데이터 수집
    detail_data_extra = {}
    if our_link and our_link != "#":
        with st.spinner("상세페이지 분석 중..."):
            detail_data_extra = fetch_smartstore_detail(our_link)

    # 블로그 리뷰 수집
    blog_reviews = fetch_blog_reviews(our_name[:25], top_n=3)
    review_summary = analyze_blog_reviews(blog_reviews) if blog_reviews else {"pros": [], "cons": [], "count": 0}

    # ── 헤더: 썸네일 + 기본 정보 ──
    img_tag = f'<img src="{our_image}" alt="상품" style="width:90px; height:90px; border-radius:10px; object-fit:cover; border:1px solid rgba(128,128,128,0.15); flex-shrink:0;" />' if our_image else ""
    link_tag = f'<a href="{our_link}" target="_blank" style="font-size:0.78rem; opacity:0.6;">상품 페이지 열기 ↗</a>' if our_link != "#" else ""

    st.markdown(f'''<div style="display:flex; align-items:center; gap:1rem; margin-bottom:1rem;">
        {img_tag}
        <div style="min-width:0;">
            <h3 style="margin:0 0 0.3rem 0; font-size:1.1rem;">🏪 {our_mall} · {our_rank}위 · {our_price:,}원</h3>
            <div style="font-size:0.85rem; opacity:0.7; word-break:break-all;">{our_name}</div>
            <div>{link_tag}</div>
        </div>
    </div>''', unsafe_allow_html=True)

    st.divider()

    # ── 1. 썸네일 분석 ──
    st.markdown("##### 📸 썸네일 이미지 분석")
    for issue in thumb_analysis.get("issues", []):
        st.markdown(f"⚠️ {issue}")
    for sug in thumb_analysis.get("suggestions", []):
        st.markdown(f"💡 {sug}")

    st.divider()

    # ── 2. 상품명 분석 ──
    st.markdown("##### 📝 상품명 분석")
    if title_analysis["issues"]:
        for issue in title_analysis["issues"]:
            st.markdown(f"⚠️ {issue}")
    else:
        st.markdown("✅ 상품명 구성이 양호합니다.")
    for sug in title_analysis.get("suggestions", []):
        st.markdown(f"💡 {sug}")

    st.divider()

    # ── 3. 가격 경쟁력 ──
    st.markdown("##### 💰 가격 경쟁력 (개당 단가 비교)")
    if price_analysis.get("우리_개당가격"):
        our_unit = price_analysis["우리_개당가격"]
        our_qty = price_analysis["우리_수량"]
        st.markdown(f"📦 **우리: {our_price:,}원 ÷ {our_qty}개 = 개당 {our_unit:,}원**")

        comps = price_analysis.get("경쟁사", [])
        if comps:
            cheapest_comp = comps[0]
            if our_unit > cheapest_comp["개당가격"]:
                diff_val = our_unit - cheapest_comp["개당가격"]
                st.markdown(f"⚠️ 최저 경쟁사({cheapest_comp['판매처']})보다 개당 **{diff_val:,}원 비쌈**")
            else:
                diff_val = cheapest_comp["개당가격"] - our_unit
                st.markdown(f"✅ 최저 경쟁사보다 개당 **{diff_val:,}원 저렴** — 가격 우위!")

            # 비교 테이블
            table_rows = [{"순위": f"{our_rank}위 🏪", "판매처": our_mall, "가격": f"{our_price:,}원", "수량": f"{our_qty}개", "개당가격": f"{our_unit:,}원"}]
            for comp in comps[:4]:
                table_rows.append({
                    "순위": f"{comp['순위']}위",
                    "판매처": comp["판매처"],
                    "가격": f"{comp['가격']:,}원",
                    "수량": f"{comp['수량']}개",
                    "개당가격": f"{comp['개당가격']:,}원",
                })
            st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)
    else:
        st.markdown("ℹ️ 상품명에서 수량 정보를 추출할 수 없어 개당 가격 비교가 어렵습니다.")

    st.divider()

    # ── 4. 상세페이지 정보 (ScraperAPI) ──
    if detail_data_extra and not detail_data_extra.get("error"):
        st.markdown("##### 🏪 스마트스토어 상세 정보")
        info_cols = st.columns(2)
        with info_cols[0]:
            st.markdown(f"**스토어명:** {detail_data_extra.get('store_name', '-')}")
            st.markdown(f"**카테고리:** {detail_data_extra.get('category', '-')}")
            st.markdown(f"**판매상태:** {detail_data_extra.get('status', '-')}")
        with info_cols[1]:
            store_domain = detail_data_extra.get("store_domain", "")
            if store_domain:
                st.markdown(f"**자체 도메인:** {store_domain}")
            store_url = detail_data_extra.get("store_url", "")
            if store_url:
                st.markdown(f"**스토어 URL:** smartstore.naver.com/{store_url}")
            store_img = detail_data_extra.get("store_image", "")
            if store_img:
                st.image(store_img, width=80, caption="스토어 대표 이미지")
        st.divider()

    # ── 5. 블로그 리뷰 분석 ──
    if review_summary["pros"] or review_summary["cons"]:
        st.markdown("##### 💬 블로그 리뷰 장단점")
        rv_cols = st.columns(2)
        with rv_cols[0]:
            st.markdown("**장점**")
            for p in review_summary["pros"]:
                st.markdown(f"👍 {p}")
            if not review_summary["pros"]:
                st.caption("추출된 장점 없음")
        with rv_cols[1]:
            st.markdown("**단점**")
            for c in review_summary["cons"]:
                st.markdown(f"👎 {c}")
            if not review_summary["cons"]:
                st.caption("추출된 단점 없음")
        # 블로그 원문 링크
        if blog_reviews:
            st.markdown("**출처:**")
            for b in blog_reviews[:2]:
                st.markdown(f"[📝 {b['title'][:40]}...]({b['link']})")
        st.divider()

    # ── 6. 즉시 실행 액션 플랜 ──
    st.markdown("##### 🎯 즉시 실행 액션 플랜")
    action_items = []
    if thumb_analysis.get("issues"):
        action_items.append("🔴 **썸네일 이미지 교체** — 제품 스펙이 보이는 디자인 이미지로 교체 (수량, 특징 텍스트 삽입)")
    if title_analysis.get("issues"):
        action_items.append("🔴 **상품명 수정** — 관련 없는 키워드 제거, 실제 스펙 키워드로 교체")
    if price_analysis.get("우리_개당가격") and price_analysis.get("경쟁사"):
        cheapest_comp = price_analysis["경쟁사"][0]
        if price_analysis["우리_개당가격"] > cheapest_comp["개당가격"]:
            action_items.append(f"🟡 **가격 재검토** — 개당 단가를 {cheapest_comp['개당가격']:,}원 이하로 낮출 수 있는 묶음 구성 고려")
    action_items.append("🟡 **리뷰 확보** — 구매 후 포토리뷰 작성 시 적립금 500~1,000원 제공")
    action_items.append("🟢 **상세페이지 보강** — 비교표, 사용 후기 사진, FAQ 추가로 체류시간 증가")

    for item in action_items:
        st.markdown(item)



# ─────────────────────────────────────────────
# 메인 - 헤더 배너
# ─────────────────────────────────────────────
today = datetime.now()
weekdays = ["월", "화", "수", "목", "금", "토", "일"]
weekday_kr = weekdays[today.weekday()]

st.markdown(f"""
<div class="header-banner">
    <div class="logo">👶</div>
    <div>
        <h1>신아인터네셔날 업무 대시보드</h1>
        <p>실시간 가격 모니터링 · 매출/재고 현황 · 업무 일지</p>
    </div>
    <div class="header-right">
        <div class="date">{today.strftime('%Y.%m.%d')} ({weekday_kr})</div>
        <div>{today.strftime('%H:%M')} 기준</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════
# 페이지 라우팅
# ═════════════════════════════════════════════
current_page = st.session_state.get("current_page", "dashboard")


# ─────────────────────────────────────────────
# 📊 대시보드 (메인 요약 페이지)
# ─────────────────────────────────────────────
if current_page == "dashboard":
    # CEO 지시 사항
    ceo_data = load_json(CEO_MSG_FILE, {"message": "", "updated": ""})
    if ceo_data.get("message"):
        st.markdown(f"""
        <div class="ceo-strategy-box">
            <div class="badge">CEO STRATEGY</div>
            <h3>📋 오늘의 전략</h3>
            <div class="content">{ceo_data['message'].replace(chr(10), '<br>')}</div>
            <div class="meta">최종 수정: {ceo_data.get('updated', '-')}</div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("✏️ CEO 지시사항 수정 (관리자 전용)", expanded=False):
        new_msg = st.text_area(
            "오늘의 전략 / 지시사항",
            value=ceo_data.get("message", ""),
            height=100,
            placeholder="직원들에게 전달할 오늘의 전략을 입력하세요...",
        )
        if st.button("💾 지시사항 저장", type="primary"):
            ceo_data = {
                "message": new_msg,
                "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            save_json(CEO_MSG_FILE, ceo_data)
            st.success("저장되었습니다!")
            st.rerun()

    # ── 오늘 요약 KPI ──
    st.markdown('<div class="section-title"><span class="icon">📊</span> 오늘 현황 요약</div>', unsafe_allow_html=True)

    sales_data = fetch_yesterday_sales()
    inventory_data = fetch_current_inventory()

    sales_connected = sales_data["status"] == "연동 완료"
    inv_connected = inventory_data["status"] == "연동 완료"
    sales_error = "오류" in sales_data.get("status", "")

    # 매출 KPI (독립)
    if sales_connected:
        sales_diff = sales_data["total_sales"] - sales_data.get("prev_sales", 0)
        count_diff = sales_data["order_count"] - sales_data.get("prev_count", 0)
        sales_diff_text = f"{'▲' if sales_diff >= 0 else '▼'} {format_won(abs(sales_diff))}" if sales_data.get("prev_sales") else "전일 대비"
        count_diff_text = f"{'▲' if count_diff >= 0 else '▼'} {abs(count_diff)}건" if sales_data.get("prev_count") is not None else "전일 대비"
        sales_kpi = [
            {"icon": "💰", "label": "어제 총 매출", "value": format_won(sales_data['total_sales']), "sub": sales_diff_text},
            {"icon": "📦", "label": "어제 주문 건수", "value": f"{sales_data['order_count']}건", "sub": count_diff_text},
        ]
    else:
        sales_kpi = [
            {"icon": "💰", "label": "어제 총 매출", "value": "—", "sub": "API 미연동"},
            {"icon": "📦", "label": "어제 주문 건수", "value": "—", "sub": "API 미연동"},
        ]

    # 재고 KPI (독립)
    product_names = fetch_product_names()
    total_all_sku = len(product_names)

    if inv_connected:
        inv_kpi = [
            {"icon": "🏷️", "label": "총 SKU 수", "value": f"{total_all_sku}개", "sub": "관리 중"},
            {"icon": "📦", "label": "오늘 출고 품목", "value": f"{inventory_data['total_sku']}개", "sub": "오늘 변동"},
            {"icon": "⚠️", "label": "재고 부족 품목", "value": f"{inventory_data['low_stock_count']}개", "sub": "10개 이하"},
        ]
    else:
        inv_kpi = [
            {"icon": "🏷️", "label": "총 SKU 수", "value": f"{total_all_sku}개" if total_all_sku else "—", "sub": "관리 중"},
            {"icon": "📦", "label": "오늘 출고 품목", "value": "—", "sub": "오늘 변동"},
            {"icon": "⚠️", "label": "재고 부족 품목", "value": "—", "sub": "긴급 확인 필요"},
        ]

    kpi_items = sales_kpi + inv_kpi

    cols = st.columns(len(kpi_items))
    for col, item in zip(cols, kpi_items):
        col.markdown(f"""
        <div class="kpi-card">
            <div class="icon">{item['icon']}</div>
            <div class="label">{item['label']}</div>
            <div class="value">{item['value']}</div>
            <div class="sub">{item['sub']}</div>
        </div>
        """, unsafe_allow_html=True)

    if sales_error:
        st.warning(f"⚠️ 매출 API 오류: {sales_data['status']} (주문 API 권한 확인 필요)")
    if not inv_connected and "오류" in inventory_data.get("status", ""):
        st.warning(f"⚠️ 재고 API 오류: {inventory_data['status']}")

    # ── 판매 대응 필요 상품 요약 ──
    st.markdown('<div class="section-title"><span class="icon">🚨</span> 판매 대응 필요 상품</div>', unsafe_allow_html=True)

    insight_data = fetch_sales_insight()

    if insight_data["status"] == "분석 완료":
        anomalies = insight_data["anomalies"]
        daily_sellers = insight_data["daily_sellers"]
        dormant_count = len([s for s in daily_sellers if not s["today_shipped"]])

        # 요약 카드
        ins_cols = st.columns(4)
        ins_cols[0].markdown(f"""
        <div class="kpi-card">
            <div class="icon">📊</div>
            <div class="label">최근 출고 상품</div>
            <div class="value">{insight_data['total_tracked']}개</div>
            <div class="sub">최근 5영업일</div>
        </div>
        """, unsafe_allow_html=True)
        ins_cols[1].markdown(f"""
        <div class="kpi-card">
            <div class="icon">📦</div>
            <div class="label">오늘 출고</div>
            <div class="value">{insight_data['today_count']}개</div>
            <div class="sub">현재까지</div>
        </div>
        """, unsafe_allow_html=True)
        anomaly_color = "#f5576c" if anomalies else "#22c55e"
        ins_cols[2].markdown(f"""
        <div class="kpi-card" style="border-color: {anomaly_color}40;">
            <div class="icon">🚨</div>
            <div class="label">판매 대응 필요</div>
            <div class="value" style="color: {anomaly_color};">{len(anomalies)}개</div>
            <div class="sub">매일 출고 → 오늘 0</div>
        </div>
        """, unsafe_allow_html=True)
        ins_cols[3].markdown(f"""
        <div class="kpi-card">
            <div class="icon">💤</div>
            <div class="label">오늘 미출고</div>
            <div class="value">{dormant_count}개</div>
            <div class="sub">최근 출고 이력 有</div>
        </div>
        """, unsafe_allow_html=True)

        # 대시보드에서는 간단 요약만 표시
        if anomalies:
            product_names_map = fetch_product_names()
            st.markdown(f"**판매 대응 필요 {len(anomalies)}개 상품** — 상세 내용은 '판매 대응' 메뉴에서 확인하세요.")
            for item in anomalies[:5]:
                pid = item["product_id"]
                name = product_names_map.get(pid, pid)
                brand = extract_brand(name)
                severity = "🔴" if item["avg_qty"] >= 10 else ("🟡" if item["avg_qty"] >= 3 else "🟠")
                st.markdown(f"- {severity} **[{brand}]** {name} — 일평균 {item['avg_qty']}개, 오늘 0개")
            if len(anomalies) > 5:
                st.caption(f"...외 {len(anomalies) - 5}개 상품")
        else:
            st.success("✅ 판매 대응 필요 상품 없음 — 매일 출고 상품이 오늘도 정상 출고 중입니다.")
    elif insight_data["status"] != "미연동":
        st.info(f"📊 판매 인사이트: {insight_data['status']}")

    # ── 브랜드별 오늘 출고 현황 (CEO 관점) ──
    if inv_connected:
        st.markdown('<div class="section-title"><span class="icon">📈</span> 브랜드별 오늘 출고 현황</div>', unsafe_allow_html=True)
        brand_summary = {}
        for item in inventory_data.get("items", []):
            pid = item["product_id"]
            name = product_names.get(pid, pid)
            brand = extract_brand(name)
            if brand not in brand_summary:
                brand_summary[brand] = {"품목수": 0, "총출고": 0, "부족": 0}
            brand_summary[brand]["품목수"] += 1
            brand_summary[brand]["총출고"] += abs(item["trans_qty"])
            if item["stock_qty"] <= 10:
                brand_summary[brand]["부족"] += 1

        if brand_summary:
            brand_rows = []
            for brand, info in sorted(brand_summary.items(), key=lambda x: -x[1]["총출고"]):
                brand_rows.append({
                    "브랜드": brand,
                    "출고 품목수": info["품목수"],
                    "총 출고량": info["총출고"],
                    "재고 부족": f"{info['부족']}개" if info["부족"] else "—",
                })
            st.dataframe(pd.DataFrame(brand_rows), use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────
# 🚨 판매 대응 페이지
# ─────────────────────────────────────────────
elif current_page == "sales_action":
    st.markdown('<div class="section-title"><span class="icon">🚨</span> 판매 대응 필요 상품</div>', unsafe_allow_html=True)

    insight_data = fetch_sales_insight()
    product_names_map = fetch_product_names()
    shop_list = fetch_shop_list()

    if insight_data["status"] == "분석 완료":
        anomalies = insight_data["anomalies"]
        daily_sellers = insight_data["daily_sellers"]
        dormant_count = len([s for s in daily_sellers if not s["today_shipped"]])

        # 요약 KPI 카드
        ins_cols = st.columns(4)
        ins_cols[0].markdown(f"""
        <div class="kpi-card">
            <div class="icon">📊</div>
            <div class="label">최근 출고 상품</div>
            <div class="value">{insight_data['total_tracked']}개</div>
            <div class="sub">최근 5영업일</div>
        </div>
        """, unsafe_allow_html=True)
        ins_cols[1].markdown(f"""
        <div class="kpi-card">
            <div class="icon">📦</div>
            <div class="label">오늘 출고</div>
            <div class="value">{insight_data['today_count']}개</div>
            <div class="sub">현재까지</div>
        </div>
        """, unsafe_allow_html=True)
        anomaly_color = "#f5576c" if anomalies else "#22c55e"
        ins_cols[2].markdown(f"""
        <div class="kpi-card" style="border-color: {anomaly_color}40;">
            <div class="icon">🚨</div>
            <div class="label">판매 대응 필요</div>
            <div class="value" style="color: {anomaly_color};">{len(anomalies)}개</div>
            <div class="sub">매일 출고 → 오늘 0</div>
        </div>
        """, unsafe_allow_html=True)
        ins_cols[3].markdown(f"""
        <div class="kpi-card">
            <div class="icon">💤</div>
            <div class="label">오늘 미출고</div>
            <div class="value">{dormant_count}개</div>
            <div class="sub">최근 출고 이력 有</div>
        </div>
        """, unsafe_allow_html=True)

        # ── 판매처별 주문 데이터 수집 (최근 7일, 캐시) ──
        from collections import defaultdict, Counter

        @st.cache_data(ttl=300, show_spinner=False)
        def _build_order_product_shops(_shop_list_tuple):
            """주문 데이터를 집계하여 {product_id: {shop_name: {qty, amount, order_count, shop_product_ids}}} 반환"""
            shop_dict = dict(_shop_list_tuple)
            result = {}
            for days_ago in range(1, 8):
                date_str = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
                orders = fetch_orders_by_date(date_str)
                for order in orders:
                    shop_id = order.get("shop_id", "")
                    if not shop_id:
                        continue
                    shop_name = shop_dict.get(shop_id, shop_id)
                    shop_product_id = order.get("shop_product_id", "")
                    order_products = order.get("order_products", [])
                    if isinstance(order_products, list):
                        for op in order_products:
                            pid = op.get("product_id", "")
                            qty = 1
                            try:
                                qty = int(float(str(op.get("qty", 1))))
                            except (ValueError, TypeError):
                                pass
                            prd_amount = 0
                            try:
                                prd_amount = int(float(str(op.get("prd_amount", 0))))
                            except (ValueError, TypeError):
                                pass
                            if pid:
                                if pid not in result:
                                    result[pid] = {}
                                if shop_name not in result[pid]:
                                    result[pid][shop_name] = {"qty": 0, "shop_product_ids": [], "amount": 0, "order_count": 0}
                                info = result[pid][shop_name]
                                info["qty"] += qty
                                info["amount"] += prd_amount
                                info["order_count"] += 1
                                if shop_product_id and shop_product_id not in info["shop_product_ids"]:
                                    info["shop_product_ids"].append(shop_product_id)
            return result

        order_product_shops = _build_order_product_shops(tuple(sorted(shop_list.items())))

        # 판매처 URL 생성 헬퍼
        def build_shop_url(shop_name: str, shop_product_id: str) -> str:
            sn = shop_name.lower()
            if "스토어팜" in shop_name or "네이버" in sn:
                if "맘스베베" in shop_name:
                    return f"https://smartstore.naver.com/momsbebe/products/{shop_product_id}"
                elif "키니비니" in shop_name:
                    return f"https://smartstore.naver.com/kinibini/products/{shop_product_id}"
                elif "키니공식" in shop_name:
                    return f"https://smartstore.naver.com/kinibini_official/products/{shop_product_id}"
                return f"https://smartstore.naver.com/main/products/{shop_product_id}"
            elif "11번가" in shop_name:
                return f"https://www.11st.co.kr/products/{shop_product_id}"
            elif "쿠팡" in shop_name:
                return f"https://www.coupang.com/vp/products/{shop_product_id}"
            elif "g마켓" in sn:
                return f"https://item.gmarket.co.kr/Item?goodscode={shop_product_id}"
            elif "옥션" in shop_name:
                return f"https://itempage3.auction.co.kr/DetailView.aspx?ItemNo={shop_product_id}"
            elif "롯데" in shop_name:
                return f"https://www.lotteon.com/p/product/{shop_product_id}"
            elif "신세계" in shop_name or "이마트" in shop_name or "ssg" in sn:
                return f"https://www.ssg.com/item/itemView.ssg?itemId={shop_product_id}"
            elif "카카오" in shop_name:
                return f"https://store.kakao.com/products/{shop_product_id}"
            elif "토스" in shop_name:
                return f"https://commerce.toss.im/products/{shop_product_id}"
            return ""

        # 판매처 팝업 데이터 준비 헬퍼
        def _prepare_shop_data(pid, name, item=None):
            pid_shops = order_product_shops.get(pid, {})
            if not pid_shops:
                return None
            sorted_shops = sorted(pid_shops.items(), key=lambda x: -x[1]["qty"])
            all_shops_data = []
            for s_name, s_info in sorted_shops:
                urls = [build_shop_url(s_name, spid) for spid in s_info["shop_product_ids"] if build_shop_url(s_name, spid)]
                all_shops_data.append({"name": s_name, "qty": s_info["qty"], "amount": s_info["amount"], "order_count": s_info["order_count"], "urls": urls})
            # 요약 정보
            brand = extract_brand(name)
            avg_qty = item.get("avg_qty", 0) if item else 0
            today_shipped = item.get("today_shipped", False) if item else None
            shop_summary = " · ".join([f"{sn} {si['qty']}개" for sn, si in sorted_shops[:3]])
            return {
                "product_name": name, "product_id": pid, "shops": all_shops_data,
                "brand": brand, "avg_qty": avg_qty, "today_shipped": today_shipped,
                "shop_summary": shop_summary,
            }

        # 판매처 상세 팝업
        @st.dialog("🛒 판매처별 판매 현황", width="large")
        def show_shop_detail_dialog():
            data = st.session_state.get("_shop_detail_data", {})
            if not data:
                st.warning("데이터를 불러올 수 없습니다.")
                return

            p_name = data.get("product_name", "")
            p_id = data.get("product_id", "")
            brand = data.get("brand", "")
            avg_qty = data.get("avg_qty", 0)
            today_shipped = data.get("today_shipped")
            shop_summary = data.get("shop_summary", "")
            shops_info = data.get("shops", [])
            total_qty = sum(s["qty"] for s in shops_info)
            total_amount = sum(s["amount"] for s in shops_info)
            total_orders = sum(s["order_count"] for s in shops_info)

            # ── 상단 요약 영역 ──
            today_badge = ""
            if today_shipped is True:
                today_badge = " · ✅ 오늘출고"
            elif today_shipped is False:
                today_badge = " · ❌ 미출고"
            summary_line = f"**{brand}** | {p_name} — 일평균 **{avg_qty}개**{today_badge}"
            if shop_summary:
                summary_line += f" | 🛒 {shop_summary}"
            st.markdown(summary_line)
            st.divider()

            # ── KPI 지표 ──
            hc = st.columns(4)
            hc[0].metric("상품코드", p_id)
            hc[1].metric("총 판매수량", f"{total_qty}개")
            hc[2].metric("총 주문건수", f"{total_orders}건")
            hc[3].metric("총 매출액", f"{total_amount:,}원")

            # ── 판매처 테이블 ──
            rows = []
            for shop in shops_info:
                pct = round(shop["qty"] / total_qty * 100, 1) if total_qty else 0
                url_text = shop["urls"][0] if shop["urls"] else ""
                rows.append({
                    "판매처": shop["name"], "판매수량": shop["qty"], "점유율(%)": pct,
                    "주문건수": shop["order_count"], "매출액": shop["amount"], "상품URL": url_text,
                })
            st.dataframe(
                pd.DataFrame(rows), use_container_width=True, hide_index=True,
                column_config={
                    "판매처": st.column_config.TextColumn("판매처", width="medium"),
                    "판매수량": st.column_config.NumberColumn("판매수량", format="%d개"),
                    "점유율(%)": st.column_config.ProgressColumn("점유율", min_value=0, max_value=100, format="%.0f%%"),
                    "주문건수": st.column_config.NumberColumn("주문건수", format="%d건"),
                    "매출액": st.column_config.NumberColumn("매출액", format="%d원"),
                    "상품URL": st.column_config.LinkColumn("상품페이지", display_text="열기 ↗"),
                },
                height=min(len(rows) * 40 + 60, 400),
            )

        # ── 상품 리스트 렌더링 헬퍼 (4개 탭 공용) ──
        def _render_product_list(products, tab_prefix, show_today_col=False):
            """products: list of dict — 테이블 + selectbox → 판매처 팝업"""
            if not products:
                st.info("해당 상품이 없습니다.")
                return

            # 테이블 데이터 구성
            table_rows = []
            product_map = {}  # "상품코드 | 상품명" → item
            for item in products:
                pid = item["product_id"]
                name = product_names_map.get(pid, pid)
                brand = extract_brand(name)
                row = {
                    "브랜드": brand,
                    "상품코드": pid,
                    "상품명": name,
                    "일평균": item.get("avg_qty", 0),
                    "출고일수": f"{item.get('active_days', 0)}/{item.get('total_days', 7)}일",
                }
                if show_today_col:
                    row["오늘출고"] = "✅" if item.get("today_shipped") else "❌"
                table_rows.append(row)
                product_map[f"{pid} | {name}"] = item

            df = pd.DataFrame(table_rows)

            col_config = {
                "브랜드": st.column_config.TextColumn("브랜드", width="small"),
                "상품코드": st.column_config.TextColumn("상품코드", width="small"),
                "상품명": st.column_config.TextColumn("상품명", width="large"),
                "일평균": st.column_config.NumberColumn("일평균", format="%d개"),
                "출고일수": st.column_config.TextColumn("출고일수", width="small"),
            }
            if show_today_col:
                col_config["오늘출고"] = st.column_config.TextColumn("오늘출고", width="small")

            # 테이블 표시
            st.dataframe(
                df, use_container_width=True, hide_index=True,
                column_config=col_config,
                height=min(len(table_rows) * 35 + 60, 600),
            )

            # 상품 선택 → 판매처 상세 팝업
            sel_cols = st.columns([4, 1])
            with sel_cols[0]:
                options = list(product_map.keys())
                selected = st.selectbox(
                    "🔍 상품 선택 (판매처 상세 보기)",
                    options=[""] + options,
                    format_func=lambda x: "상품을 선택하세요..." if x == "" else x,
                    key=f"{tab_prefix}_select",
                    label_visibility="collapsed",
                )
            with sel_cols[1]:
                btn_disabled = (selected == "" or selected not in product_map)
                if st.button("📊 판매처 상세", key=f"{tab_prefix}_btn", use_container_width=True, disabled=btn_disabled):
                    sel_item = product_map[selected]
                    sel_pid = sel_item["product_id"]
                    sel_name = product_names_map.get(sel_pid, sel_pid)
                    shop_data = _prepare_shop_data(sel_pid, sel_name, sel_item)
                    if shop_data:
                        st.session_state["_shop_detail_data"] = shop_data
                        show_shop_detail_dialog()
                    else:
                        st.toast(f"{sel_name}: 최근 7일 주문 데이터 없음")

        # ═══ 4개 탭 ═══
        tab_all, tab_today, tab_anomaly, tab_dormant = st.tabs([
            f"📊 전체 출고 상품 ({insight_data['total_tracked']})",
            f"📦 오늘 출고 ({insight_data['today_count']})",
            f"🚨 판매 대응 필요 ({len(anomalies)})",
            f"💤 오늘 미출고 ({dormant_count})",
        ])

        with tab_all:
            all_sorted = sorted(daily_sellers, key=lambda x: (-x["active_days"], -x["avg_qty"]))
            _render_product_list(all_sorted, "tab_all", show_today_col=True)

        with tab_today:
            shipped = sorted([s for s in daily_sellers if s["today_shipped"]], key=lambda x: -x["avg_qty"])
            if shipped:
                _render_product_list(shipped, "tab_today")
            else:
                st.info("오늘 출고된 상품이 아직 없습니다.")

        with tab_anomaly:
            if anomalies:
                anomaly_sorted = sorted(anomalies, key=lambda x: (extract_brand(product_names_map.get(x["product_id"], "")), -x.get("avg_qty", 0)))
                _render_product_list(anomaly_sorted, "tab_anom")
            else:
                st.success("✅ 판매 대응 필요 상품 없음 — 매일 출고 상품이 오늘도 정상 출고 중입니다.")

        with tab_dormant:
            dormant_list = sorted([s for s in daily_sellers if not s["today_shipped"]], key=lambda x: (-x["active_days"], -x["avg_qty"]))
            if dormant_list:
                _render_product_list(dormant_list, "tab_dorm")
            else:
                st.success("✅ 모든 상품이 오늘 정상 출고되었습니다.")

    elif insight_data["status"] == "미연동":
        st.info("📡 원싱크(OneWMS) API 연동 후 판매 대응 분석이 가능합니다.")
    else:
        st.info(f"📊 판매 인사이트: {insight_data['status']}")


# ─────────────────────────────────────────────
# 📦 재고 현황 페이지
# ─────────────────────────────────────────────
elif current_page == "inventory":
    st.markdown('<div class="section-title"><span class="icon">📦</span> 재고 현황</div>', unsafe_allow_html=True)

    product_names = fetch_product_names()
    total_all_sku = len(product_names)
    inventory_data = fetch_current_inventory()
    inv_connected = inventory_data["status"] == "연동 완료"

    # KPI 요약
    inv_cols = st.columns(4)
    inv_cols[0].markdown(f"""
    <div class="kpi-card">
        <div class="icon">🏷️</div>
        <div class="label">총 SKU 수</div>
        <div class="value">{total_all_sku}개</div>
        <div class="sub">관리 중</div>
    </div>
    """, unsafe_allow_html=True)
    inv_cols[1].markdown(f"""
    <div class="kpi-card">
        <div class="icon">📦</div>
        <div class="label">오늘 출고 품목</div>
        <div class="value">{inventory_data['total_sku']}개</div>
        <div class="sub">오늘 변동</div>
    </div>
    """, unsafe_allow_html=True)
    inv_cols[2].markdown(f"""
    <div class="kpi-card">
        <div class="icon">⚠️</div>
        <div class="label">재고 부족 품목</div>
        <div class="value">{inventory_data['low_stock_count']}개</div>
        <div class="sub">10개 이하</div>
    </div>
    """, unsafe_allow_html=True)
    # 브랜드 수 계산
    all_brands = set()
    for name in product_names.values():
        all_brands.add(extract_brand(name))
    inv_cols[3].markdown(f"""
    <div class="kpi-card">
        <div class="icon">🏷️</div>
        <div class="label">브랜드 수</div>
        <div class="value">{len(all_brands)}개</div>
        <div class="sub">활성 브랜드</div>
    </div>
    """, unsafe_allow_html=True)

    # ── 보기 모드 선택 ──
    view_mode = st.radio("보기 모드", ["전체 SKU", "오늘 출고 상품", "재고 부족 품목", "브랜드별 요약"], horizontal=True)

    if view_mode == "전체 SKU":
        st.markdown(f"**총 {total_all_sku}개 SKU 등록**")
        stock_map = {}
        for item in inventory_data.get("items", []):
            stock_map[item["product_id"]] = item
        rows = []
        for pid, name in sorted(product_names.items(), key=lambda x: x[1]):
            brand = extract_brand(name)
            stock_info = stock_map.get(pid)
            if stock_info:
                rows.append({"브랜드": brand, "상품코드": pid, "상품명": name, "재고수량": stock_info["stock_qty"], "출고량": stock_info["trans_qty"], "오늘변동": "O"})
            else:
                rows.append({"브랜드": brand, "상품코드": pid, "상품명": name, "재고수량": "—", "출고량": "—", "오늘변동": ""})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=600)

    elif view_mode == "오늘 출고 상품":
        items = inventory_data.get("items", [])
        items_sorted = sorted(items, key=lambda x: product_names.get(x["product_id"], x["product_id"]))
        st.markdown(f"**오늘 변동 {len(items_sorted)}개 품목**")
        rows = []
        for item in items_sorted:
            pid = item["product_id"]
            name = product_names.get(pid, pid)
            brand = extract_brand(name)
            status = "🔴 부족" if item["stock_qty"] <= 10 else ("🟡 주의" if item["stock_qty"] <= 30 else "🟢 정상")
            rows.append({"브랜드": brand, "상품코드": pid, "상품명": name, "재고수량": item["stock_qty"], "출고량": item["trans_qty"], "상태": status})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=600)

    elif view_mode == "재고 부족 품목":
        low = inventory_data.get("low_items", [])
        low_sorted = sorted(low, key=lambda x: x["stock_qty"])
        st.markdown(f"**총 {len(low_sorted)}개 품목** — 긴급 발주 검토 필요")
        rows = []
        for item in low_sorted:
            pid = item["product_id"]
            name = product_names.get(pid, pid)
            brand = extract_brand(name)
            if item["stock_qty"] < 0:
                status = "⛔ 마이너스"
            elif item["stock_qty"] == 0:
                status = "🔴 품절"
            else:
                status = "🔴 부족"
            rows.append({"브랜드": brand, "상품코드": pid, "상품명": name, "재고수량": item["stock_qty"], "출고량": item["trans_qty"], "상태": status})
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
                          column_config={"재고수량": st.column_config.NumberColumn(format="%d개")},
                          height=600)
        else:
            st.success("✅ 재고 부족 품목이 없습니다.")

    elif view_mode == "브랜드별 요약":
        from collections import defaultdict
        brand_inv = defaultdict(lambda: {"품목수": 0, "출고품목": 0, "총출고": 0, "부족": 0, "품절": 0})
        for pid, name in product_names.items():
            brand = extract_brand(name)
            brand_inv[brand]["품목수"] += 1
        stock_map = {}
        for item in inventory_data.get("items", []):
            stock_map[item["product_id"]] = item
        for pid, name in product_names.items():
            brand = extract_brand(name)
            stock_info = stock_map.get(pid)
            if stock_info:
                brand_inv[brand]["출고품목"] += 1
                brand_inv[brand]["총출고"] += abs(stock_info["trans_qty"])
                if stock_info["stock_qty"] <= 0:
                    brand_inv[brand]["품절"] += 1
                elif stock_info["stock_qty"] <= 10:
                    brand_inv[brand]["부족"] += 1

        rows = []
        for brand, info in sorted(brand_inv.items(), key=lambda x: -x[1]["총출고"]):
            rows.append({
                "브랜드": brand,
                "총 SKU": info["품목수"],
                "오늘 출고 품목": info["출고품목"],
                "총 출고량": info["총출고"],
                "재고 부족": info["부족"],
                "품절": info["품절"],
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────
# 🛒 가격 모니터링 페이지
# ─────────────────────────────────────────────
elif current_page == "price_monitor":
    st.markdown('<div class="section-title"><span class="icon">🛒</span> 실시간 가격 모니터링 (네이버 쇼핑)</div>', unsafe_allow_html=True)

    # 검색 폼 (메인 영역에 배치)
    search_col1, search_col2 = st.columns([4, 1])
    with search_col1:
        search_keyword = st.text_input("🔍 검색 키워드", value="", placeholder="검색할 상품 키워드를 입력하세요...", label_visibility="collapsed")
    with search_col2:
        search_btn = st.button("🔍 검색", type="primary", use_container_width=True)

    # 빠른 검색 버튼
    quick_keywords = ["맘스베베 기저귀", "키니비니 면도기", "일회용 면도기", "아기 물티슈"]
    qk_cols = st.columns(len(quick_keywords))
    for i, kw in enumerate(quick_keywords):
        if qk_cols[i].button(kw, key=f"quick_{i}", use_container_width=True):
            search_keyword = kw
            search_btn = True

    # 검색 이력
    history = load_search_history()
    if history:
        st.caption("최근 검색: " + " · ".join(history[:5]))

    active_keyword = search_keyword if search_btn and search_keyword else st.session_state.get("active_keyword")

    if search_btn and search_keyword:
        add_to_search_history(search_keyword)
        st.session_state.active_keyword = search_keyword

    if active_keyword:
        with st.spinner(f"'{active_keyword}' 검색 중..."):
            df, is_demo = search_products(active_keyword)

        if not df.empty:
            if is_demo:
                st.info(
                    "📌 **데모 모드** — 네이버 API 키 등록 후 실제 데이터를 조회할 수 있습니다.  \n"
                    "`.streamlit/secrets.toml`에 `[naver]` > `client_id`, `client_secret`을 등록하세요.",
                )

            # 우리 매장 / 경쟁사 분리
            df["우리매장"] = df["판매처"].apply(is_our_store)
            our_df = df[df["우리매장"]].copy()
            top7_df = df.head(7)
            total_searched = len(df)

            min_price = df["가격(원)"].min()
            max_price = df["가격(원)"].max()
            avg_price = df["가격(원)"].mean()
            cheapest = df.loc[df["가격(원)"].idxmin()]

            # ── 우리 매장 현황 ──
            our_col, summary_col = st.columns([3, 2])

            with our_col:
                if not our_df.empty:
                    rows_html = ""
                    for _, row in our_df.iterrows():
                        rank = int(row["순위"])
                        price = int(row["가격(원)"])
                        link = row.get("링크", "#")
                        has_link = link and link != "#"
                        name_linked = f'<a href="{link}" target="_blank" style="color:inherit; text-decoration:none;">{row["상품명"][:45]} ↗</a>' if has_link else row["상품명"][:45]
                        diff = price - avg_price
                        diff_text = f"평균 대비 {abs(diff):,.0f}원 {'비쌈' if diff > 0 else '저렴'}" if diff != 0 else "평균가 동일"
                        url_html = ""
                        if has_link:
                            short_url = link[:55] + "..." if len(link) > 55 else link
                            url_html = f'<div style="font-size:0.7rem; opacity:0.4; margin-top:0.15rem;"><a href="{link}" target="_blank" style="color:inherit; text-decoration:none;">🔗 {short_url}</a></div>'
                        rows_html += f'<div class="our-store-row"><div class="rank-num">{rank}위</div><div style="flex:1; min-width:0;"><div class="store-name">🏪 {row["판매처"]}</div><div class="store-product">{name_linked}</div><div style="font-size:0.72rem; opacity:0.5;">{diff_text}</div>{url_html}</div><div class="store-price">{price:,.0f}원</div></div>'

                    full_html = f'<div class="our-store-summary"><h4>🏪 우리 매장 현황 — 상위 {total_searched}개 중 {len(our_df)}개 상품 발견</h4>{rows_html}</div>'
                    st.markdown(full_html, unsafe_allow_html=True)

                    # 상세분석 버튼
                    btn_cols = st.columns(len(our_df))
                    for idx, (_, our_row) in enumerate(our_df.iterrows()):
                        with btn_cols[idx]:
                            btn_label = f"🔬 {our_row['판매처']} · {int(our_row['순위'])}위 상세분석"
                            if st.button(btn_label, key=f"detail_{idx}", use_container_width=True):
                                st.session_state[f"show_detail_{idx}"] = True
                                st.session_state[f"detail_data_{idx}"] = {
                                    "rank": int(our_row["순위"]),
                                    "price": int(our_row["가격(원)"]),
                                    "name": our_row.get("원본상품명", our_row["상품명"]),
                                    "image": our_row.get("이미지", ""),
                                    "link": our_row.get("링크", "#"),
                                    "mall": our_row["판매처"],
                                }
                                st.rerun()
                else:
                    st.markdown(f'<div class="our-not-found">🔍 상위 {total_searched}개 결과에서 우리 매장(키니비니, 맘스베베, 키니비니 공식)이 발견되지 않았습니다.</div>', unsafe_allow_html=True)

            with summary_col:
                summary_html = f'<div class="price-summary" style="flex-direction:column;"><div class="price-summary-item lowest"><div class="label">🏷️ 최저가</div><div class="value">{min_price:,.0f}원</div><div class="sub">{cheapest["판매처"]}</div></div><div class="price-summary-item average" style="margin-top:0.5rem;"><div class="label">📊 평균가</div><div class="value">{avg_price:,.0f}원</div><div class="sub">상위 {total_searched}개 상품 기준 · 편차 {max_price - min_price:,.0f}원</div></div></div>'
                st.markdown(summary_html, unsafe_allow_html=True)

            st.markdown("")

            # ── 상위 상품 리스트 + 차트 ──
            list_col, chart_col = st.columns([3, 2])

            with list_col:
                st.markdown(f"**상위 {len(top7_df)}개 상품**")
                for _, row in top7_df.iterrows():
                    rank = int(row["순위"])
                    rank_class = " top1" if rank == 1 else ""
                    price = int(row["가격(원)"])
                    is_lowest = price == min_price
                    price_class = " lowest" if is_lowest else ""
                    link = row.get("링크", "#")
                    has_link = link and link != "#"
                    ours = row["우리매장"]
                    card_class = " ours" if ours else ""

                    if has_link:
                        name_html = f'<a href="{link}" target="_blank">{row["상품명"]} ↗</a>'
                    else:
                        name_html = row["상품명"]

                    ours_badge = '<span class="ours-badge">우리매장</span>' if ours else ""

                    link_text = ""
                    if has_link:
                        short_url = link[:45] + "..." if len(link) > 45 else link
                        link_text = f'<a href="{link}" target="_blank" style="opacity:0.4; font-size:0.7rem; text-decoration:none;">🔗 {short_url}</a>'

                    card_html = f'<div class="product-card{card_class}"><div class="rank{rank_class}">{rank}</div><div class="info"><div class="name">{name_html}{ours_badge}</div><div class="meta-row"><span class="mall-badge">{row["판매처"]}</span>{link_text}</div></div><div class="price{price_class}">{price:,.0f}원</div></div>'
                    st.markdown(card_html, unsafe_allow_html=True)

            with chart_col:
                chart_df = top7_df.copy()
                bar_colors = ['#f59e0b' if is_our_store(m) else '#667eea' for m in chart_df["판매처"]]

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=chart_df["상품명"].str[:18],
                    x=chart_df["가격(원)"],
                    text=[f"{p:,.0f}원" for p in chart_df["가격(원)"]],
                    textposition="outside",
                    orientation="h",
                    marker=dict(color=bar_colors, cornerradius=6),
                    hovertemplate="<b>%{y}</b><br>가격: %{x:,.0f}원<extra></extra>",
                ))
                fig.update_layout(
                    title=dict(text="가격 비교 (🟠 우리매장)", font=dict(size=13)),
                    xaxis=dict(title="", gridcolor="rgba(128,128,128,0.1)"),
                    yaxis=dict(title="", autorange="reversed"),
                    height=320,
                    margin=dict(t=40, b=20, l=10, r=60),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(size=11),
                )
                st.plotly_chart(fig, use_container_width=True)

            # ── 순위 경쟁력 분석 ──
            st.markdown('<div class="section-title"><span class="icon">📈</span> 순위 경쟁력 분석</div>', unsafe_allow_html=True)

            actions = analyze_ranking(df, our_df, active_keyword)
            if actions:
                for act in actions:
                    p = act["priority"]
                    p_label = {"high": "긴급", "mid": "권장", "low": "참고"}.get(p, "참고")
                    p_class = f"priority-{p}"
                    act_html = f'<div class="action-item"><span class="priority {p_class}">{p_label}</span><div><strong>{act["title"]}</strong><br>{act["body"]}</div></div>'
                    st.markdown(act_html, unsafe_allow_html=True)
            else:
                st.caption("분석 데이터가 부족합니다.")

            # ── 상위 상품 리뷰 분석 ──
            st.markdown('<div class="section-title"><span class="icon">💬</span> 상위 상품 리뷰 분석 (장단점)</div>', unsafe_allow_html=True)

            with st.spinner("블로그 리뷰 수집 중..."):
                review_results = []
                for _, row in top7_df.iterrows():
                    product_name = row["상품명"][:30]
                    blogs = fetch_blog_reviews(product_name, top_n=3)
                    summary = analyze_blog_reviews(blogs)
                    review_results.append({
                        "rank": int(row["순위"]),
                        "name": row["상품명"][:40],
                        "mall": row["판매처"],
                        "price": int(row["가격(원)"]),
                        "summary": summary,
                        "blogs": blogs,
                    })

            has_any = any(r["summary"]["pros"] or r["summary"]["cons"] for r in review_results)
            if has_any:
                for rv in review_results:
                    s = rv["summary"]
                    if not s["pros"] and not s["cons"]:
                        continue
                    pros_html = ""
                    if s["pros"]:
                        pros_list = "".join(f"<div>👍 {p}</div>" for p in s["pros"])
                        pros_html = f'<div class="rv-pros">{pros_list}</div>'
                    cons_html = ""
                    if s["cons"]:
                        cons_list = "".join(f"<div>👎 {c}</div>" for c in s["cons"])
                        cons_html = f'<div class="rv-cons">{cons_list}</div>'
                    ours_tag = ' <span class="ours-badge">우리매장</span>' if is_our_store(rv["mall"]) else ""
                    blog_links = ""
                    for b in rv.get("blogs", [])[:2]:
                        blog_links += f'<a href="{b["link"]}" target="_blank" style="font-size:0.72rem; opacity:0.5; text-decoration:none; margin-right:0.5rem;">📝 {b["title"][:30]}...</a>'
                    card = f'<div class="review-card"><div class="rv-header"><strong>{rv["rank"]}위</strong> <span class="mall-badge">{rv["mall"]}</span>{ours_tag} · {rv["price"]:,}원</div><div class="rv-product">{rv["name"]}</div>{pros_html}{cons_html}<div style="margin-top:0.4rem;">{blog_links}</div></div>'
                    st.markdown(card, unsafe_allow_html=True)
            else:
                st.caption("리뷰 데이터를 충분히 수집하지 못했습니다.")

        else:
            st.warning("검색 결과가 없습니다. 다른 키워드로 시도해보세요.")
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">🔍</div>
            <p>키워드를 입력하고 검색 버튼을 눌러주세요.</p>
        </div>
        """, unsafe_allow_html=True)

    # 팝업 트리거 처리
    for _idx in range(10):
        if st.session_state.get(f"show_detail_{_idx}"):
            detail_data = st.session_state.get(f"detail_data_{_idx}", {})
            if detail_data and active_keyword:
                _df, _ = search_products(active_keyword)
                show_detail_analysis(detail_data, _df)
            st.session_state[f"show_detail_{_idx}"] = False
            break


# ─────────────────────────────────────────────
# 📝 업무 일지 페이지
# ─────────────────────────────────────────────
elif current_page == "daily_log":
    st.markdown('<div class="section-title"><span class="icon">📝</span> 업무 일지 (Daily Log)</div>', unsafe_allow_html=True)

    today_str = datetime.now().strftime("%Y-%m-%d")
    all_logs = load_json(DAILY_LOG_FILE, {})
    today_logs = all_logs.get(today_str, [])

    col_form, col_logs = st.columns([3, 2])

    with col_form:
        with st.form("daily_log_form", clear_on_submit=True):
            form_top = st.columns([1, 2])
            with form_top[0]:
                writer = st.selectbox("작성자", ["MD", "CS", "CEO", "기타"])
            with form_top[1]:
                st.markdown(f"<div style='padding-top:1.6rem; font-size:0.85rem; opacity:0.5;'>📅 {today_str} 기록</div>", unsafe_allow_html=True)

            notable = st.text_area(
                "🔔 오늘의 특이사항",
                height=70,
                placeholder="오늘 발생한 특이사항을 기록하세요...",
            )
            competitor = st.text_area(
                "🏪 경쟁사 동향",
                height=70,
                placeholder="경쟁사 가격 변동, 프로모션 등...",
            )
            action = st.text_area(
                "✅ 조치 사항",
                height=70,
                placeholder="취한 조치 또는 필요한 조치...",
            )
            submitted = st.form_submit_button(
                "💾 업무 일지 저장",
                type="primary",
                use_container_width=True,
            )

            if submitted:
                if not (notable or competitor or action):
                    st.warning("최소 하나의 항목을 입력해주세요.")
                else:
                    new_entry = {
                        "작성자": writer,
                        "시간": datetime.now().strftime("%H:%M"),
                        "오늘의 특이사항": notable,
                        "경쟁사 동향": competitor,
                        "조치 사항": action,
                    }
                    today_logs.append(new_entry)
                    all_logs[today_str] = today_logs
                    save_json(DAILY_LOG_FILE, all_logs)
                    st.success("업무 일지가 저장되었습니다!")
                    st.rerun()

    with col_logs:
        st.markdown(f"**오늘의 기록** · {len(today_logs)}건")

        if today_logs:
            for log in reversed(today_logs):
                role = log['작성자']
                role_class = {"MD": "role-md", "CS": "role-cs", "CEO": "role-ceo"}.get(role, "role-etc")

                parts = []
                if log.get("오늘의 특이사항"):
                    parts.append(f'<div class="log-label">🔔 특이사항</div><div class="log-item">{log["오늘의 특이사항"]}</div>')
                if log.get("경쟁사 동향"):
                    parts.append(f'<div class="log-label">🏪 경쟁사</div><div class="log-item">{log["경쟁사 동향"]}</div>')
                if log.get("조치 사항"):
                    parts.append(f'<div class="log-label">✅ 조치</div><div class="log-item">{log["조치 사항"]}</div>')

                st.markdown(f"""
                <div class="log-entry">
                    <div class="log-header">
                        <span class="role-badge {role_class}">{role}</span>
                        <span style="opacity:0.5; font-size:0.8rem;">{log['시간']}</span>
                    </div>
                    {''.join(parts)}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state" style="padding:1.5rem;">
                <div class="icon">📋</div>
                <p>오늘 작성된 업무 일지가 없습니다.</p>
            </div>
            """, unsafe_allow_html=True)

        # 과거 일지 열람
        st.markdown("---")
        past_dates = sorted([d for d in all_logs.keys() if d != today_str], reverse=True)
        if past_dates:
            sel_date = st.selectbox("📂 과거 일지 조회", past_dates, label_visibility="visible")
            if sel_date:
                past_logs = all_logs[sel_date]
                for log in past_logs:
                    role = log['작성자']
                    role_class = {"MD": "role-md", "CS": "role-cs", "CEO": "role-ceo"}.get(role, "role-etc")
                    summary_parts = []
                    if log.get("오늘의 특이사항"):
                        summary_parts.append(log["오늘의 특이사항"][:40])
                    if log.get("경쟁사 동향"):
                        summary_parts.append(log["경쟁사 동향"][:40])
                    if log.get("조치 사항"):
                        summary_parts.append(log["조치 사항"][:40])
                    st.markdown(f"""
                    <div class="log-entry" style="padding:0.7rem 1rem;">
                        <div class="log-header" style="margin-bottom:0.2rem;">
                            <span class="role-badge {role_class}">{role}</span>
                            <span style="opacity:0.5; font-size:0.8rem;">{log['시간']}</span>
                        </div>
                        <div style="font-size:0.82rem; opacity:0.7;">{'  |  '.join(summary_parts)}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.caption("과거 기록이 없습니다.")


# ─────────────────────────────────────────────
# 푸터 (모든 페이지 공통)
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
    신아인터네셔날(ShinA) 업무 대시보드 v2.0 · {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</div>
""", unsafe_allow_html=True)
