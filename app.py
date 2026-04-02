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
from datetime import datetime, timedelta, timezone
import uuid
import calendar

KST = timezone(timedelta(hours=9))

# ─────────────────────────────────────────────
# 페이지 기본 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="신아인터네셔날 업무 대시보드",
    page_icon="🏷️",
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
        width: 56px; height: 56px;
        border-radius: 50%;
        background: linear-gradient(135deg, #e8192c 0%, #ff4757 100%);
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        box-shadow: 0 3px 12px rgba(232,25,44,0.3);
        flex-shrink: 0;
    }
    .header-banner .logo .kb-text {
        font-size: 0.55rem; font-weight: 900;
        color: #fff; letter-spacing: 1.5px;
        line-height: 1; text-transform: uppercase;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    .header-banner .logo .kb-sub {
        font-size: 0.3rem; color: rgba(255,255,255,0.85);
        letter-spacing: 0.5px; margin-top: 1px;
    }
    .sidebar-logo {
        width: 44px; height: 44px;
        border-radius: 50%;
        background: linear-gradient(135deg, #e8192c 0%, #ff4757 100%);
        display: inline-flex; flex-direction: column;
        align-items: center; justify-content: center;
        box-shadow: 0 2px 8px rgba(232,25,44,0.25);
        vertical-align: middle; margin-right: 8px;
    }
    .sidebar-logo .kb-text {
        font-size: 0.45rem; font-weight: 900;
        color: #fff; letter-spacing: 1.2px;
        line-height: 1; text-transform: uppercase;
    }
    .sidebar-logo .kb-sub {
        font-size: 0.25rem; color: rgba(255,255,255,0.8);
        letter-spacing: 0.3px; margin-top: 1px;
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
        padding: 0.35rem 0.5rem;
        border-radius: 8px;
        border: 1px solid rgba(128,128,128,0.12);
        background: rgba(128,128,128,0.03);
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .kpi-card .icon { font-size: 0.95rem; margin-bottom: 0.1rem; }
    .kpi-card .label { font-size: 0.65rem; opacity: 0.6; margin-bottom: 0.1rem; }
    .kpi-card .value { font-size: 1.05rem; font-weight: 800; }
    .kpi-card .sub { font-size: 0.58rem; opacity: 0.5; margin-top: 0.05rem; }
    .kpi-card.pending .value { opacity: 0.35; font-size: 0.85rem; }

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
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
STICKY_FILE = os.path.join(DATA_DIR, "sticky_notes.json")
SEARCH_HISTORY_FILE = os.path.join(DATA_DIR, "search_history.json")


# ─────────────────────────────────────────────
# GitHub Gist 기반 클라우드 데이터 영속성
# ─────────────────────────────────────────────
def _get_gist_config():
    """GitHub Gist 설정을 반환. 설정 없으면 None."""
    try:
        token = st.secrets["github"]["gist_token"]
        gist_id = st.secrets["github"]["gist_id"]
        return {"token": token, "gist_id": gist_id}
    except (KeyError, FileNotFoundError):
        return None


def _gist_restore_all():
    """앱 시작 시 GitHub Gist에서 모든 데이터 파일 복원."""
    if st.session_state.get("_gist_restored"):
        return
    cfg = _get_gist_config()
    if not cfg:
        st.session_state["_gist_restored"] = True
        return
    try:
        resp = requests.get(
            f"https://api.github.com/gists/{cfg['gist_id']}",
            headers={"Authorization": f"token {cfg['token']}"},
            timeout=10,
        )
        if resp.status_code == 200:
            files = resp.json().get("files", {})
            for fname, fdata in files.items():
                local_path = os.path.join(DATA_DIR, fname)
                if not os.path.exists(local_path) or os.path.getsize(local_path) == 0:
                    with open(local_path, "w", encoding="utf-8") as f:
                        f.write(fdata["content"])
    except Exception:
        pass
    st.session_state["_gist_restored"] = True


def _gist_backup(filepath):
    """파일 변경 시 GitHub Gist에 백업 (백그라운드 스레드)."""
    import threading
    cfg = _get_gist_config()
    if not cfg:
        return
    fname = os.path.basename(filepath)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return

    def _upload():
        try:
            requests.patch(
                f"https://api.github.com/gists/{cfg['gist_id']}",
                headers={"Authorization": f"token {cfg['token']}"},
                json={"files": {fname: {"content": content}}},
                timeout=10,
            )
        except Exception:
            pass

    threading.Thread(target=_upload, daemon=True).start()


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
    _gist_backup(filepath)


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


@st.cache_data(ttl=600, show_spinner=False)
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
        return resp.json()
    except requests.RequestException as e:
        return {"error": str(e)}


def get_onesync_api_key() -> str:
    """OneWMS API 키 존재 여부를 확인합니다 (하위 호환)."""
    keys = get_onewms_keys()
    return keys.get("partner_key", "")


@st.cache_data(ttl=600, show_spinner=False)
def fetch_yesterday_sales() -> dict:
    """OneWMS API(get_order_info)로 어제 매출 데이터를 조회합니다."""
    keys = get_onewms_keys()
    if not keys:
        return {"total_sales": 0, "order_count": 0, "status": "미연동"}

    yesterday = (datetime.now(KST) - timedelta(days=1)).strftime("%Y-%m-%d")
    day_before = (datetime.now(KST) - timedelta(days=2)).strftime("%Y-%m-%d")

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


@st.cache_data(ttl=1800, show_spinner=False)
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


@st.cache_data(ttl=1800, show_spinner=False)
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
# 2-0. 상품 재발굴 분석 (장기 무출고 상품 분류)
# ─────────────────────────────────────────────
@st.cache_data(ttl=21600, show_spinner=False)
def fetch_slow_moving_products() -> dict:
    """전체 상품 대비 출고 이력 분석 → 부진 등급 4단계 분류.

    등급:
      - remind (리마인드): 30~89일 무출고
      - review (재점검): 90~179일 무출고
      - rediscover (재발굴): 180~364일 무출고
      - convert (전환검토): 365일+ 무출고 or 출고 이력 없음
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    keys = get_onewms_keys()
    if not keys:
        return {"status": "미연동", "tiers": {}, "total_products": 0, "total_slow": 0}

    # 1) 전체 상품 목록
    all_products = fetch_product_names()
    if not all_products:
        return {"status": "상품 없음", "tiers": {}, "total_products": 0, "total_slow": 0}

    # 2) 재고 수량 매핑
    inv = fetch_current_inventory()
    stock_map = {}
    for item in inv.get("items", []):
        pid = item.get("product_id", "")
        qty = item.get("stock_qty", 0)
        # 같은 product_id가 여러 창고에 있을 수 있으므로 합산
        stock_map[pid] = stock_map.get(pid, 0) + qty

    today = datetime.now(KST)

    # 3) 분기별 출고 이력 병렬 수집 (4분기 = 365일)
    def _fetch_quarter_trans(start_str, end_str):
        """한 분기 출고 이력에서 상품별 최종 출고일 수집."""
        product_dates = {}
        for page in range(1, 80):
            data = call_onewms_api("get_stock_tx_detail_info", {
                "type": "product",
                "start_date": start_str,
                "end_date": end_str,
                "limit": "100",
                "page": str(page),
            })
            items = data.get("data", [])
            if not items:
                break
            for item in items:
                if item.get("job") == "trans":
                    pid = item.get("product_id", "")
                    d = item.get("crdate", "")[:10]
                    if pid and d:
                        if pid not in product_dates or d > product_dates[pid]:
                            product_dates[pid] = d
        return product_dates

    # 4분기 날짜 범위 생성
    quarters = []
    for i in range(4):
        q_end = today - timedelta(days=i * 91)
        q_start = today - timedelta(days=(i + 1) * 91)
        quarters.append((q_start.strftime("%Y-%m-%d"), q_end.strftime("%Y-%m-%d")))

    # 병렬 수집
    last_sale = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(_fetch_quarter_trans, s, e): i for i, (s, e) in enumerate(quarters)}
        for future in as_completed(futures):
            try:
                quarter_data = future.result()
                for pid, d in quarter_data.items():
                    if pid not in last_sale or d > last_sale[pid]:
                        last_sale[pid] = d
            except Exception:
                pass

    # 4) 등급 분류 (단종 상품 별도 분리)
    tiers = {"remind": [], "review": [], "rediscover": [], "convert": [], "discontinued": []}

    for pid, pname in all_products.items():
        stock_qty = stock_map.get(pid, 0)

        # "단" 또는 "(단)" 포함 상품 = 단종
        _pname_stripped = pname.strip()
        _is_discontinued = "(단)" in _pname_stripped or (
            _pname_stripped.startswith("단") and (
                len(_pname_stripped) == 1
                or _pname_stripped[1] in ("-", "_", " ", ")")
                or not _pname_stripped[1].isalpha()
            )
        )

        if pid in last_sale:
            try:
                last_date = datetime.strptime(last_sale[pid], "%Y-%m-%d").replace(tzinfo=KST)
                days_since = (today - last_date).days
            except ValueError:
                days_since = 999
        else:
            days_since = 999  # 365일 범위 내 출고 이력 없음

        item = {
            "product_id": pid,
            "product_name": pname,
            "last_sale": last_sale.get(pid),
            "days_since": days_since,
            "stock_qty": stock_qty,
        }

        # 단종 상품은 판매일과 무관하게 별도 분류
        if _is_discontinued:
            tiers["discontinued"].append(item)
            continue

        if days_since < 30:
            continue  # 최근 판매 — 정상 상품

        if days_since < 90:
            tiers["remind"].append(item)
        elif days_since < 180:
            tiers["review"].append(item)
        elif days_since < 365:
            tiers["rediscover"].append(item)
        else:
            tiers["convert"].append(item)

    # 건수 많은 순 정렬 (days_since 내림차순)
    for key in tiers:
        tiers[key].sort(key=lambda x: -x["days_since"])

    _slow_count = sum(len(v) for k, v in tiers.items() if k != "discontinued")
    return {
        "status": "분석 완료",
        "total_products": len(all_products),
        "total_slow": _slow_count,
        "total_discontinued": len(tiers["discontinued"]),
        "tiers": tiers,
    }


# ─────────────────────────────────────────────
# 2-1. 판매 인사이트 분석 (판매 대응 필요 상품 감지)
# ─────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_sales_insight() -> dict:
    """최근 5영업일 출고 패턴 분석 → 이상 징후 감지."""
    from collections import defaultdict
    keys = get_onewms_keys()
    if not keys:
        return {"anomalies": [], "daily_sellers": [], "status": "미연동"}

    today = datetime.now(KST)
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

    # 송장 미출력 판단: 오늘 출고가 0이면 아직 송장을 뽑지 않은 상태
    today_shipped = len(today_products) > 0

    # 일별 판매 데이터 집계 (송장 여부와 무관하게 항상 계산)
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
    daily_sellers.sort(key=lambda x: (-x["active_days"], -x["avg_qty"]))

    # 이상 징후: 송장 출력 후에만 계산
    anomalies = []   # 🔴 긴급 대응: 70%+ 출고 → 오늘 0
    watchlist = []    # 🟡 추가 확인: 40~70% 출고 → 오늘 0
    if today_shipped:
        threshold_urgent = max(len(work_days) * 0.7, 2)    # 70%
        threshold_watch = max(len(work_days) * 0.4, 1)     # 40%
        for pid, days in product_daily.items():
            active_count = sum(1 for d in work_days if days.get(d, 0) > 0)
            total_qty = sum(days.get(d, 0) for d in work_days)
            avg_qty = total_qty / len(work_days) if work_days else 0
            if pid in today_products:
                continue
            item = {
                "product_id": pid,
                "active_days": active_count,
                "total_days": len(work_days),
                "avg_qty": round(avg_qty, 1),
                "total_qty": total_qty,
            }
            if active_count >= threshold_urgent:
                anomalies.append(item)
            elif active_count >= threshold_watch:
                watchlist.append(item)
        anomalies.sort(key=lambda x: -x["avg_qty"])
        watchlist.sort(key=lambda x: -x["avg_qty"])

    return {
        "anomalies": anomalies,
        "watchlist": watchlist,
        "daily_sellers": daily_sellers,
        "work_days": work_days,
        "today_count": len(today_products),
        "total_tracked": len(product_daily),
        "today_shipped": today_shipped,
        "status": "분석 완료" if today_shipped else "송장 미출력",
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
def _detect_product_category(title: str) -> str:
    """상품명에서 카테고리를 추정합니다."""
    t = title.lower()
    if any(k in t for k in ["면도", "쉐이빙", "레이저", "면도기"]):
        return "면도기"
    elif any(k in t for k in ["기저귀", "팬티형", "밴드형", "pull-up"]):
        return "기저귀"
    elif any(k in t for k in ["물티슈", "티슈", "물티슈캡"]):
        return "물티슈"
    elif any(k in t for k in ["칫솔", "치약", "구강"]):
        return "구강용품"
    elif any(k in t for k in ["세제", "세탁", "섬유유연제", "빨래"]):
        return "세탁용품"
    elif any(k in t for k in ["화장", "스킨", "로션", "크림", "세럼", "에센스", "파운데이션", "립", "마스카라"]):
        return "화장품"
    elif any(k in t for k in ["커터", "칼날", "블레이드"]):
        return "커터/문구"
    elif any(k in t for k in ["젖병", "분유", "이유식", "유아", "아기"]):
        return "유아용품"
    return "일반"


# 카테고리별 스펙 키워드 및 차별화 조언
_CATEGORY_SPECS = {
    "면도기": {
        "spec_keywords": ["중날", "3중", "4중", "5중", "6중", "스테인리스", "윤활밴드", "윤활스트립", "피벗헤드", "트리머", "논슬립", "고무그립"],
        "missing_advice": {
            "날수": {"check": ["중날", "3중", "4중", "5중", "6중", "1회용"], "tip": "날 수(3중날, 5중날 등)를 명시하면 품질 인식 향상"},
            "윤활": {"check": ["윤활밴드", "윤활스트립", "알로에", "비타민E"], "tip": "윤활밴드/알로에 스트립 유무를 명시하면 프리미엄 이미지 강화"},
            "헤드": {"check": ["피벗", "회전", "플렉스"], "tip": "피벗헤드(회전 기능) 여부를 강조하면 사용감 어필 가능"},
            "그립": {"check": ["논슬립", "고무그립", "미끄럼방지"], "tip": "논슬립 그립 소재를 언급하면 안전성·편의성 차별화"},
        },
        "diff_tips": ["경쟁사 대비 날 수가 많으면 강조 (예: '5중날 프리미엄')", "대용량 패키지는 '개당 가격' 강조가 효과적", "여행/호텔 용도면 '휴대용 면도기'로 타겟 키워드 추가"],
    },
    "기저귀": {
        "spec_keywords": ["밴드형", "팬티형", "신생아", "소형", "중형", "대형", "특대형", "점보", "순면", "유기농", "통기성"],
        "missing_advice": {
            "타입": {"check": ["밴드형", "팬티형", "pull-up"], "tip": "밴드형/팬티형 구분을 명시하면 정확한 검색 매칭"},
            "사이즈": {"check": ["신생아", "소형", "중형", "대형", "특대형", "S", "M", "L", "XL"], "tip": "사이즈/단계를 명시하면 타겟 고객 클릭률 향상"},
            "소재": {"check": ["순면", "유기농", "오가닉", "천연"], "tip": "순면/유기농 소재 강조는 프리미엄 포지셔닝에 효과적"},
            "흡수력": {"check": ["흡수", "12시간", "밤새", "오버나이트"], "tip": "흡수력(12시간 지속 등)을 수치로 표현하면 신뢰도 상승"},
        },
        "diff_tips": ["수량 대비 가격(개당 단가) 강조가 구매 결정에 핵심", "아기 피부 민감도 관련 인증(피부테스트 완료 등) 강조"],
    },
    "물티슈": {
        "spec_keywords": ["캡형", "리필", "엠보싱", "무향", "무알코올", "무파라벤", "EDI정제수", "두꺼운"],
        "missing_advice": {
            "성분": {"check": ["EDI", "정제수", "무알코올", "무파라벤", "무향"], "tip": "EDI정제수/무알코올/무파라벤 등 안전 성분을 강조하면 엄마 고객 신뢰도 상승"},
            "두께": {"check": ["두꺼운", "엠보싱", "프리미엄"], "tip": "'두꺼운 엠보싱' 등 질감을 강조하면 프리미엄 인식 향상"},
            "형태": {"check": ["캡형", "리필", "휴대용"], "tip": "캡형/리필/휴대용 구분을 명시하면 용도별 검색 노출 증가"},
        },
        "diff_tips": ["매수 대비 가격(장당 단가) 명시가 가성비 어필에 효과적", "생분해/친환경 키워드가 최근 트렌드"],
    },
    "화장품": {
        "spec_keywords": ["용량", "ml", "g", "SPF", "PA", "비건", "더마", "CICA", "히알루론산"],
        "missing_advice": {
            "용량": {"check": ["ml", "g", "oz"], "tip": "정확한 용량(ml/g)을 명시하면 가격 비교 시 유리"},
            "성분": {"check": ["비건", "더마", "CICA", "히알루론산", "나이아신아마이드", "레티놀"], "tip": "주요 성분명을 포함하면 성분 검색 고객 유입 증가"},
        },
        "diff_tips": ["인증/테스트 결과(피부과 테스트 완료 등) 강조", "용량 대비 가격(ml당 단가) 비교 제시"],
    },
    "커터/문구": {
        "spec_keywords": ["스테인리스", "자동잠금", "세라믹", "고탄소강"],
        "missing_advice": {
            "칼날": {"check": ["스테인리스", "세라믹", "고탄소강", "SKS-7"], "tip": "칼날 소재(스테인리스, SKS-7 등)를 명시하면 품질 신뢰도 향상"},
            "안전": {"check": ["자동잠금", "안전", "슬라이드"], "tip": "자동잠금/안전 기능을 강조하면 차별화 가능"},
        },
        "diff_tips": ["칼날 교체 편의성이나 내구성을 강조"],
    },
    "일반": {
        "spec_keywords": [],
        "missing_advice": {},
        "diff_tips": ["수량/용량 정보를 명확히 표기하면 가성비 인식 향상", "용도(가정용, 업소용 등)를 명시하면 타겟 검색 노출 증가"],
    },
}


def analyze_product_title(title: str) -> dict:
    """상품명을 분석하여 카테고리 맞춤 문제점과 개선안을 제시합니다."""
    issues = []
    suggestions = []

    # 카테고리 감지
    category = _detect_product_category(title)

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

    # 수량 정보 포함 여부
    has_count = any(c.isdigit() for c in title) and any(u in title for u in ["개", "입", "P", "EA", "매", "ml", "g"])
    if not has_count:
        suggestions.append("수량/용량 정보(예: 24개입, 200ml)를 명시하면 클릭률 향상")

    # 카테고리 맞춤 스펙 분석
    cat_info = _CATEGORY_SPECS.get(category, _CATEGORY_SPECS["일반"])

    found_specs = []
    for sk in cat_info.get("spec_keywords", []):
        if sk.lower() in title.lower():
            found_specs.append(sk)

    # 누락된 스펙별 맞춤 조언
    for spec_name, spec_info in cat_info.get("missing_advice", {}).items():
        has_it = any(kw.lower() in title.lower() for kw in spec_info["check"])
        if not has_it:
            suggestions.append(spec_info["tip"])

    # 용도 키워드
    usage_keywords = ["휴대용", "여행용", "업소용", "호텔용", "대용량", "가정용"]
    has_usage = any(uk in title for uk in usage_keywords)
    if not has_usage:
        suggestions.append("용도 키워드(휴대용, 여행용, 업소용 등)를 추가하면 타겟 검색 노출 증가")

    # 차별화 팁
    diff_tips = cat_info.get("diff_tips", [])

    return {
        "issues": issues,
        "suggestions": suggestions,
        "category": category,
        "found_specs": found_specs,
        "diff_tips": diff_tips,
    }


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
# 3-3. CTA 관점 상세페이지 분석 (논문 기반)
# ─────────────────────────────────────────────
def analyze_cta_strategy(our_price: int, our_name: str, our_rank: int,
                         price_analysis: dict, title_analysis: dict,
                         detail_extra: dict, all_df) -> dict:
    """논문 기반 CTA(Call-to-Action) 관점 상세페이지 리디자인 분석.

    참고 논문:
    - Kakuko et al. (2024): 상품 페이지 디자인이 구매에 미치는 영향 (r=0.819)
    - Deng (2024): 앵커링 효과와 온라인 가격 전략
    """
    category = title_analysis.get("category", "일반")
    our_qty = price_analysis.get("우리_수량", 0)
    our_unit = price_analysis.get("우리_개당가격", 0)
    comps = price_analysis.get("경쟁사", [])

    # ── 1. 가격 앵커링 전략 ──
    anchoring = {"score": 0, "max": 3, "items": []}

    # 개당 단가 앵커
    if our_qty and our_unit:
        single_price_est = our_unit  # 낱개 가격 추정
        if category == "물티슈":
            unit_label = "장당"
            # 물티슈: 매수 기준 단가
            qty_match = __import__('re').findall(r'(\d+)\s*매', our_name)
            sheets = int(qty_match[0]) if qty_match else 0
            packs_match = __import__('re').findall(r'(\d+)\s*(?:팩|개입|입)', our_name)
            packs = int(packs_match[0]) if packs_match else our_qty
            total_sheets = sheets * packs if sheets else our_qty
            if total_sheets > 0:
                sheet_price = round(our_price / total_sheets, 1)
                anchoring["items"].append({
                    "type": "단가 앵커",
                    "status": "적용 가능",
                    "action": f"상세페이지에 **'{unit_label} {sheet_price}원'** 강조 표시 → 가성비 인식 극대화",
                    "detail": f"총 {total_sheets:,}매 ÷ {our_price:,}원 = {unit_label} {sheet_price}원",
                })
        elif category == "기저귀":
            unit_label = "장당"
            anchoring["items"].append({
                "type": "단가 앵커",
                "status": "적용 가능",
                "action": f"**'{unit_label} {our_unit:,}원'** 표시 → 가성비 핵심 어필 포인트",
                "detail": f"{our_qty}개 ÷ {our_price:,}원",
            })
        else:
            unit_label = "개당"
            anchoring["items"].append({
                "type": "단가 앵커",
                "status": "적용 가능",
                "action": f"**'{unit_label} {our_unit:,}원'** 표시 → 가성비 핵심 어필 포인트",
                "detail": f"{our_qty}개 ÷ {our_price:,}원",
            })
        anchoring["score"] += 1

    # 할인/원가 앵커
    anchoring["items"].append({
        "type": "원가 대비 앵커",
        "status": "확인 필요",
        "action": "원래 가격(정가)을 취소선으로 표시하고, 현재가를 크게 표시 → **할인 프레이밍**",
        "detail": "예: ~~42,000원~~ → **32,000원** (24% 할인)",
    })

    # 경쟁사 대비 앵커
    if comps:
        most_expensive = max(comps, key=lambda x: x["개당가격"])
        if our_unit and our_unit < most_expensive["개당가격"]:
            save_pct = round((1 - our_unit / most_expensive["개당가격"]) * 100)
            anchoring["items"].append({
                "type": "경쟁 비교 앵커",
                "status": "우위",
                "action": f"경쟁사 대비 **{save_pct}% 저렴** — 비교표를 상세페이지에 삽입",
                "detail": f"우리 {our_unit:,}원 vs 최고가 {most_expensive['개당가격']:,}원({most_expensive['판매처']})",
            })
            anchoring["score"] += 1

    # ── 상품명에서 실제 문구 재료 추출 ──
    import re as _re
    # 브랜드명 추출 (첫 단어 또는 한글 2~4자)
    brand_match = _re.match(r'^([가-힣A-Za-z]+)', our_name)
    brand_name = brand_match.group(1) if brand_match else "우리 제품"
    # 짧은 상품 요약 (앞 15자)
    short_name = our_name[:15].strip()
    # 수량 텍스트
    qty_text = f"{our_qty}개" if our_qty else ""
    price_text = f"{our_price:,}원" if our_price else ""

    # 카테고리별 리뷰 키워드 예시
    _review_keywords = {
        "물티슈": ["두꺼워요 💪", "향이 좋아요 🌿", "아기 피부에 순해요 👶", "가성비 최고 💰"],
        "면도기": ["면도 잘 돼요 ✨", "피부 자극 없어요 🛡️", "그립감 좋아요 👍", "날이 오래가요 💎"],
        "기저귀": ["안 새요 🛡️", "부드러워요 🧸", "통기성 좋아요 🌬️", "가성비 최고 💰"],
        "화장품": ["촉촉해요 💧", "흡수 빨라요 ⚡", "향이 좋아요 🌸", "순한 성분 🌿"],
    }
    review_kw = _review_keywords.get(category, ["품질 좋아요 ⭐", "가성비 최고 💰", "빠른배송 🚀"])

    # ── 2. 사회적 증거 (Social Proof) ──
    social_proof = {"score": 0, "max": 3, "items": []}

    social_proof["items"].append({
        "type": "판매량 표시",
        "action": "상세페이지 최상단에 누적 판매 배지 삽입",
        "detail": "논문: 60.8%가 리뷰/사회적 증거를 구매 결정에 중요하게 평가 (Kakuko et al.)",
        "example": f'🏆 "{brand_name} 시리즈 누적 판매 10만개 돌파!" · "네이버쇼핑 {category} 부문 BEST"',
    })
    social_proof["items"].append({
        "type": "리뷰 하이라이트",
        "action": "상세페이지 중간에 베스트 리뷰 키워드 배지 삽입 → 스크롤 중 이탈 방지",
        "detail": "리뷰에서 자주 등장하는 키워드를 배지화하여 시각적 신뢰 구축",
        "example": f"💬 실구매자 키워드: {' · '.join([f'「{kw}」' for kw in review_kw])}",
    })
    social_proof["items"].append({
        "type": "사회적 동조 앵커",
        "action": "이번 달 구매자 수 또는 재구매율 문구 추가",
        "detail": "논문: 다수의 선택이 앵커로 작용, 소비자가 검토 없이 같은 행동을 취함 (Deng, 2024)",
        "example": f'📊 "이번 달 {brand_name} 구매자 1,200명+" · "재구매율 94% — 한번 쓰면 바꿀 수 없는 {category}"',
    })

    # ── 3. FOMO(희소성·긴급성) 전략 ──
    fomo = {"score": 0, "max": 3, "items": []}

    fomo["items"].append({
        "type": "시간 앵커",
        "action": "당일 출고 마감 시간을 명시하여 즉각 행동 유도",
        "detail": "논문: 시간 앵커가 소비자의 의사결정 과정을 단축시킴 (Deng, 2024)",
        "example": f'⏰ "오늘 17시 이전 주문 → 당일 출고!" · "지금 주문하면 내일 {short_name} 받아보세요"',
    })
    fomo["items"].append({
        "type": "재고 앵커",
        "action": "실제 재고 데이터 기반 소진 임박 표시 (OneWMS 연동)",
        "detail": "실제 재고가 적을 때만 노출하면 신뢰도 유지 — 허위 희소성은 역효과",
        "example": f'🔥 "현재 재고 23개 — 이번 주 소진 예상" · "{brand_name} {category} 입고 대기 중, 지금이 마지막!"',
    })
    fomo["items"].append({
        "type": "프로모션 앵커",
        "action": "한정 혜택(무료배송/추가증정)으로 구매 전환율 상승",
        "detail": "논문: 52.1%가 인센티브/프로모션이 구매 유도에 효과적이라고 응답 (Kakuko et al.)",
        "example": f'🎁 "이번 주만! {short_name} 무료배송" · "{qty_text} 구매 시 +1개 추가 증정"' if qty_text else f'🎁 "이번 주만! {short_name} 무료배송 + 사은품 증정"',
    })

    # ── 4. 장바구니 이탈 방지 ──
    cart_abandon = {"score": 0, "max": 4, "items": []}

    cart_abandon["items"].append({
        "type": "정보 불안 해소",
        "action": "상세페이지 상단에 핵심 정보 집중 배치 → 스크롤 전에 확신 제공",
        "detail": "배송정보 · 교환/반품 · 성분안전성을 한눈에 → 논문: 35%만 정보 충분하다고 응답 (개선 여지 큼)",
        "example": f'📋 상단 배치 예: "✅ 무료배송 · ✅ 당일출고 · ✅ 100% 환불보장 · ✅ 정품인증"',
    })

    # 카테고리별 불안 해소 포인트
    if category == "물티슈":
        cart_abandon["items"].append({
            "type": "안전성 인증",
            "action": "피부테스트·성분안전 인증 배지를 상단에 배치",
            "detail": "엄마 고객의 최대 관심사 = 아기 피부 안전성. 스크롤 전에 해결해야 이탈 방지",
            "example": f'🛡️ "EDI정제수 99.9% · 무알코올 · 무파라벤 · 피부자극 테스트 완료" 인증마크',
        })
    elif category == "면도기":
        cart_abandon["items"].append({
            "type": "품질 인증",
            "action": "칼날 품질·피부 안전 인증 배지 상단 배치",
            "detail": "면도기 구매 시 핵심 불안요소 = 칼날 품질 + 피부 자극",
            "example": f'🛡️ "스테인리스 정밀 칼날 · 인체공학 논슬립 그립 · 민감성 피부 테스트 완료"',
        })
    elif category == "기저귀":
        cart_abandon["items"].append({
            "type": "안전성 인증",
            "action": "피부과 테스트·소재 안전 인증 배지 상단 배치",
            "detail": "기저귀의 핵심 구매 불안 = 아기 피부 트러블",
            "example": f'🛡️ "피부과 테스트 완료 · 순면 탑시트 · 무형광증백제 · 3중 누수방지"',
        })

    cart_abandon["items"].append({
        "type": "경쟁사 비교표",
        "action": "우리 vs 경쟁사 비교표를 상세페이지에 삽입 → 이탈 전 확신 제공",
        "detail": "가격, 수량, 핵심 스펙을 한눈에 비교 → 다른 페이지로 이탈할 필요 제거",
        "example": f'📊 비교표: "{brand_name} {price_text}/{qty_text}" vs 경쟁사 A/B → 개당 단가 강조' if qty_text else f'📊 "{brand_name}" vs 경쟁사 비교표 — 가격·품질·배송 한눈에',
    })
    cart_abandon["items"].append({
        "type": "배송·교환 안심",
        "action": "무료배송·무료교환·환불보장 배지를 CTA 버튼 바로 위에 배치",
        "detail": "구매 직전 마지막 불안을 해소하는 위치가 중요 (CTA 버튼 근처)",
        "example": '🚚 CTA 버튼 바로 위: "무료배송 · 무료교환 · 100% 환불보장 — 걱정 없이 주문하세요"',
    })

    # ── 5. CTA 버튼 최적화 ──
    cta_button = {"items": []}
    cta_button["items"].append({
        "type": "행동 유도 문구",
        "action": "'구매하기' 대신 혜택을 포함한 구체적 문구 사용",
        "detail": "논문: CTA 버튼 가시성과 문구가 전환율에 직접적 영향 — 68.2% 동의 (Kakuko et al.)",
        "example": f'🔘 "{price_text} 무료배송으로 받기" · "할인가 {price_text}에 지금 구매" · "오늘만 이 가격! 바로 주문"' if price_text else '🔘 "오늘 무료배송으로 받기" · "할인가로 지금 구매"',
    })
    cta_button["items"].append({
        "type": "시각적 계층",
        "action": "상세페이지 내 중간·하단에 CTA 유도 섹션 반복 배치",
        "detail": "긴 상세페이지에서 스크롤 중간에 구매 동기를 재점화하는 구간 필요",
        "example": f'📍 스크롤 중간 삽입: "여기까지 읽으셨다면, {brand_name} {category}의 차이를 느끼셨을 거예요 → 지금 주문하기"',
    })

    return {
        "anchoring": anchoring,
        "social_proof": social_proof,
        "fomo": fomo,
        "cart_abandon": cart_abandon,
        "cta_button": cta_button,
        "category": category,
    }


# ─────────────────────────────────────────────
# 3-4. ScraperAPI 기반 상세페이지 분석
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
# 공통: 판매처 URL 생성 & 판매처 상세 팝업
# ─────────────────────────────────────────────
def build_shop_url(shop_name: str, shop_product_id: str) -> str:
    """판매처명 + shop_product_id로 상품 페이지 URL을 생성합니다."""
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


@st.dialog("🛒 판매처별 판매 현황", width="large")
def show_shop_detail_dialog():
    """공통 판매처 상세 팝업 — session_state['_shop_detail_data'] 사용"""
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
    summary_line = f"**{brand}** | {p_name}"
    if avg_qty:
        summary_line += f" — 일평균 **{avg_qty}개**"
    summary_line += today_badge
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


@st.dialog("📝 판매처별 상품페이지", width="small")
def show_product_pages_dialog():
    """판매처별 상품페이지 URL 목록 팝업"""
    import re as _re
    data = st.session_state.get("_product_pages_data", {})
    if not data:
        st.warning("데이터를 불러올 수 없습니다.")
        return
    p_name = data.get("product_name", "")
    p_id = data.get("product_id", "")
    shops = data.get("shops", [])
    brand = data.get("brand", "")

    st.markdown(f'<div style="font-size:0.9rem;"><b>{brand}</b> | {p_name} <code>[{p_id}]</code></div>', unsafe_allow_html=True)
    st.caption("각 판매처 상품페이지를 열어 썸네일·제목·상세이미지·가격을 확인하세요.")

    has_urls = False
    for shop in shops:
        urls = shop.get("urls", [])
        if urls:
            has_urls = True
            for url in urls:
                # URL 끝의 숫자를 상품코드로 추출
                code_match = _re.search(r'(\d{5,})(?:\?|$|/\s*$)', url)
                shop_code = code_match.group(1) if code_match else ""
                code_html = f' <span style="font-size:0.75rem; color:#888; background:#f0f0f0; padding:0 3px; border-radius:3px;">{shop_code}</span>' if shop_code else ""
                st.markdown(
                    f'<div style="display:flex; align-items:center; gap:6px; padding:3px 8px; border-bottom:1px solid #eee; font-size:0.86rem;">'
                    f'<span style="flex:1; white-space:nowrap; overflow:hidden;">🛒 <b>{shop["name"]}</b>{code_html}</span>'
                    f'<span style="font-size:0.78rem; color:#999; white-space:nowrap;">{shop["qty"]}개</span>'
                    f'<a href="{url}" target="_blank" style="background:#1e88e5; color:#fff; padding:1px 6px; border-radius:3px; font-size:0.75rem; text-decoration:none; white-space:nowrap;">열기↗</a>'
                    f'</div>', unsafe_allow_html=True)
    if not has_urls:
        st.info("등록된 상품페이지 URL이 없습니다.")


ACTION_TYPES = {
    "price_change": "💰 가격 수정",
    "page_edit": "📝 상세페이지 수정",
    "stock_check": "📦 재고 확인/발주",
    "no_issue": "🔍 확인만 (이상없음)",
    "defer": "⏳ 내일 대응 예정",
}


@st.dialog("✅ 대응 완료 기록", width="small")
def show_action_dialog():
    """태스크 완료 시 대응 내용을 기록하는 팝업."""
    data = st.session_state.get("_action_dialog_data", {})
    if not data:
        st.warning("데이터 없음")
        return
    tid = data.get("task_id", "")
    pname = data.get("product_name", "")
    st.markdown(f"**{pname}**")
    st.caption("어떤 대응을 했나요?")
    action_type = st.radio(
        "대응 유형", options=list(ACTION_TYPES.keys()),
        format_func=lambda x: ACTION_TYPES[x],
        key="_action_type_radio", label_visibility="collapsed",
    )

    # 대응 유형에 따른 개선 내용 입력 (구체적 기록)
    _detail_placeholders = {
        "price_change": "예: 12,900원 → 10,900원으로 변경 (쿠팡)",
        "page_edit": "예: 썸네일에 개당 단가 텍스트 추가",
        "stock_check": "예: 발주 50개 요청 완료",
        "no_issue": "예: 경쟁사 대비 가격 정상 확인",
        "defer": "예: 내일 오전 마케팅팀과 협의 예정",
    }
    detail = st.text_input(
        "개선 내용 (구체적으로)",
        placeholder=_detail_placeholders.get(action_type, "어떻게 개선했는지 기록"),
        key="_action_detail",
    )
    memo = st.text_input("추가 메모 (선택)", placeholder="기타 참고 사항", key="_action_memo")
    if st.button("완료 저장", use_container_width=True, type="primary"):
        st.session_state["_action_result"] = {
            "task_id": tid,
            "action_type": action_type,
            "detail": detail,
            "memo": memo,
        }
        st.rerun()


def quick_shop_detail(pid: str, pname: str, avg_qty=0, today_shipped=None):
    """업무 일지 등에서 바로 판매처 상세 팝업을 띄우는 헬퍼."""
    from datetime import timedelta as _td
    _today = datetime.now(KST)
    dates = tuple((_today - _td(days=i)).strftime("%Y-%m-%d") for i in range(1, 8))
    orders_map = fetch_orders_parallel(dates)
    shop_list = fetch_shop_list()
    pid_shops: dict = {}
    for d_str, orders in orders_map.items():
        for o in orders:
            shop_code = o.get("shop_id", "")
            if not shop_code:
                continue
            shop_name = shop_list.get(shop_code, shop_code)
            shop_pid = o.get("shop_product_id", "")
            order_products = o.get("order_products", [])
            if isinstance(order_products, list):
                for op in order_products:
                    if str(op.get("product_id", "")) != str(pid):
                        continue
                    qty = 1
                    try:
                        qty = int(float(str(op.get("qty", 1))))
                    except (ValueError, TypeError):
                        pass
                    amount = 0
                    try:
                        amount = int(float(str(op.get("prd_amount", 0))))
                    except (ValueError, TypeError):
                        pass
                    if shop_name not in pid_shops:
                        pid_shops[shop_name] = {"qty": 0, "amount": 0, "order_count": 0, "shop_product_ids": set()}
                    pid_shops[shop_name]["qty"] += qty
                    pid_shops[shop_name]["amount"] += amount
                    pid_shops[shop_name]["order_count"] += 1
                    if shop_pid:
                        pid_shops[shop_name]["shop_product_ids"].add(shop_pid)
    if not pid_shops:
        return None
    sorted_shops = sorted(pid_shops.items(), key=lambda x: -x[1]["qty"])
    shops_data = []
    for s_name, s_info in sorted_shops:
        urls = [build_shop_url(s_name, spid) for spid in s_info["shop_product_ids"] if build_shop_url(s_name, spid)]
        shops_data.append({"name": s_name, "qty": s_info["qty"], "amount": s_info["amount"], "order_count": s_info["order_count"], "urls": urls})
    brand = extract_brand(pname)
    shop_summary = " · ".join([f"{sn} {si['qty']}개" for sn, si in sorted_shops[:3]])
    return {
        "product_name": pname, "product_id": pid, "shops": shops_data,
        "brand": brand, "avg_qty": avg_qty, "today_shipped": today_shipped,
        "shop_summary": shop_summary,
    }


# ─────────────────────────────────────────────
# 판매처별 매출 조회
# ─────────────────────────────────────────────
@st.cache_data(ttl=21600, show_spinner=False)
def fetch_shop_list() -> dict:
    """판매처 목록을 가져옵니다. (거의 변하지 않으므로 6시간 캐시)"""
    data = call_onewms_api("get_etc_info", {"type": "product", "search_type": "shop"})
    if isinstance(data, dict) and data.get("error") == 0:
        return {item["code"]: item["name"] for item in data.get("data", [])}
    return {}


def _fetch_orders_by_date_raw(date_str: str) -> list:
    """특정 날짜의 주문 데이터를 가져옵니다 (캐시 없음, 병렬 호출용)."""
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


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_orders_by_date(date_str: str) -> list:
    """특정 날짜의 주문 데이터 (단일 호출, 30분 캐시)."""
    return _fetch_orders_by_date_raw(date_str)


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_orders_parallel(date_strings: tuple) -> dict:
    """여러 날짜의 주문 데이터를 병렬로 가져옵니다. {date_str: [orders]}"""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    results = {}
    with ThreadPoolExecutor(max_workers=7) as executor:
        future_to_date = {executor.submit(_fetch_orders_by_date_raw, d): d for d in date_strings}
        for future in as_completed(future_to_date):
            date_str = future_to_date[future]
            try:
                results[date_str] = future.result()
            except Exception:
                results[date_str] = []
    return results


with st.sidebar:
    st.markdown('<div style="display:flex;align-items:center;margin-bottom:0.3rem;"><div class="sidebar-logo"><div class="kb-text">KINI<br>BINI</div><div class="kb-sub">Premium</div></div><span style="font-size:1.3rem;font-weight:800;">신아인터네셔날</span></div>', unsafe_allow_html=True)
    st.caption("ShinA International 업무 대시보드")
    st.markdown("---")

    # ── 메뉴 네비게이션 ──
    menu_items = {
        "📊 대시보드": "dashboard",
        "📦 판매대응 및 재고": "sales_inventory",
        "🛒 가격 모니터링": "price_monitor",
        "📝 업무 일지": "daily_log",
        "🔍 상품 재발굴": "slow_moving",
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
    now = datetime.now(KST)
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

    # ── 분석 실행 ──
    title_analysis = analyze_product_title(our_name)
    price_analysis = analyze_price_competitiveness(our_price, our_name, all_df)
    thumb_analysis = generate_thumbnail_analysis(our_image, our_name, our_rank)

    detail_data_extra = {}
    if our_link and our_link != "#":
        with st.spinner("상세페이지 분석 중..."):
            detail_data_extra = fetch_smartstore_detail(our_link)

    blog_reviews = fetch_blog_reviews(our_name[:25], top_n=3)
    review_summary = analyze_blog_reviews(blog_reviews) if blog_reviews else {"pros": [], "cons": [], "count": 0}
    cta = analyze_cta_strategy(our_price, our_name, our_rank, price_analysis, title_analysis, detail_data_extra, all_df)

    # ── 공통 변수 ──
    category = title_analysis.get("category", "일반")
    our_unit = price_analysis.get("우리_개당가격", 0)
    our_qty = price_analysis.get("우리_수량", 0)
    comps = price_analysis.get("경쟁사", [])
    issues = title_analysis.get("issues", [])
    suggestions = title_analysis.get("suggestions", [])
    found_specs = title_analysis.get("found_specs", [])
    diff_tips = title_analysis.get("diff_tips", [])

    # ════════════════════════════════════════
    # SECTION 1: 상품 헤더 + 점수 배지
    # ════════════════════════════════════════
    scores = {}
    if our_unit and comps:
        cheapest = comps[0]
        if our_unit <= cheapest["개당가격"]:
            scores["가격"] = {"s": "우위", "c": "#22c55e", "d": f"{our_unit:,}원"}
        elif our_unit <= cheapest["개당가격"] * 1.1:
            scores["가격"] = {"s": "보통", "c": "#f59e0b", "d": f"{our_unit:,}원"}
        else:
            diff_pct = round((our_unit / cheapest["개당가격"] - 1) * 100)
            scores["가격"] = {"s": "주의", "c": "#ef4444", "d": f"+{diff_pct}%"}
    else:
        scores["가격"] = {"s": "-", "c": "#94a3b8", "d": "분석불가"}

    if len(issues) > 0:
        scores["상품명"] = {"s": "수정", "c": "#ef4444", "d": f"{len(issues)}건"}
    elif len(suggestions) > 2:
        scores["상품명"] = {"s": "개선", "c": "#f59e0b", "d": f"{len(suggestions)}건"}
    else:
        scores["상품명"] = {"s": "양호", "c": "#22c55e", "d": "OK"}

    if thumb_analysis.get("issues"):
        scores["썸네일"] = {"s": "개선", "c": "#f59e0b", "d": f"{len(thumb_analysis['issues'])}건"}
    else:
        scores["썸네일"] = {"s": "양호", "c": "#22c55e", "d": "OK"}

    if our_rank <= 5:
        scores["순위"] = {"s": "상위", "c": "#22c55e", "d": f"{our_rank}위"}
    elif our_rank <= 15:
        scores["순위"] = {"s": "보통", "c": "#f59e0b", "d": f"{our_rank}위"}
    else:
        scores["순위"] = {"s": "하위", "c": "#ef4444", "d": f"{our_rank}위"}

    score_badges = ""
    for label, info in scores.items():
        score_badges += f'<div style="text-align:center; min-width:52px;"><div style="width:10px; height:10px; border-radius:50%; background:{info["c"]}; margin:0 auto 2px;"></div><div style="font-size:0.58rem; color:#94a3b8;">{label}</div><div style="font-size:0.68rem; font-weight:700;">{info["s"]}</div><div style="font-size:0.55rem; color:#94a3b8;">{info["d"]}</div></div>'

    img_html = f'<img src="{our_image}" style="width:50px; height:50px; border-radius:6px; object-fit:cover;">' if our_image else ''
    link_html = f' · <a href="{our_link}" target="_blank" style="font-size:0.7rem; color:#3b82f6;">상품페이지↗</a>' if our_link and our_link != "#" else ''

    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:0.8rem; padding:0.5rem 0;">
        {img_html}
        <div style="flex:1; min-width:0;">
            <div style="font-size:0.8rem; font-weight:700;">🏪 {our_mall} · {our_rank}위 · {our_price:,}원{link_html}</div>
            <div style="font-size:0.68rem; color:#64748b; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{our_name}</div>
        </div>
        <div style="display:flex; gap:0.4rem; flex-shrink:0;">
            {score_badges}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ════════════════════════════════════════
    # SECTION 2: 💸 매출 손실 추정 카드
    # ════════════════════════════════════════
    if our_unit and comps:
        cheapest = comps[0]
        unit_diff = our_unit - cheapest["개당가격"]
        if unit_diff > 0:
            # 업무일지에서 일평균 출고량 가져오기 시도
            _avg_qty_est = 0
            try:
                _insight = fetch_sales_insight()
                for _anom in _insight.get("anomalies", []) + _insight.get("watchlist", []):
                    if our_name and _anom.get("product_id", "") in our_name:
                        _avg_qty_est = _anom.get("avg_qty", 0)
                        break
            except Exception:
                pass
            _daily_qty = _avg_qty_est if _avg_qty_est > 0 else 10  # 기본 추정 10개/일
            _daily_loss = unit_diff * _daily_qty
            _monthly_loss = _daily_loss * 30
            _recommend_price = cheapest["개당가격"] * 1.1  # 최저가 대비 +10%
            _recommend_total = round(_recommend_price * our_qty) if our_qty else our_price
            _diff_pct = round((our_unit / cheapest["개당가격"] - 1) * 100)

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fef2f2, #fff5f5); border: 1px solid #fecaca; border-radius: 12px; padding: 0.8rem 1rem; margin: 0.5rem 0;">
                <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
                    <span style="font-size:1.1rem;">💸</span>
                    <span style="font-size:0.9rem; font-weight:800; color:#dc2626;">예상 매출 손실</span>
                    <span style="font-size:0.68rem; color:#999; margin-left:auto;">일평균 {_daily_qty}개 기준</span>
                </div>
                <div style="display:flex; gap:1rem; flex-wrap:wrap;">
                    <div style="flex:1; min-width:120px;">
                        <div style="font-size:0.68rem; color:#888;">우리 개당가격</div>
                        <div style="font-size:1rem; font-weight:700; color:#dc2626;">{our_unit:,}원</div>
                    </div>
                    <div style="flex:1; min-width:120px;">
                        <div style="font-size:0.68rem; color:#888;">최저가 (개당)</div>
                        <div style="font-size:1rem; font-weight:700; color:#16a34a;">{cheapest['개당가격']:,}원</div>
                    </div>
                    <div style="flex:1; min-width:120px;">
                        <div style="font-size:0.68rem; color:#888;">차이</div>
                        <div style="font-size:1rem; font-weight:700; color:#dc2626;">+{unit_diff:,}원 (+{_diff_pct}%)</div>
                    </div>
                </div>
                <div style="margin-top:0.6rem; padding-top:0.5rem; border-top:1px solid #fecaca; display:flex; gap:1rem; flex-wrap:wrap;">
                    <div style="flex:1; text-align:center; padding:0.4rem; background:#fff; border-radius:8px;">
                        <div style="font-size:0.68rem; color:#888;">일 손실</div>
                        <div style="font-size:1.1rem; font-weight:800; color:#dc2626;">-{_daily_loss:,}원</div>
                    </div>
                    <div style="flex:1; text-align:center; padding:0.4rem; background:#fff; border-radius:8px;">
                        <div style="font-size:0.68rem; color:#888;">월 손실 추정</div>
                        <div style="font-size:1.1rem; font-weight:800; color:#dc2626;">-{_monthly_loss:,}원</div>
                    </div>
                    <div style="flex:1; text-align:center; padding:0.4rem; background:#f0fdf4; border-radius:8px; border:1px solid #bbf7d0;">
                        <div style="font-size:0.68rem; color:#888;">🎯 권장 가격</div>
                        <div style="font-size:1.1rem; font-weight:800; color:#16a34a;">{_recommend_total:,}원</div>
                        <div style="font-size:0.6rem; color:#888;">최저가+10%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif unit_diff <= 0:
            _save_pct = round((1 - our_unit / cheapest["개당가격"]) * 100) if cheapest["개당가격"] > 0 else 0
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f0fdf4, #ecfdf5); border: 1px solid #bbf7d0; border-radius: 12px; padding: 0.7rem 1rem; margin: 0.5rem 0;">
                <span style="font-size:1rem;">✅</span>
                <span style="font-size:0.88rem; font-weight:700; color:#16a34a;"> 가격 경쟁력 확보됨</span>
                <span style="font-size:0.78rem; color:#555;"> — 최저가 대비 {_save_pct}% 저렴 (개당 {our_unit:,}원 vs {cheapest['개당가격']:,}원)</span>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ════════════════════════════════════════
    # SECTION 3: 동적 TOP 액션 (상품별 맞춤)
    # ════════════════════════════════════════
    st.markdown("##### 🚀 지금 바로 해야 할 일")
    top_actions = []

    # 긴급 — 가격이 비쌀 때만
    if scores.get("가격", {}).get("c") == "#ef4444" and comps:
        cheapest = comps[0]
        _rec_unit = round(cheapest["개당가격"] * 1.1)
        _rec_total = round(_rec_unit * our_qty) if our_qty else our_price
        top_actions.append({
            "priority": "긴급", "bg": "#fff5f5", "border": "#f5576c",
            "title": "💰 가격 인하",
            "action": f"{our_price:,}원 → {_rec_total:,}원 (개당 {our_unit:,}→{_rec_unit:,}원)",
        })

    # 긴급 — 상품명 이슈
    if issues:
        top_actions.append({
            "priority": "긴급", "bg": "#fff5f5", "border": "#f5576c",
            "title": "📝 상품명 수정",
            "action": " / ".join(issues[:2])[:60],
        })

    # 긴급 — 순위 하위
    if our_rank > 30:
        top_actions.append({
            "priority": "긴급", "bg": "#fff5f5", "border": "#f5576c",
            "title": "📉 순위 개선 필요",
            "action": f"현재 {our_rank}위 — 광고 집행 또는 가격/상품명 개선 시급",
        })

    # 중요 — 개당단가 앵커링 (항상 유용하지만 가격 데이터 있을 때만)
    if our_unit and our_qty:
        top_actions.append({
            "priority": "중요", "bg": "#fffbeb", "border": "#f59e0b",
            "title": "🏷️ 개당 단가 강조",
            "action": f"썸네일·상세페이지에 '개당 {our_unit:,}원' 텍스트 삽입",
        })

    # 중요 — 썸네일 이슈
    if thumb_analysis.get("issues"):
        top_actions.append({
            "priority": "중요", "bg": "#fffbeb", "border": "#f59e0b",
            "title": "📸 썸네일 개선",
            "action": thumb_analysis["issues"][0][:50],
        })

    # 권장 — 상품명 개선안이 많을 때
    if len(suggestions) > 2:
        top_actions.append({
            "priority": "권장", "bg": "#f0fdf4", "border": "#22c55e",
            "title": "📝 상품명 키워드 보강",
            "action": f"{len(suggestions)}개 개선 항목 — 상품명·페이지 탭에서 확인",
        })

    if not top_actions:
        st.success("✅ 현재 긴급하게 수정할 사항이 없습니다. 아래 탭에서 세부 분석을 확인하세요.")
    else:
        # 2열 그리드
        _act_cols = st.columns(2)
        for i, act in enumerate(top_actions[:6]):
            with _act_cols[i % 2]:
                st.markdown(f"""
                <div style="padding:0.45rem 0.7rem; margin-bottom:0.35rem; border-radius:6px; background:{act['bg']}; border-left:3px solid {act['border']};">
                    <div style="display:flex; align-items:center; gap:0.3rem;">
                        <span style="font-size:0.55rem; font-weight:700; color:#fff; background:{act['border']}; padding:0.08rem 0.3rem; border-radius:3px;">{act['priority']}</span>
                        <span style="font-weight:700; font-size:0.78rem;">{act['title']}</span>
                    </div>
                    <div style="margin-top:0.15rem; font-size:0.72rem; color:#475569;">{act['action']}</div>
                </div>
                """, unsafe_allow_html=True)

    # ════════════════════════════════════════
    # SECTION 4: 상세 분석 3탭
    # ════════════════════════════════════════
    st.markdown("")
    st.markdown("#### 📋 상세 분석")

    tab_price, tab_product, tab_action = st.tabs([
        "💰 가격·경쟁력", "📝 상품명·페이지", "📊 종합 액션플랜"
    ])

    # ── 탭 1: 가격·경쟁력 ──
    with tab_price:
        if our_unit:
            # ── 가격 바 차트 (비주얼 비교) ──
            st.markdown("##### 📊 경쟁사 개당가격 비교")
            _bar_items = [{"판매처": f"🏪 우리 ({our_mall})", "개당가격": our_unit, "is_ours": True}]
            for comp in comps[:5]:
                _bar_items.append({"판매처": f"{comp['순위']}위 {comp['판매처']}", "개당가격": comp["개당가격"], "is_ours": False})

            if _bar_items:
                _sorted_bars = sorted(_bar_items, key=lambda x: x["개당가격"])
                _max_price = max(b["개당가격"] for b in _sorted_bars) if _sorted_bars else 1
                _bar_html = ""
                for b in _sorted_bars:
                    _pct = round(b["개당가격"] / _max_price * 100)
                    if b["is_ours"]:
                        _bar_color = "#dc2626" if our_unit > (comps[0]["개당가격"] if comps else our_unit) else "#16a34a"
                        _bar_bg = "#fef2f2" if _bar_color == "#dc2626" else "#f0fdf4"
                        _name_style = "font-weight:800; color:#111;"
                        _bar_border = f"border:2px solid {_bar_color};"
                    else:
                        _bar_color = "#94a3b8"
                        _bar_bg = "#f8fafc"
                        _name_style = "color:#555;"
                        _bar_border = ""
                    _bar_html += f"""
                    <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.3rem; padding:0.3rem 0.5rem; border-radius:6px; background:{_bar_bg}; {_bar_border}">
                        <div style="width:120px; font-size:0.72rem; {_name_style} flex-shrink:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{b['판매처']}</div>
                        <div style="flex:1; background:#e5e7eb; border-radius:4px; height:18px; overflow:hidden;">
                            <div style="width:{_pct}%; height:100%; background:{_bar_color}; border-radius:4px; transition:width 0.5s;"></div>
                        </div>
                        <div style="width:65px; text-align:right; font-size:0.78rem; font-weight:700; color:{_bar_color}; flex-shrink:0;">{b['개당가격']:,}원</div>
                    </div>"""
                st.markdown(_bar_html, unsafe_allow_html=True)

            st.markdown("")
            # 상세 테이블 (접힘)
            with st.expander("📋 상세 가격 테이블", expanded=False):
                table_rows = [{"구분": "🏪 우리", "판매처": our_mall, "가격": f"{our_price:,}원", "수량": f"{our_qty}개", "개당가격": f"{our_unit:,}원"}]
                for comp in comps[:4]:
                    table_rows.append({
                        "구분": f"{comp['순위']}위",
                        "판매처": comp["판매처"],
                        "가격": f"{comp['가격']:,}원",
                        "수량": f"{comp['수량']}개",
                        "개당가격": f"{comp['개당가격']:,}원",
                    })
                st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)
        else:
            st.info("상품명에서 수량 정보를 추출할 수 없어 개당 가격 비교가 어렵습니다.")

        # 앵커링 전략 (간결화)
        st.markdown("---")
        st.markdown("**💡 가격 앵커링 적용**")
        for item in cta["anchoring"]["items"]:
            st.markdown(f"""
            <div style="padding:0.5rem 0.7rem; margin-bottom:0.3rem; border-radius:8px; background:#fffbeb; border-left:4px solid #f59e0b;">
                <span style="font-weight:700; font-size:0.9rem;">{item['type']}</span>
                <span style="font-size:0.85rem; color:#475569;"> — {item['action']}</span>
            </div>
            """, unsafe_allow_html=True)

    # ── 탭 2: 상품명·페이지 ──
    with tab_product:
        # ── 상품명 Before → After 제안 ──
        st.markdown("##### ✏️ 상품명 수정 제안")

        # After 상품명 생성
        import re as _re2
        _brand = extract_brand(our_name)
        _base_name = our_name.replace(f"{_brand}-", "").replace(f"{_brand} ", "").strip()
        # 카테고리 키워드 추가
        _cat_keywords = {
            "면도기": "면도기", "기저귀": "기저귀", "물티슈": "물티슈",
            "구강용품": "칫솔", "화장품": "화장품", "커터/문구": "커터칼",
        }
        _cat_kw = _cat_keywords.get(category, "")
        _has_cat_kw = _cat_kw.lower() in our_name.lower() if _cat_kw else True
        # 빠진 스펙 키워드 제안
        _missing_specs = []
        for spec_name, spec_info in _CATEGORY_SPECS.get(category, {}).get("missing_advice", {}).items():
            has_it = any(kw.lower() in our_name.lower() for kw in spec_info["check"])
            if not has_it and spec_info["check"]:
                _missing_specs.append(spec_info["check"][0])
        # After 생성
        _after_parts = [_brand]
        _after_parts.append(_base_name)
        if not _has_cat_kw and _cat_kw:
            _after_parts.append(_cat_kw)
        if _missing_specs:
            _after_parts.extend(_missing_specs[:2])
        _qty_text = f"{our_qty}개입" if our_qty else ""
        if _qty_text and _qty_text not in our_name:
            _after_parts.append(f"({_qty_text})")
        _after_name = " ".join(_after_parts)

        _changes_html = ""
        if not _has_cat_kw and _cat_kw:
            _changes_html += f'<span style="display:inline-block; margin:2px; padding:1px 6px; border-radius:4px; background:#e8f5e9; color:#2e7d32; font-size:0.7rem;">+{_cat_kw}</span>'
        for _ms in _missing_specs[:2]:
            _changes_html += f'<span style="display:inline-block; margin:2px; padding:1px 6px; border-radius:4px; background:#e3f2fd; color:#1565c0; font-size:0.7rem;">+{_ms}</span>'
        if _qty_text and _qty_text not in our_name:
            _changes_html += f'<span style="display:inline-block; margin:2px; padding:1px 6px; border-radius:4px; background:#fff3e0; color:#e65100; font-size:0.7rem;">+{_qty_text}</span>'

        st.markdown(f"""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:0.8rem 1rem; margin-bottom:0.8rem;">
            <div style="margin-bottom:0.5rem;">
                <span style="font-size:0.65rem; font-weight:700; color:#fff; background:#94a3b8; padding:2px 6px; border-radius:3px;">BEFORE</span>
                <div style="font-size:0.82rem; color:#888; margin-top:4px; text-decoration:line-through;">{our_name}</div>
            </div>
            <div style="margin-bottom:0.4rem;">
                <span style="font-size:0.65rem; font-weight:700; color:#fff; background:#16a34a; padding:2px 6px; border-radius:3px;">AFTER</span>
                <div style="font-size:0.85rem; color:#111; font-weight:700; margin-top:4px;">{_after_name}</div>
            </div>
            <div style="font-size:0.7rem; color:#666;">추가 키워드: {_changes_html if _changes_html else '<span style="color:#16a34a;">— 현재 상품명 양호</span>'}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── 카테고리 + 스펙 진단 ──
        if category != "일반":
            st.markdown(f"<div style='display:inline-block; padding:0.2rem 0.6rem; border-radius:12px; background:#e8f4fd; color:#0369a1; font-size:0.75rem; font-weight:600;'>📂 {category}</div>", unsafe_allow_html=True)

        p_cols = st.columns(2)
        with p_cols[0]:
            st.markdown("**📝 상품명 진단**")
            if issues:
                for issue in issues:
                    st.markdown(f"""
                    <div style="padding:0.5rem 0.7rem; margin-bottom:0.3rem; border-radius:8px; background:#fef2f2; border-left:4px solid #ef4444;">
                        <span style="font-size:0.65rem; font-weight:700; color:#fff; background:#ef4444; padding:2px 6px; border-radius:4px;">수정</span>
                        <span style="font-size:0.88rem; font-weight:600;"> {issue}</span>
                    </div>
                    """, unsafe_allow_html=True)
            if found_specs:
                specs_html = " ".join([f"<span style='display:inline-block; padding:2px 7px; margin:2px; border-radius:4px; background:#f0fdf4; color:#16a34a; font-size:0.82rem; border:1px solid #bbf7d0;'>✅ {s}</span>" for s in found_specs])
                st.markdown(f"<div style='margin:0.3rem 0;'>{specs_html}</div>", unsafe_allow_html=True)
            if suggestions:
                for sug in suggestions[:4]:
                    st.markdown(f"""
                    <div style="padding:0.45rem 0.7rem; margin-bottom:0.25rem; border-radius:8px; background:#fffbeb; border-left:4px solid #f59e0b;">
                        <span style="font-size:0.65rem; font-weight:700; color:#fff; background:#f59e0b; padding:2px 6px; border-radius:4px;">권장</span>
                        <span style="font-size:0.85rem;"> {sug}</span>
                    </div>
                    """, unsafe_allow_html=True)
                if len(suggestions) > 4:
                    st.caption(f"...외 {len(suggestions)-4}개 항목")
            if not issues and not suggestions:
                st.success("✅ 상품명 구성 양호")

        with p_cols[1]:
            st.markdown("**📸 썸네일 진단**")
            if our_image:
                st.image(our_image, width=110)
            for issue in thumb_analysis.get("issues", []):
                st.markdown(f"""
                <div style="padding:0.45rem 0.7rem; margin-bottom:0.25rem; border-radius:8px; background:#fef2f2; border-left:4px solid #ef4444;">
                    <span style="font-size:0.65rem; font-weight:700; color:#fff; background:#ef4444; padding:2px 6px; border-radius:4px;">수정</span>
                    <span style="font-size:0.85rem;"> {issue}</span>
                </div>
                """, unsafe_allow_html=True)
            for sug in thumb_analysis.get("suggestions", []):
                st.markdown(f"""
                <div style="padding:0.45rem 0.7rem; margin-bottom:0.25rem; border-radius:8px; background:#fffbeb; border-left:4px solid #f59e0b;">
                    <span style="font-size:0.65rem; font-weight:700; color:#fff; background:#f59e0b; padding:2px 6px; border-radius:4px;">권장</span>
                    <span style="font-size:0.85rem;"> {sug}</span>
                </div>
                """, unsafe_allow_html=True)

        # 차별화 전략
        if diff_tips:
            st.markdown("**🎯 카테고리 차별화**")
            dt_cols = st.columns(min(len(diff_tips), 3))
            for i, tip in enumerate(diff_tips):
                with dt_cols[i % len(dt_cols)]:
                    st.markdown(f"""
                    <div style="padding:0.5rem 0.7rem; border-radius:8px; background:linear-gradient(135deg, #eff6ff, #f0f9ff); border:1px solid #bfdbfe;">
                        <div style="font-size:0.88rem; color:#1e40af;">💎 {tip}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # ── 리뷰 분석 (이 탭에 통합) ──
        st.markdown("---")
        st.markdown("**💬 리뷰 분석**")
        if detail_data_extra and not detail_data_extra.get("error"):
            info_cols = st.columns(3)
            info_cols[0].markdown(f"스토어: **{detail_data_extra.get('store_name', '-')}**")
            info_cols[1].markdown(f"카테고리: **{detail_data_extra.get('category', '-')}**")
            info_cols[2].markdown(f"상태: **{detail_data_extra.get('status', '-')}**")

        if review_summary["pros"] or review_summary["cons"]:
            rv_cols = st.columns(2)
            with rv_cols[0]:
                st.markdown("👍 **장점**")
                for p in review_summary["pros"]:
                    st.markdown(f"&nbsp;&nbsp;✅ {p}")
                if not review_summary["pros"]:
                    st.caption("추출된 장점 없음")
            with rv_cols[1]:
                st.markdown("👎 **개선점**")
                for c in review_summary["cons"]:
                    st.markdown(f"&nbsp;&nbsp;⚠️ {c}")
                if not review_summary["cons"]:
                    st.caption("추출된 단점 없음")
            if blog_reviews:
                with st.expander("📝 리뷰 출처", expanded=False):
                    for b in blog_reviews[:3]:
                        st.markdown(f"[{b['title'][:40]}...]({b['link']})")
        else:
            st.caption("블로그 리뷰 데이터 없음")

    # ── 탭 3: 종합 액션플랜 (실행 체크리스트) ──
    with tab_action:
        st.markdown("##### ✅ 실행 체크리스트")
        st.caption("우선순위순으로 정리. 위에서부터 하나씩 처리하세요.")

        _checklist = []
        _num = 0

        # 1. 가격 관련
        if our_unit and comps and our_unit > comps[0]["개당가격"]:
            _num += 1
            _rec_unit = round(comps[0]["개당가격"] * 1.1)
            _rec_total = round(_rec_unit * our_qty) if our_qty else our_price
            _checklist.append(("긴급", "#ef4444", f"가격을 {_rec_total:,}원으로 수정 (최저가 대비 +10%, 개당 {_rec_unit:,}원)"))

        # 2. 상품명 이슈
        for issue in issues:
            _num += 1
            _checklist.append(("긴급", "#ef4444", f"상품명 수정: {issue}"))

        # 3. 순위 문제
        if our_rank > 30:
            _num += 1
            _checklist.append(("긴급", "#ef4444", f"검색 순위 {our_rank}위 — 광고 또는 가격/키워드 개선"))

        # 4. 상품명 개선
        if _changes_html:
            _num += 1
            _checklist.append(("중요", "#f59e0b", f"상품명에 키워드 추가 (위 Before→After 참고)"))

        # 5. 썸네일
        if our_unit and our_qty:
            _num += 1
            _checklist.append(("중요", "#f59e0b", f"썸네일에 '개당 {our_unit:,}원' 텍스트 삽입"))

        for issue in thumb_analysis.get("issues", []):
            _num += 1
            _checklist.append(("중요", "#f59e0b", f"썸네일: {issue}"))

        # 6. 상세페이지 CTA 관련 (핵심만)
        _num += 1
        _brand_name = extract_brand(our_name)
        _checklist.append(("중요", "#f59e0b", f"상세페이지 상단에 '✅무료배송 ✅당일출고 ✅환불보장' 배지 추가"))
        _num += 1
        _checklist.append(("권장", "#22c55e", f"'{_brand_name} 시리즈 누적 판매 N만개' 사회적 증거 배지 삽입"))
        _num += 1
        _checklist.append(("권장", "#22c55e", f"'오늘 17시 이전 주문 → 당일 출고' 긴급성 문구 추가"))
        _num += 1
        _checklist.append(("권장", "#22c55e", f"상세페이지 중간·하단에 CTA 버튼 반복 배치"))

        # 상품명 개선 제안
        for sug in suggestions[:3]:
            _num += 1
            _checklist.append(("권장", "#22c55e", sug))

        # 렌더링
        for idx, (pri, color, text) in enumerate(_checklist):
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:0.6rem; padding:0.5rem 0.8rem; margin-bottom:0.3rem; border-radius:8px; background:#fff; border:1px solid #f0f0f0; border-left:4px solid {color};">
                <span style="font-size:1rem; color:#ccc;">☐</span>
                <span style="font-size:0.68rem; font-weight:700; color:#fff; background:{color}; padding:2px 7px; border-radius:4px; flex-shrink:0;">{pri}</span>
                <span style="font-size:0.9rem; color:#333;">{text}</span>
            </div>
            """, unsafe_allow_html=True)

        # CTA 세부 전략 (접힘)
        with st.expander("📖 CTA 전략 상세 (참고용)", expanded=False):
            _cta_sections = [
                ("social_proof", "사회적 증거", "👥", "#8b5cf6", "#f5f3ff"),
                ("fomo", "FOMO 전략", "⏰", "#ef4444", "#fef2f2"),
                ("cart_abandon", "이탈 방지", "🛒", "#f59e0b", "#fffbeb"),
                ("cta_button", "CTA 버튼", "🔘", "#06b6d4", "#ecfeff"),
            ]
            # 2x2 그리드 배치
            for row_i in range(0, len(_cta_sections), 2):
                _grid = st.columns(2)
                for col_i in range(2):
                    si = row_i + col_i
                    if si >= len(_cta_sections):
                        break
                    section_key, section_title, section_icon, accent, bg = _cta_sections[si]
                    with _grid[col_i]:
                        st.markdown(f"**{section_icon} {section_title}**")
                        for item in cta[section_key]["items"]:
                            example = item.get("example", "")
                            st.markdown(f"""
                            <div style="padding:0.45rem 0.7rem; margin:0.2rem 0; border-radius:8px; background:{bg}; border-left:3px solid {accent};">
                                <div style="font-size:0.88rem; font-weight:700; color:#334155;">{item.get('type','')}</div>
                                <div style="font-size:0.82rem; color:#475569; margin-top:2px;">{item['action']}</div>
                                {f'<div style="font-size:0.78rem; color:#555; margin-top:3px;">✍️ {example}</div>' if example else ''}
                            </div>
                            """, unsafe_allow_html=True)



# ─────────────────────────────────────────────
# 메인 - 헤더 배너
# ─────────────────────────────────────────────
today = datetime.now(KST)
weekdays = ["월", "화", "수", "목", "금", "토", "일"]
weekday_kr = weekdays[today.weekday()]

st.markdown(f"""
<div class="header-banner">
    <div class="logo"><div class="kb-text">KINI<br>BINI</div><div class="kb-sub">Momsbebe Premium</div></div>
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
# 클라우드 환경: Gist에서 데이터 복원 (앱 시작 시 1회)
_gist_restore_all()

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
                "updated": datetime.now(KST).strftime("%Y-%m-%d %H:%M"),
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

    # ── 판매 대응 상품 요약 ──
    st.markdown('<div class="section-title"><span class="icon">📋</span> 판매 대응 현황</div>', unsafe_allow_html=True)

    insight_data = fetch_sales_insight()

    if insight_data["status"] in ("분석 완료", "송장 미출력"):
        anomalies = insight_data["anomalies"]
        watchlist = insight_data.get("watchlist", [])
        daily_sellers = insight_data["daily_sellers"]
        _today_shipped = insight_data.get("today_shipped", False)

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
        _ship_label = f"{insight_data['today_count']}개" if _today_shipped else "⏳ 대기"
        _ship_sub = "현재까지" if _today_shipped else "송장 미출력"
        ins_cols[1].markdown(f"""
        <div class="kpi-card">
            <div class="icon">📦</div>
            <div class="label">오늘 출고</div>
            <div class="value">{_ship_label}</div>
            <div class="sub">{_ship_sub}</div>
        </div>
        """, unsafe_allow_html=True)
        if _today_shipped:
            _urgent_color = "#f5576c" if anomalies else "#22c55e"
            _urgent_val = f"{len(anomalies)}개"
            _urgent_sub = "매일 출고 → 오늘 0"
            _watch_color = "#f59e0b" if watchlist else "#22c55e"
            _watch_val = f"{len(watchlist)}개"
            _watch_sub = "간헐 출고 → 오늘 0"
        else:
            _urgent_color = "#9ca3af"
            _urgent_val = "—"
            _urgent_sub = "송장 출력 후 확인"
            _watch_color = "#9ca3af"
            _watch_val = "—"
            _watch_sub = "송장 출력 후 확인"
        ins_cols[2].markdown(f"""
        <div class="kpi-card" style="border-color: {_urgent_color}40;">
            <div class="icon">🔴</div>
            <div class="label">긴급 대응</div>
            <div class="value" style="color: {_urgent_color};">{_urgent_val}</div>
            <div class="sub">{_urgent_sub}</div>
        </div>
        """, unsafe_allow_html=True)
        ins_cols[3].markdown(f"""
        <div class="kpi-card" style="border-color: {_watch_color}40;">
            <div class="icon">🟡</div>
            <div class="label">추가 확인</div>
            <div class="value" style="color: {_watch_color};">{_watch_val}</div>
            <div class="sub">{_watch_sub}</div>
        </div>
        """, unsafe_allow_html=True)

        # 대시보드에서는 간단 요약만 표시
        if not _today_shipped:
            st.info("📋 오늘 송장이 아직 출력되지 않았습니다. 송장 출력(출고 처리) 후 판매 대응 상품이 자동으로 표시됩니다.")
        else:
            product_names_map = fetch_product_names()
            if anomalies:
                st.markdown(f"**🔴 긴급 대응 {len(anomalies)}개** — 상세 내용은 '판매 대응' 메뉴에서 확인하세요.")
                for item in anomalies[:5]:
                    pid = item["product_id"]
                    name = product_names_map.get(pid, pid)
                    brand = extract_brand(name)
                    st.markdown(f"- 🔴 **[{brand}]** {name} — 일평균 {item['avg_qty']}개, 오늘 0개")
                if len(anomalies) > 5:
                    st.caption(f"...외 {len(anomalies) - 5}개 상품")
            if watchlist:
                st.markdown(f"**🟡 추가 확인 {len(watchlist)}개** — 긴급 대응 완료 후 확인하세요.")
                for item in watchlist[:3]:
                    pid = item["product_id"]
                    name = product_names_map.get(pid, pid)
                    brand = extract_brand(name)
                    st.markdown(f"- 🟡 **[{brand}]** {name} — 일평균 {item['avg_qty']}개, 오늘 0개")
                if len(watchlist) > 3:
                    st.caption(f"...외 {len(watchlist) - 3}개 상품")
            if not anomalies and not watchlist:
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

    # ── CEO 대응 현황 (대시보드 메인) ──
    _dash_today_str = today.strftime("%Y-%m-%d")
    _dash_tasks = load_json(TASKS_FILE, {"tasks": []}).get("tasks", [])
    _dash_today_actions = [t for t in _dash_tasks if t.get("due") == _dash_today_str and t.get("action")]
    _dash_today_total = [t for t in _dash_tasks if t.get("due") == _dash_today_str]
    _dash_done_count = sum(1 for t in _dash_today_total if t.get("done"))

    if _dash_today_actions or _dash_today_total:
        st.markdown('<div class="section-title"><span class="icon">📋</span> 오늘 직원 대응 현황</div>', unsafe_allow_html=True)

        # 요약 카드
        _dash_rate = round(_dash_done_count / len(_dash_today_total) * 100) if _dash_today_total else 0
        _dc1, _dc2, _dc3 = st.columns(3)
        _dc1.metric("전체 업무", f"{len(_dash_today_total)}건")
        _dc2.metric("완료", f"{_dash_done_count}건")
        _dc3.metric("대응률", f"{_dash_rate}%")

        if _dash_today_actions:
            for t in sorted(_dash_today_actions, key=lambda x: x.get("done_at", ""), reverse=True):
                _a = t.get("action", {})
                _time = _a.get("time", t.get("done_at", "")[-5:])
                _type_lbl = _a.get("label", "✅")
                _pname = t.get("meta", {}).get("product_name", t.get("title", ""))
                _detail = _a.get("detail", "")
                _memo = _a.get("memo", "")
                _detail_html = f'<span style="color:#1565c0; font-size:0.78rem;"> — 📋 {_detail}</span>' if _detail else ""
                _memo_html = f'<span style="color:#888; font-size:0.72rem;"> 💬 {_memo}</span>' if _memo else ""
                st.markdown(f"""
                <div style="padding:0.4rem 0.7rem; margin-bottom:0.2rem; border-radius:6px; background:#fafafa; border-left:3px solid #66bb6a;">
                    <span style="font-size:0.72rem; color:#999;">{_time}</span>
                    <span style="font-size:0.82rem; font-weight:600; margin-left:0.3rem;">{_type_lbl}</span>
                    <span style="font-size:0.82rem;"> {_pname}</span>
                    {_detail_html}{_memo_html}
                </div>
                """, unsafe_allow_html=True)
        elif _dash_today_total:
            st.info("아직 대응 완료된 업무가 없습니다.")


# ─────────────────────────────────────────────
# 🚨 판매 대응 페이지
# ─────────────────────────────────────────────
elif current_page == "sales_inventory":
    st.markdown('<div class="section-title"><span class="icon">📦</span> 판매대응 및 재고</div>', unsafe_allow_html=True)

    insight_data = fetch_sales_insight()
    product_names_map = fetch_product_names()
    shop_list = fetch_shop_list()

    if insight_data["status"] in ("분석 완료", "송장 미출력"):
        anomalies = insight_data["anomalies"]
        watchlist = insight_data.get("watchlist", [])
        daily_sellers = insight_data["daily_sellers"]
        _today_shipped_inv = insight_data.get("today_shipped", False)

        # 송장 미출력 안내
        if not _today_shipped_inv:
            st.info("📋 오늘 송장이 아직 출력되지 않았습니다. 송장 출력(출고 처리) 후 판매 대응 상품이 자동으로 표시됩니다.")

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
        _ship_label2 = f"{insight_data['today_count']}개" if _today_shipped_inv else "⏳ 대기"
        _ship_sub2 = "현재까지" if _today_shipped_inv else "송장 미출력"
        ins_cols[1].markdown(f"""
        <div class="kpi-card">
            <div class="icon">📦</div>
            <div class="label">오늘 출고</div>
            <div class="value">{_ship_label2}</div>
            <div class="sub">{_ship_sub2}</div>
        </div>
        """, unsafe_allow_html=True)
        if _today_shipped_inv:
            _uc = "#f5576c" if anomalies else "#22c55e"
            _uv = f"{len(anomalies)}개"
            _us = "매일 출고 → 오늘 0"
            _wc = "#f59e0b" if watchlist else "#22c55e"
            _wv = f"{len(watchlist)}개"
            _ws = "간헐 출고 → 오늘 0"
        else:
            _uc = _wc = "#9ca3af"
            _uv = _wv = "—"
            _us = _ws = "송장 출력 후 확인"
        ins_cols[2].markdown(f"""
        <div class="kpi-card" style="border-color: {_uc}40;">
            <div class="icon">🔴</div>
            <div class="label">긴급 대응</div>
            <div class="value" style="color: {_uc};">{_uv}</div>
            <div class="sub">{_us}</div>
        </div>
        """, unsafe_allow_html=True)
        ins_cols[3].markdown(f"""
        <div class="kpi-card" style="border-color: {_wc}40;">
            <div class="icon">🟡</div>
            <div class="label">추가 확인</div>
            <div class="value" style="color: {_wc};">{_wv}</div>
            <div class="sub">{_ws}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── 판매처별 주문 데이터 수집 (최근 7일, 캐시) ──
        from collections import defaultdict, Counter

        @st.cache_data(ttl=600, show_spinner=False)
        def _build_order_product_shops(_shop_list_tuple):
            """주문 데이터를 집계하여 {product_id: {shop_name: {qty, amount, order_count, shop_product_ids}}} 반환"""
            shop_dict = dict(_shop_list_tuple)
            result = {}
            date_strings = tuple(
                (datetime.now(KST) - timedelta(days=d)).strftime("%Y-%m-%d") for d in range(1, 8)
            )
            all_date_orders = fetch_orders_parallel(date_strings)
            for date_str in date_strings:
                orders = all_date_orders.get(date_str, [])
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

        # ── 상품 리스트 렌더링 헬퍼 (4개 탭 공용) ──
        def _render_product_list(products, tab_prefix, show_today_col=False):
            """products: list of dict — 테이블 행 클릭 → 판매처 팝업"""
            if not products:
                st.info("해당 상품이 없습니다.")
                return

            # 테이블 데이터 구성
            table_rows = []
            items_list = []  # 인덱스 기반 접근
            product_map = {}  # 상품명 → item
            for item in products:
                pid = item["product_id"]
                name = product_names_map.get(pid, pid)
                brand = extract_brand(name)
                avg_qty = int(item.get("avg_qty", 0) or 0)
                row = {
                    "브랜드": str(brand),
                    "상품코드": str(pid),
                    "상품명": str(name),
                    "일평균": avg_qty,
                    "출고일수": f"{item.get('active_days', 0)}/{item.get('total_days', 7)}일",
                }
                if show_today_col:
                    row["오늘출고"] = "✅" if item.get("today_shipped") else "❌"
                table_rows.append(row)
                items_list.append(item)
                product_map[name] = item

            df = pd.DataFrame(table_rows)
            df["일평균"] = df["일평균"].astype(int)

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

            # 상품 검색/선택 → 판매처 상세
            product_names_list = list(product_map.keys())

            # 업무보드에서 바로 이동 시 자동 선택
            _auto_pid = st.session_state.pop("auto_select_product", None)
            _default_name = ""
            if _auto_pid:
                _auto_name = product_names_map.get(_auto_pid, _auto_pid)
                if _auto_name in product_map:
                    _default_name = _auto_name
                    st.session_state[f"{tab_prefix}_select"] = _default_name

            sel_cols = st.columns([4, 1])
            with sel_cols[0]:
                selected_name = st.selectbox(
                    "상품 선택",
                    options=[""] + product_names_list,
                    format_func=lambda x: "🔍 상품명을 입력하여 검색..." if x == "" else x,
                    key=f"{tab_prefix}_select",
                    label_visibility="collapsed",
                )
            with sel_cols[1]:
                btn_disabled = (selected_name == "" or selected_name not in product_map)
                if st.button("📊 판매처 상세", key=f"{tab_prefix}_btn", use_container_width=True, disabled=btn_disabled):
                    sel_item = product_map[selected_name]
                    sel_pid = sel_item["product_id"]
                    sel_name = product_names_map.get(sel_pid, sel_pid)
                    shop_data = _prepare_shop_data(sel_pid, sel_name, sel_item)
                    if shop_data:
                        st.session_state["_shop_detail_data"] = shop_data
                        show_shop_detail_dialog()
                    else:
                        st.toast(f"{sel_name}: 최근 7일 주문 데이터 없음")

        # ═══ 탭 (판매대응 + 재고 통합) ═══
        inventory_data = fetch_current_inventory()
        all_brands = set()
        for name in product_names_map.values():
            all_brands.add(extract_brand(name))
        total_all_sku = len(product_names_map)

        _dormant_count_inv = len([s for s in daily_sellers if not s["today_shipped"]]) if _today_shipped_inv else 0
        tab_all, tab_today, tab_anomaly, tab_watch, tab_sku, tab_low, tab_brand = st.tabs([
            f"📊 최근 5일 출고 ({insight_data['total_tracked']})",
            f"📦 오늘 출고 ({insight_data['today_count']})",
            f"🔴 긴급 대응 ({len(anomalies)})",
            f"🟡 추가 확인 ({len(watchlist)})",
            f"🏷️ 전체 SKU ({total_all_sku})",
            f"⚠️ 재고 부족 ({inventory_data['low_stock_count']})",
            f"🏷️ 브랜드별 ({len(all_brands)})",
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
            if not _today_shipped_inv:
                st.info("📋 송장 출력 후 긴급 대응 상품이 표시됩니다.")
            elif anomalies:
                anomaly_sorted = sorted(anomalies, key=lambda x: (extract_brand(product_names_map.get(x["product_id"], "")), -x.get("avg_qty", 0)))
                _render_product_list(anomaly_sorted, "tab_anom")
            else:
                st.success("✅ 긴급 대응 상품 없음 — 매일 출고 상품이 오늘도 정상 출고 중입니다.")

        with tab_watch:
            if not _today_shipped_inv:
                st.info("📋 송장 출력 후 추가 확인 상품이 표시됩니다.")
            elif watchlist:
                watch_sorted = sorted(watchlist, key=lambda x: (extract_brand(product_names_map.get(x["product_id"], "")), -x.get("avg_qty", 0)))
                _render_product_list(watch_sorted, "tab_watch")
            else:
                st.success("✅ 추가 확인 상품 없음")

        with tab_sku:
            stock_map = {}
            for item in inventory_data.get("items", []):
                stock_map[item["product_id"]] = item
            rows = []
            for pid, name in sorted(product_names_map.items(), key=lambda x: x[1]):
                brand = extract_brand(name)
                stock_info = stock_map.get(pid)
                if stock_info:
                    rows.append({"브랜드": brand, "상품코드": pid, "상품명": name, "재고수량": str(stock_info["stock_qty"]), "출고량": str(stock_info["trans_qty"]), "오늘변동": "O"})
                else:
                    rows.append({"브랜드": brand, "상품코드": pid, "상품명": name, "재고수량": "—", "출고량": "—", "오늘변동": ""})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=600)

        with tab_low:
            low = inventory_data.get("low_items", [])
            low_sorted = sorted(low, key=lambda x: x["stock_qty"])
            if low_sorted:
                rows = []
                for item in low_sorted:
                    pid = item["product_id"]
                    name = product_names_map.get(pid, pid)
                    brand = extract_brand(name)
                    if item["stock_qty"] < 0:
                        status = "⛔ 마이너스"
                    elif item["stock_qty"] == 0:
                        status = "🔴 품절"
                    else:
                        status = "🔴 부족"
                    rows.append({"브랜드": brand, "상품코드": pid, "상품명": name, "재고수량": item["stock_qty"], "출고량": item["trans_qty"], "상태": status})
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
                              column_config={"재고수량": st.column_config.NumberColumn(format="%d개")},
                              height=600)
            else:
                st.success("✅ 재고 부족 품목이 없습니다.")

        with tab_brand:
            from collections import defaultdict as _dd
            brand_inv = _dd(lambda: {"품목수": 0, "출고품목": 0, "총출고": 0, "부족": 0, "품절": 0})
            for pid, name in product_names_map.items():
                brand = extract_brand(name)
                brand_inv[brand]["품목수"] += 1
            stock_map = {}
            for item in inventory_data.get("items", []):
                stock_map[item["product_id"]] = item
            for pid, name in product_names_map.items():
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
                    "브랜드": brand, "총 SKU": info["품목수"], "오늘 출고 품목": info["출고품목"],
                    "총 출고량": info["총출고"], "재고 부족": info["부족"], "품절": info["품절"],
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    elif insight_data["status"] == "미연동":
        st.info("📡 원싱크(OneWMS) API 연동 후 판매 대응 분석이 가능합니다.")
    else:
        st.info(f"📊 판매 인사이트: {insight_data['status']}")


# ─────────────────────────────────────────────
# 🛒 가격 모니터링 페이지
# ─────────────────────────────────────────────
elif current_page == "price_monitor":
    st.markdown('<div class="section-title"><span class="icon">🛒</span> 실시간 가격 모니터링 (네이버 쇼핑)</div>', unsafe_allow_html=True)

    # 업무일지에서 넘어온 자동 검색 키워드
    _auto_kw = st.session_state.pop("_auto_price_keyword", "")

    # 검색 폼 (메인 영역에 배치)
    search_col1, search_col2 = st.columns([4, 1])
    with search_col1:
        search_keyword = st.text_input("🔍 검색 키워드", value=_auto_kw, placeholder="검색할 상품 키워드를 입력하세요...", label_visibility="collapsed")
    with search_col2:
        search_btn = st.button("🔍 검색", type="primary", use_container_width=True)
    # 자동 검색 트리거
    if _auto_kw and not search_btn:
        search_btn = True

    # 최근 검색 이력 (클릭 재검색 + 삭제 기능)
    history = load_search_history()
    if history:
        st.caption("최근 검색")
        hist_cols_per_row = 5
        for row_start in range(0, min(len(history), 10), hist_cols_per_row):
            row_items = history[row_start:row_start + hist_cols_per_row]
            cols = st.columns(len(row_items))
            for i, kw in enumerate(row_items):
                with cols[i]:
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        if st.button(f"🔍 {kw}", key=f"hist_{row_start+i}", use_container_width=True):
                            search_keyword = kw
                            search_btn = True
                    with c2:
                        if st.button("✕", key=f"hist_del_{row_start+i}", use_container_width=True):
                            remove_from_search_history(kw)
                            st.rerun()

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

    # ── 커스텀 CSS (리디자인) ──
    st.markdown("""
    <style>
    /* ── KPI 요약 카드 ── */
    .log-kpi-row { display: flex; gap: 0.4rem; margin-bottom: 0.6rem; }
    .log-kpi {
        flex: 1; border-radius: 10px; padding: 0.35rem 0.5rem; text-align: center;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06); position: relative; overflow: hidden;
    }
    .log-kpi .kpi-icon { font-size: 0.95rem; }
    .log-kpi .kpi-label { font-size: 0.65rem; color: #666; margin-top: 1px; }
    .log-kpi .kpi-value { font-size: 1.05rem; font-weight: 800; margin: 1px 0; }
    .log-kpi .kpi-sub { font-size: 0.6rem; color: #999; }
    .log-kpi.urgent { background: linear-gradient(135deg, #fff5f5, #ffe0e0); border: 1px solid #ffcdd2; }
    .log-kpi.urgent .kpi-value { color: #d32f2f; }
    .log-kpi.watch { background: linear-gradient(135deg, #fffbf0, #fff3e0); border: 1px solid #ffe0b2; }
    .log-kpi.watch .kpi-value { color: #e65100; }
    .log-kpi.done { background: linear-gradient(135deg, #f1faf1, #e8f5e9); border: 1px solid #c8e6c9; }
    .log-kpi.done .kpi-value { color: #2e7d32; }
    .log-kpi.rate { background: linear-gradient(135deg, #f3f0ff, #ede7f6); border: 1px solid #d1c4e9; }
    .log-kpi.rate .kpi-value { color: #5e35b1; }

    /* ── 프로그레스 바 ── */
    .progress-container {
        background: #e8e8e8; border-radius: 10px; height: 8px;
        overflow: hidden; margin: 0 0 1.2rem 0; position: relative;
    }
    .progress-fill {
        height: 100%; border-radius: 10px;
        background: linear-gradient(90deg, #43a047, #66bb6a);
        transition: width 0.5s ease;
    }

    /* ── 송장 미출력 오버레이 ── */
    .shipment-pending {
        background: #f8f9fa; border: 2px dashed #ccc; border-radius: 12px;
        padding: 2rem 1rem; text-align: center; color: #888; margin: 1rem 0;
    }
    .shipment-pending .sp-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
    .shipment-pending .sp-title { font-size: 1rem; font-weight: 700; color: #555; }
    .shipment-pending .sp-desc { font-size: 0.82rem; color: #999; margin-top: 0.3rem; }

    /* ── 섹션 헤더 ── */
    .log-section {
        display: flex; align-items: center; gap: 0.5rem;
        padding: 0.4rem 0; margin: 0.6rem 0 0.3rem 0;
        font-weight: 700; font-size: 0.9rem; color: #333;
        border-bottom: 2px solid #eee;
    }
    .log-section .sec-count {
        background: #e3f2fd; color: #1565c0; padding: 1px 8px;
        border-radius: 10px; font-size: 0.72rem; font-weight: 600;
    }
    .log-section.urgent-sec { border-bottom-color: #ef9a9a; }
    .log-section.urgent-sec .sec-count { background: #ffebee; color: #c62828; }
    .log-section.watch-sec { border-bottom-color: #ffe0b2; }
    .log-section.watch-sec .sec-count { background: #fff3e0; color: #e65100; }
    .log-section.done-sec { border-bottom-color: #c8e6c9; }
    .log-section.done-sec .sec-count { background: #e8f5e9; color: #2e7d32; }

    /* ── 컴팩트 태스크 카드 ── */
    .task-row {
        display: flex; align-items: center; gap: 0.5rem;
        padding: 0.55rem 0.8rem; margin-bottom: 0.35rem;
        border-radius: 10px; background: #fff;
        border: 1px solid #f0f0f0; transition: all 0.15s;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .task-row:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-color: #ddd; }
    .task-row.urgent-row { border-left: 4px solid #e53935; }
    .task-row.watch-row { border-left: 4px solid #f59e0b; }
    .task-row.manual-row { border-left: 4px solid #1e88e5; }
    .task-row.done-row { opacity: 1; background: #f9fdf9; }
    .task-row .tr-icon { font-size: 1rem; flex-shrink: 0; }
    .task-row .tr-body { flex: 1; min-width: 0; }
    .task-row .tr-name {
        font-weight: 700; font-size: 0.85rem; color: #333;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .task-row.done-row .tr-name { text-decoration: none; color: #333; }
    .task-row .tr-detail {
        font-size: 0.72rem; color: #888; margin-top: 1px;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .task-row .tr-badge {
        display: inline-block; padding: 1px 6px; border-radius: 8px;
        font-size: 0.62rem; font-weight: 600; margin-left: 4px;
    }
    .tr-badge.bg-red { background: #ffebee; color: #c62828; }
    .tr-badge.bg-orange { background: #fff3e0; color: #e65100; }
    .tr-badge.bg-green { background: #e8f5e9; color: #2e7d32; }
    .tr-badge.bg-blue { background: #e3f2fd; color: #1565c0; }
    .tr-badge.bg-gray { background: #f5f5f5; color: #666; }

    /* ── 대응 로그 테이블 ── */
    .action-log-row {
        display: flex; align-items: center; gap: 0.5rem;
        padding: 0.35rem 0.6rem; font-size: 0.78rem;
        border-bottom: 1px solid #f5f5f5;
    }
    .action-log-row:last-child { border-bottom: none; }
    .al-time { color: #999; font-size: 0.72rem; width: 45px; flex-shrink: 0; }
    .al-type { font-weight: 600; width: 110px; flex-shrink: 0; }
    .al-name { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .al-memo { color: #666; font-size: 0.72rem; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

    /* ── 수동 태스크 카드 ── */
    .manual-task {
        display: flex; align-items: center; gap: 0.6rem;
        padding: 0.5rem 0.8rem; margin-bottom: 0.3rem;
        border-radius: 8px; background: #fff; border: 1px solid #eee;
    }
    .manual-task.mt-done { opacity: 0.5; }
    .manual-task .mt-title { flex: 1; font-size: 0.85rem; font-weight: 600; }
    .manual-task.mt-done .mt-title { text-decoration: line-through; color: #999; }
    .mt-pri {
        display: inline-block; padding: 1px 8px; border-radius: 8px;
        font-size: 0.68rem; font-weight: 600; color: #fff;
    }
    .mt-pri.pri-urgent { background: #e53935; }
    .mt-pri.pri-normal { background: #1e88e5; }
    .mt-pri.pri-routine { background: #90a4ae; }

    /* ── 달력 / 주간 뷰 ── */
    .cal-grid {
        display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px;
        margin: 0.5rem 0;
    }
    .cal-header {
        text-align: center; font-weight: 700; font-size: 0.75rem;
        padding: 4px 0; color: #666;
    }
    .cal-cell {
        text-align: center; padding: 6px 2px; border-radius: 6px;
        font-size: 0.78rem; min-height: 38px; cursor: pointer;
        border: 1px solid #eee; transition: background 0.15s;
    }
    .cal-cell:hover { background: #e3f2fd; }
    .cal-cell.today { background: #e8f5e9; font-weight: 700; border-color: #66bb6a; }
    .cal-cell.has-tasks { position: relative; }
    .cal-cell .task-dot {
        display: inline-block; width: 6px; height: 6px;
        background: #1e88e5; border-radius: 50%; margin-top: 2px;
    }
    .cal-cell.empty { border: none; cursor: default; }
    .week-col {
        background: var(--background-color, #fafafa);
        border-radius: 8px; padding: 0.5rem;
        border: 1px solid #eee; min-height: 80px;
    }
    .week-col-header {
        font-weight: 700; font-size: 0.8rem; text-align: center;
        padding-bottom: 0.3rem; border-bottom: 1px solid #ddd; margin-bottom: 0.4rem;
    }
    .week-task-item {
        font-size: 0.75rem; padding: 2px 4px; border-radius: 4px;
        margin-bottom: 2px; background: #e3f2fd;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .week-task-item.done { text-decoration: line-through; opacity: 0.5; }

    /* ── 메모 ── */
    .sticky-note {
        border-radius: 8px; padding: 1rem; min-height: 100px;
        box-shadow: 2px 3px 10px rgba(0,0,0,0.1);
        position: relative; margin-bottom: 0.8rem;
        font-size: 0.88rem; line-height: 1.5;
    }
    .sticky-note.rot-1 { transform: rotate(-1.5deg); }
    .sticky-note.rot-2 { transform: rotate(1deg); }
    .sticky-note.rot-3 { transform: rotate(-0.5deg); }
    .sticky-note .note-meta {
        margin-top: 0.7rem; font-size: 0.72rem; opacity: 0.6;
        display: flex; justify-content: space-between; align-items: center;
    }

    /* ── selectbox 손가락 커서 ── */
    [data-testid="stSelectbox"] > div > div {
        cursor: pointer !important;
    }
    [data-testid="stSelectbox"] svg {
        cursor: pointer !important;
    }

    /* ── 업무일지 내 버튼 축소 ── */
    [data-testid="stVerticalBlock"] [data-testid="stButton"] button {
        font-size: 0.75rem !important;
        padding: 0.15rem 0.5rem !important;
        min-height: 1.6rem !important;
        height: 1.6rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── 데이터 로드 ──
    now = datetime.now(KST)
    today_str = now.strftime("%Y-%m-%d")
    yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")

    tasks_data = load_json(TASKS_FILE, {"tasks": []})
    all_tasks = tasks_data.get("tasks", [])
    sticky_data = load_json(STICKY_FILE, {"notes": []})
    all_notes = sticky_data.get("notes", [])

    # ── 헬퍼 함수 ──
    def save_tasks():
        save_json(TASKS_FILE, {"tasks": all_tasks})

    def save_notes():
        save_json(STICKY_FILE, {"notes": all_notes})

    def add_task(title, task_type="daily", priority="normal", due=None, auto=False, writer="MD", meta=None, _skip_save=False):
        if due is None:
            due = today_str
        new_task = {
            "id": str(uuid.uuid4()),
            "title": title,
            "type": task_type,
            "priority": priority,
            "done": False,
            "created": today_str,
            "due": due,
            "done_at": None,
            "auto": auto,
            "writer": writer,
        }
        if meta:
            new_task["meta"] = meta
        all_tasks.append(new_task)
        if not _skip_save:
            save_tasks()
        return new_task

    def toggle_task(task_id, done_value):
        for t in all_tasks:
            if t["id"] == task_id:
                t["done"] = done_value
                t["done_at"] = now.strftime("%Y-%m-%d %H:%M") if done_value else None
                break
        save_tasks()

    def delete_task(task_id):
        nonlocal_tasks = [t for t in all_tasks if t["id"] != task_id]
        all_tasks.clear()
        all_tasks.extend(nonlocal_tasks)
        save_tasks()

    # ── 자동 업무 생성 (판매 이상 징후) ──
    try:
        insight = fetch_sales_insight()
        anomalies = insight.get("anomalies", [])
        _watchlist_log = insight.get("watchlist", [])
        _today_shipped_log = insight.get("today_shipped", False)
    except Exception:
        anomalies = []
        _watchlist_log = []
        _today_shipped_log = False

    try:
        _pname_map = fetch_product_names()
    except Exception:
        _pname_map = {}

    # 기존 자동태스크에서 meta 없는 구형 태스크 제거
    _old_auto = [t for t in all_tasks if t.get("auto") and t["due"] == today_str and not t.get("meta")]
    for _ot in _old_auto:
        all_tasks.remove(_ot)
    if _old_auto:
        save_tasks()

    # 송장 미출력 시: 기존 자동태스크 전체 삭제 (잘못된 데이터 기반)
    if not _today_shipped_log:
        _stale_auto = [t for t in all_tasks if t.get("auto") and t["due"] == today_str and t.get("meta")]
        if _stale_auto:
            for _st in _stale_auto:
                all_tasks.remove(_st)
            save_tasks()

    # 송장 출력 후에만 자동태스크 생성/동기화
    if _today_shipped_log:
        # 실시간 동기화: 출고 완료된 자동태스크 자동 완료 처리
        _all_active_pids = {a["product_id"] for a in anomalies} | {w["product_id"] for w in _watchlist_log}
        _sync_changed = False
        for t in all_tasks:
            if not (t.get("auto") and t["due"] == today_str and t.get("meta")):
                continue
            t_pid = t["meta"].get("product_id", "")
            if t_pid and t_pid not in _all_active_pids and not t.get("done"):
                t["done"] = True
                t["done_at"] = datetime.now(KST).strftime("%Y-%m-%d %H:%M")
                _sync_changed = True
        if _sync_changed:
            save_tasks()

        # 신규 자동태스크 생성 (긴급 대응 + 추가 확인) — 배치 저장
        existing_auto_pids = {t.get("meta", {}).get("product_id") for t in all_tasks if t.get("auto") and t["due"] == today_str and t.get("meta")}
        _combined = [(a, "urgent") for a in anomalies] + [(w, "watch") for w in _watchlist_log]
        _auto_added = 0
        for item, level in _combined:
            pid = item.get("product_id", "")
            if pid in existing_auto_pids:
                continue
            pname = _pname_map.get(pid, pid)
            avg_qty = item.get("avg_qty", 0)
            active_days = item.get("active_days", 0)
            total_days = item.get("total_days", 5)
            total_qty = item.get("total_qty", 0)
            _icon = "\U0001f534" if level == "urgent" else "\U0001f7e1"  # 🔴 or 🟡
            auto_title = f"{_icon} {pname}"
            add_task(
                auto_title, task_type="daily", priority=level,
                due=today_str, auto=True, writer="MD",
                _skip_save=True,
                meta={
                    "product_id": pid,
                    "product_name": pname,
                    "avg_qty": avg_qty,
                    "active_days": active_days,
                    "total_days": total_days,
                    "total_qty": total_qty,
                    "level": level,
                    "reason": f"최근 {total_days}일 중 {active_days}일 출고(일평균 {avg_qty}개) → 오늘 미출고",
                },
            )
            _auto_added += 1
        if _auto_added:
            save_tasks()

    # ── 어제 미완료 이월 — 배치 저장 ──
    yesterday_incomplete = [t for t in all_tasks if t.get("due") == yesterday_str and not t.get("done")]
    carried_ids = set()
    existing_today_titles = {t["title"] for t in all_tasks if t.get("due") == today_str}
    _carry_added = 0
    for t in yesterday_incomplete:
        carry_title = t["title"]
        if carry_title not in existing_today_titles:
            new_t = add_task(carry_title, task_type=t.get("type", "daily"), priority=t.get("priority", "normal"), due=today_str, writer=t.get("writer", "MD"), _skip_save=True)
            carried_ids.add(new_t["id"])
            _carry_added += 1
    if _carry_added:
        save_tasks()

    # 오늘 업무 필터
    today_tasks = [t for t in all_tasks if t.get("due") == today_str]
    done_count = sum(1 for t in today_tasks if t.get("done"))
    total_count = len(today_tasks)
    pct = round((done_count / total_count * 100), 1) if total_count > 0 else 0

    # ── 팝업 트리거 (tabs 밖에서 실행해야 @st.dialog 정상 작동) ──
    _pending = st.session_state.pop("_pending_shop_detail", None)
    if _pending:
        with st.spinner(f"📡 {_pending['pname']} 판매처 조회 중..."):
            _shop_data = quick_shop_detail(_pending["pid"], _pending["pname"], _pending.get("avg_qty", 0))
        if _shop_data:
            st.session_state["_shop_detail_data"] = _shop_data
            show_shop_detail_dialog()
        else:
            st.toast(f"{_pending['pname']}: 최근 7일 주문 데이터 없음")

    _pending_pages = st.session_state.pop("_pending_product_pages", None)
    if _pending_pages:
        with st.spinner(f"📡 {_pending_pages['pname']} 상품페이지 조회 중..."):
            _pages_data = quick_shop_detail(_pending_pages["pid"], _pending_pages["pname"], _pending_pages.get("avg_qty", 0))
        if _pages_data:
            st.session_state["_product_pages_data"] = _pages_data
            show_product_pages_dialog()
        else:
            st.toast(f"{_pending_pages['pname']}: 최근 7일 주문 데이터 없음")

    # ── 대응 완료 다이얼로그 트리거 ──
    _pending_action = st.session_state.pop("_pending_action_dialog", None)
    if _pending_action:
        st.session_state["_action_dialog_data"] = _pending_action
        show_action_dialog()

    # ── 대응 기록 결과 저장 ──
    _action_result = st.session_state.pop("_action_result", None)
    if _action_result:
        _ar_tid = _action_result["task_id"]
        for t in all_tasks:
            if t["id"] == _ar_tid:
                t["done"] = True
                t["done_at"] = datetime.now(KST).strftime("%Y-%m-%d %H:%M")
                t["action"] = {
                    "type": _action_result["action_type"],
                    "label": ACTION_TYPES.get(_action_result["action_type"], ""),
                    "detail": _action_result.get("detail", ""),
                    "memo": _action_result.get("memo", ""),
                    "worker": "MD",
                    "time": datetime.now(KST).strftime("%H:%M"),
                }
                break
        save_tasks()
        st.toast(f"✅ 대응 기록 완료")

    # ── 3 Tabs ──
    tab1, tab_log, tab2, tab3 = st.tabs(["\U0001f4c5 오늘 업무", "\U0001f4ca 대응 로그", "\U0001f4c6 주간/월간 계획", "\U0001f4cc 공유 메모"])

    # ════════════════════════════════════════════
    # Tab 1: 오늘 업무
    # ════════════════════════════════════════════
    with tab1:
        # 자동생성 태스크와 일반 태스크 분리
        auto_tasks = [t for t in today_tasks if t.get("auto") and t.get("meta")]
        urgent_tasks = [t for t in auto_tasks if t.get("meta", {}).get("level") == "urgent" or t.get("priority") == "urgent"]
        watch_tasks = [t for t in auto_tasks if t.get("meta", {}).get("level") == "watch"]
        manual_tasks = [t for t in today_tasks if not (t.get("auto") and t.get("meta"))]

        # 미완료/완료 분리
        urgent_pending = [t for t in urgent_tasks if not t.get("done")]
        urgent_done = [t for t in urgent_tasks if t.get("done")]
        watch_pending = [t for t in watch_tasks if not t.get("done")]
        watch_done = [t for t in watch_tasks if t.get("done")]
        manual_pending = [t for t in manual_tasks if not t.get("done")]
        manual_done = [t for t in manual_tasks if t.get("done")]
        all_done = urgent_done + watch_done + manual_done
        _action_tasks = [t for t in today_tasks if t.get("action")]

        # ── ① 상단 KPI 요약 카드 4개 ──
        _urgent_pending_n = len(urgent_pending)
        _watch_pending_n = len(watch_pending)
        _done_n = len(all_done)
        _rate_pct = round((done_count / total_count * 100)) if total_count > 0 else 0
        _urgent_sub = f"미대응 {_urgent_pending_n}" if _urgent_pending_n else "모두 완료 ✓"
        _watch_sub = f"미대응 {_watch_pending_n}" if _watch_pending_n else "모두 완료 ✓"
        _done_types = {}
        for _dt in all_done:
            _a = _dt.get("action", {})
            _lbl = _a.get("label", "✅ 완료") if _a else "✅ 완료"
            _done_types[_lbl] = _done_types.get(_lbl, 0) + 1
        _done_sub = " / ".join(f"{v}건" for v in _done_types.values()) if _done_types else "-"

        st.markdown(f"""
        <div class="log-kpi-row">
            <div class="log-kpi urgent">
                <div class="kpi-icon">🔴</div>
                <div class="kpi-label">긴급 대응</div>
                <div class="kpi-value">{len(urgent_tasks)}건</div>
                <div class="kpi-sub">{_urgent_sub}</div>
            </div>
            <div class="log-kpi watch">
                <div class="kpi-icon">🟡</div>
                <div class="kpi-label">추가 확인</div>
                <div class="kpi-value">{len(watch_tasks)}건</div>
                <div class="kpi-sub">{_watch_sub}</div>
            </div>
            <div class="log-kpi done">
                <div class="kpi-icon">✅</div>
                <div class="kpi-label">완료</div>
                <div class="kpi-value">{_done_n}건</div>
                <div class="kpi-sub">{_done_sub}</div>
            </div>
            <div class="log-kpi rate">
                <div class="kpi-icon">📊</div>
                <div class="kpi-label">대응률</div>
                <div class="kpi-value">{_rate_pct}%</div>
                <div class="kpi-sub">{done_count}/{total_count}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── 프로그레스바 (슬림) ──
        pct_bar = min(pct, 100)
        st.markdown(f"""
        <div class="progress-container">
            <div class="progress-fill" style="width:{pct_bar}%;"></div>
        </div>
        """, unsafe_allow_html=True)

        # ── 송장 미출력 시 dim 처리 ──
        if not _today_shipped_log and not auto_tasks:
            st.markdown("""
            <div class="shipment-pending">
                <div class="sp-icon">📦</div>
                <div class="sp-title">오늘 송장이 아직 출력되지 않았습니다</div>
                <div class="sp-desc">송장 출력(출고 처리) 후 판매 대응 업무가 자동 생성됩니다</div>
            </div>
            """, unsafe_allow_html=True)

        # ── ④ 브랜드별 그룹핑 + 컴팩트 테이블 렌더링 ──
        _ACTION_OPTIONS = {
            "select": "— 액션 선택 —",
            "detail": "🔍 판매처 상세",
            "price": "💰 가격 확인",
            "page": "📝 상세페이지",
            "done": "✅ 대응 완료",
        }

        def _group_by_brand(task_list):
            """태스크를 브랜드별로 그룹핑."""
            groups = {}
            for t in task_list:
                meta = t.get("meta", {})
                pname = meta.get("product_name", t.get("title", ""))
                brand = extract_brand(pname)
                if brand not in groups:
                    groups[brand] = []
                groups[brand].append(t)
            # 건수 많은 브랜드순 정렬
            return dict(sorted(groups.items(), key=lambda x: -len(x[1])))

        def _render_brand_table(task_list, section_label, section_class, row_class, icon, default_expanded=True):
            """브랜드별 그룹핑된 2열 컴팩트 테이블 렌더링."""
            if not task_list:
                return
            st.markdown(f"""
            <div class="log-section {section_class}">
                <span>{icon} {section_label}</span>
                <span class="sec-count">{len(task_list)}건</span>
            </div>
            """, unsafe_allow_html=True)

            brand_groups = _group_by_brand(task_list)
            brand_list = list(brand_groups.items())

            # 2열 배치
            for row_idx in range(0, len(brand_list), 2):
                grid_cols = st.columns(2)
                for col_idx in range(2):
                    bi = row_idx + col_idx
                    if bi >= len(brand_list):
                        break
                    brand, tasks = brand_list[bi]
                    with grid_cols[col_idx]:
                        with st.expander(f"📦 {brand} ({len(tasks)}건)", expanded=default_expanded):
                            for task in tasks:
                                tid = task["id"]
                                meta = task.get("meta", {})
                                p_name = meta.get("product_name", task.get("title", ""))
                                p_id = meta.get("product_id", "")
                                avg_q = meta.get("avg_qty", 0)
                                active_d = meta.get("active_days", 0)
                                total_d = meta.get("total_days", 5)
                                is_carried = tid in carried_ids
                                carry_badge = '<span class="tr-badge bg-orange">⏰</span>' if is_carried else ""
                                # 브랜드명 제거한 짧은 상품명
                                short_name = p_name.replace(f"{brand}-", "").replace(f"{brand} ", "") if brand != p_name else p_name

                                # 상품 정보 + 액션 selectbox 한 줄
                                c_info, c_act = st.columns([6, 4])
                                with c_info:
                                    st.markdown(f"""
                                    <div class="task-row {row_class}" style="margin-bottom:0; padding:0.3rem 0.5rem;">
                                        <span class="tr-icon" style="font-size:0.82rem;">{icon}</span>
                                        <div class="tr-body">
                                            <div class="tr-name" style="font-size:0.8rem;">{short_name}{carry_badge}</div>
                                            <div class="tr-detail">일평균 {avg_q}개 · {active_d}/{total_d}일</div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                with c_act:
                                    sel_action = st.selectbox(
                                        "액션", options=list(_ACTION_OPTIONS.keys()),
                                        format_func=lambda x: _ACTION_OPTIONS[x],
                                        key=f"act_{tid}", label_visibility="collapsed",
                                    )
                                if sel_action != "select":
                                    if sel_action == "detail":
                                        st.session_state["_pending_shop_detail"] = {"pid": p_id, "pname": p_name, "avg_qty": avg_q}
                                        st.rerun()
                                    elif sel_action == "price":
                                        st.session_state.current_page = "price_monitor"
                                        st.session_state["_auto_price_keyword"] = p_name
                                        st.rerun()
                                    elif sel_action == "page":
                                        st.session_state["_pending_product_pages"] = {"pid": p_id, "pname": p_name, "avg_qty": avg_q}
                                        st.rerun()
                                    elif sel_action == "done":
                                        st.session_state["_pending_action_dialog"] = {"task_id": tid, "product_name": p_name}
                                        st.rerun()

        # ── ✅ 완료된 업무 (긴급대응 위) ──
        if all_done:
            with st.expander(f"✅ 완료된 업무 ({len(all_done)}건)", expanded=True):
                for task in sorted(all_done, key=lambda x: x.get("done_at", ""), reverse=True):
                    tid = task["id"]
                    meta = task.get("meta", {})
                    action = task.get("action")
                    p_name = meta.get("product_name", task.get("title", ""))
                    done_at = task.get("done_at", "")
                    level = meta.get("level", "")

                    # 원래 레벨 색상 유지
                    if level == "urgent":
                        _done_icon = "🔴"
                        _border_color = "#e53935"
                    elif level == "watch":
                        _done_icon = "🟡"
                        _border_color = "#f59e0b"
                    else:
                        _done_icon = "📋"
                        _border_color = "#1e88e5"

                    # 과정 로그 조립: 대응타입 → 개선내용 → 메모 → 시간
                    _done_time_short = done_at[-5:] if len(done_at) >= 5 else done_at
                    _process_parts = []
                    if action:
                        _act_label = action.get("label", "✅ 완료")
                        _process_parts.append(f'<span style="font-weight:600;">{_act_label}</span>')
                        if action.get("detail"):
                            _process_parts.append(f'<span style="color:#1565c0;">📋 {action["detail"]}</span>')
                        if action.get("memo"):
                            _process_parts.append(f'<span style="color:#777;">💬 {action["memo"]}</span>')
                        _act_time = action.get("time", _done_time_short)
                        _process_parts.append(f'<span style="color:#999;">⏱ {_act_time}</span>')
                    else:
                        # action 없이 완료된 태스크 — 기본 로그 표시
                        _process_parts.append(f'<span style="font-weight:600;">✅ 확인 완료</span>')
                        _process_parts.append(f'<span style="color:#999;">⏱ {_done_time_short}</span>')

                    _process_log = ' · '.join(_process_parts)

                    st.markdown(f"""
                    <div class="task-row done-row" style="border-left: 4px solid {_border_color};">
                        <span class="tr-icon">{_done_icon}</span>
                        <div class="tr-body">
                            <div class="tr-name" style="white-space:normal;">{p_name}</div>
                            <div class="tr-detail" style="font-size:0.8rem; white-space:normal; margin-top:3px;">{_process_log}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # ── 🔴 긴급 대응 (미완료 — 기본 펼침) ──
        _render_brand_table(urgent_pending, "긴급 대응", "urgent-sec", "urgent-row", "🔴", default_expanded=True)

        # ── 🟡 추가 확인 (미완료 — 기본 접힘) ──
        _render_brand_table(watch_pending, "추가 확인", "watch-sec", "watch-row", "🟡", default_expanded=False)

        # ── ⑤ 수동 업무 (간결한 체크리스트) ──
        if manual_tasks:
            st.markdown(f"""
            <div class="log-section">
                <span>📋 일반 업무</span>
                <span class="sec-count">{len(manual_tasks)}건</span>
            </div>
            """, unsafe_allow_html=True)

        for task in manual_pending:
            tid = task["id"]
            priority = task.get("priority", "normal")
            title = task.get("title", "")
            is_carried = tid in carried_ids
            pri_label = {"urgent": "긴급", "normal": "일반", "routine": "정기"}.get(priority, "일반")
            carry_html = ' <span class="tr-badge bg-orange">⏰ 이월</span>' if is_carried else ""

            col_chk, col_info = st.columns([0.4, 9.6])
            with col_chk:
                new_done = st.checkbox("완료", value=False, key=f"task_chk_{tid}", label_visibility="collapsed")
                if new_done:
                    toggle_task(tid, True)
                    st.rerun()
            with col_info:
                st.markdown(f"""
                <div class="manual-task">
                    <span class="mt-pri pri-{priority}">{pri_label}</span>
                    <span class="mt-title">{title}</span>{carry_html}
                </div>
                """, unsafe_allow_html=True)

        # ── ⑥ 새 업무 추가 폼 ──
        st.markdown("---")
        st.markdown("**\u2795 새 업무 추가**")
        with st.form("add_task_form", clear_on_submit=True):
            fc1, fc2, fc3, fc4 = st.columns([4, 2, 2, 2])
            with fc1:
                new_title = st.text_input("업무 제목", placeholder="업무 내용을 입력하세요...")
            with fc2:
                new_priority = st.selectbox("우선순위", ["normal", "urgent", "routine"], format_func=lambda x: {"urgent": "긴급", "normal": "일반", "routine": "정기"}[x])
            with fc3:
                new_type = st.selectbox("유형", ["daily", "weekly", "monthly"], format_func=lambda x: {"daily": "일일", "weekly": "주간", "monthly": "월간"}[x])
            with fc4:
                new_writer = st.selectbox("작성자", ["MD", "CS", "CEO", "기타"])
            add_submitted = st.form_submit_button("\U0001f4be 업무 추가", type="primary", use_container_width=True)
            if add_submitted and new_title.strip():
                add_task(new_title.strip(), task_type=new_type, priority=new_priority, due=today_str, writer=new_writer)
                st.success("업무가 추가되었습니다!")
                st.rerun()
            elif add_submitted:
                st.warning("업무 제목을 입력해주세요.")

    # ════════════════════════════════════════════
    # Tab: 대응 로그
    # ════════════════════════════════════════════
    with tab_log:
        _action_tasks = [t for t in today_tasks if t.get("action")]
        if _action_tasks:
            # 대응 로그 KPI
            _log_total = len(_action_tasks)
            _log_types = {}
            for _lt in _action_tasks:
                _la = _lt.get("action", {})
                _llbl = _la.get("label", "✅")
                _log_types[_llbl] = _log_types.get(_llbl, 0) + 1
            _log_type_summary = " · ".join(f"{k} {v}건" for k, v in _log_types.items())

            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#e8f5e9,#f1f8e9); border-radius:12px; padding:1rem 1.2rem; margin-bottom:1rem;">
                <div style="font-size:1.1rem; font-weight:700; color:#2e7d32;">📊 오늘 대응 로그</div>
                <div style="font-size:0.9rem; color:#558b2f; margin-top:0.3rem;">총 {_log_total}건 완료 — {_log_type_summary}</div>
            </div>
            """, unsafe_allow_html=True)

            _log_html = ""
            for t in sorted(_action_tasks, key=lambda x: x.get("done_at", ""), reverse=True):
                _a = t.get("action", {})
                _time = _a.get("time", t.get("done_at", "")[-5:])
                _type_lbl = _a.get("label", "✅")
                _pname = t.get("meta", {}).get("product_name", t.get("title", ""))
                _detail = _a.get("detail", "")
                _memo = _a.get("memo", "")
                _detail_html = f'<div style="font-size:0.82rem; color:#1565c0; margin-top:2px;">📋 {_detail}</div>' if _detail else ""
                _memo_html = f'<div style="font-size:0.78rem; color:#888; margin-top:1px;">💬 {_memo}</div>' if _memo else ""
                _log_html += f"""
                <div style="padding:0.6rem 0.8rem; border-bottom:1px solid #eee;">
                    <div style="display:flex; align-items:center; gap:0.5rem;">
                        <span style="font-size:0.78rem; color:#999; width:45px; flex-shrink:0;">{_time}</span>
                        <span style="font-size:0.88rem; font-weight:600; width:130px; flex-shrink:0;">{_type_lbl}</span>
                        <span style="font-size:0.88rem; flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{_pname}</span>
                    </div>
                    {_detail_html}
                    {_memo_html}
                </div>"""
            st.markdown(f'<div style="background:#fafafa; border-radius:10px; overflow:hidden;">{_log_html}</div>', unsafe_allow_html=True)
        else:
            st.info("아직 오늘 대응 완료된 업무가 없습니다. 업무를 처리하면 여기에 로그가 표시됩니다.")

    # ════════════════════════════════════════════
    # Tab 2: 주간/월간 계획
    # ════════════════════════════════════════════
    with tab2:
        sub_tab_w, sub_tab_m = st.tabs(["주간", "월간"])

        # ── 주간 뷰 ──
        with sub_tab_w:
            # 이번 주 월~일
            weekday_idx = now.weekday()  # 0=Mon
            mon = now - timedelta(days=weekday_idx)
            week_dates = [(mon + timedelta(days=i)) for i in range(7)]
            day_names = ["월", "화", "수", "목", "금", "토", "일"]

            cols = st.columns(7)
            for i, (d, dn) in enumerate(zip(week_dates, day_names)):
                d_str = d.strftime("%Y-%m-%d")
                d_tasks = [t for t in all_tasks if t.get("due") == d_str]
                d_done = sum(1 for t in d_tasks if t.get("done"))
                is_today = (d_str == today_str)
                header_style = "color:#1e88e5; font-weight:800;" if is_today else ""
                with cols[i]:
                    st.markdown(f"""
                    <div class="week-col">
                        <div class="week-col-header" style="{header_style}">
                            {dn} {d.day}일
                            <span style="font-size:0.68rem; opacity:0.5;">({d_done}/{len(d_tasks)})</span>
                        </div>
                    """, unsafe_allow_html=True)
                    if d_tasks:
                        items_html = ""
                        for t in d_tasks[:6]:
                            cls = "week-task-item done" if t.get("done") else "week-task-item"
                            items_html += f'<div class="{cls}">{t["title"][:12]}</div>'
                        if len(d_tasks) > 6:
                            items_html += f'<div style="font-size:0.7rem; opacity:0.5; text-align:center;">+{len(d_tasks)-6}건</div>'
                        st.markdown(items_html, unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="font-size:0.72rem; opacity:0.3; text-align:center; padding:8px;">-</div>', unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            # 주간 업무 추가
            st.markdown("---")
            st.markdown("**\u2795 주간 업무 추가**")
            with st.form("add_weekly_form", clear_on_submit=True):
                wc1, wc2, wc3, wc4 = st.columns([4, 2, 2, 2])
                with wc1:
                    w_title = st.text_input("업무 제목", placeholder="주간 업무 내용...", key="weekly_title")
                with wc2:
                    w_due = st.date_input("마감일", value=now, key="weekly_due")
                with wc3:
                    w_priority = st.selectbox("우선순위", ["normal", "urgent", "routine"], format_func=lambda x: {"urgent": "긴급", "normal": "일반", "routine": "정기"}[x], key="weekly_pri")
                with wc4:
                    w_writer = st.selectbox("작성자", ["MD", "CS", "CEO", "기타"], key="weekly_writer")
                w_sub = st.form_submit_button("\U0001f4be 주간 업무 추가", use_container_width=True)
                if w_sub and w_title.strip():
                    add_task(w_title.strip(), task_type="weekly", priority=w_priority, due=w_due.strftime("%Y-%m-%d"), writer=w_writer)
                    st.success("주간 업무가 추가되었습니다!")
                    st.rerun()

        # ── 월간 뷰 ──
        with sub_tab_m:
            cal_year = now.year
            cal_month = now.month
            st.markdown(f"### {cal_year}년 {cal_month}월")

            day_headers = ["월", "화", "수", "목", "금", "토", "일"]
            header_html = "".join(f'<div class="cal-header">{d}</div>' for d in day_headers)

            cal_obj = calendar.Calendar(firstweekday=0)
            month_days = cal_obj.monthdayscalendar(cal_year, cal_month)

            cells_html = ""
            for week in month_days:
                for day_num in week:
                    if day_num == 0:
                        cells_html += '<div class="cal-cell empty"></div>'
                    else:
                        d_str = f"{cal_year}-{cal_month:02d}-{day_num:02d}"
                        d_tasks = [t for t in all_tasks if t.get("due") == d_str]
                        count = len(d_tasks)
                        cls = "cal-cell"
                        if d_str == today_str:
                            cls += " today"
                        if count > 0:
                            cls += " has-tasks"
                        dot = f'<br><span class="task-dot"></span> <span style="font-size:0.65rem;">{count}</span>' if count > 0 else ""
                        cells_html += f'<div class="{cls}">{day_num}{dot}</div>'

            st.markdown(f'<div class="cal-grid">{header_html}{cells_html}</div>', unsafe_allow_html=True)

            # 날짜 선택 → 해당 날짜 업무 표시
            sel_day = st.number_input("날짜 선택 (일)", min_value=1, max_value=calendar.monthrange(cal_year, cal_month)[1], value=now.day, key="cal_day_sel")
            sel_date_str = f"{cal_year}-{cal_month:02d}-{int(sel_day):02d}"
            sel_tasks = [t for t in all_tasks if t.get("due") == sel_date_str]
            if sel_tasks:
                st.markdown(f"**{sel_date_str} 업무 ({len(sel_tasks)}건)**")
                for t in sel_tasks:
                    pr = t.get("priority", "normal")
                    pr_label = {"urgent": "긴급", "normal": "일반", "routine": "정기"}.get(pr, "일반")
                    done_mark = "\u2705" if t.get("done") else "\u2b1c"
                    st.markdown(f'{done_mark} `{pr_label}` {t["title"]}')
            else:
                st.caption(f"{sel_date_str} — 등록된 업무 없음")

            # 월간 업무 추가
            st.markdown("---")
            st.markdown("**\u2795 월간 업무 추가**")
            with st.form("add_monthly_form", clear_on_submit=True):
                mc1, mc2, mc3, mc4 = st.columns([4, 2, 2, 2])
                with mc1:
                    m_title = st.text_input("업무 제목", placeholder="월간 업무 내용...", key="monthly_title")
                with mc2:
                    m_due = st.date_input("마감일", value=now, key="monthly_due")
                with mc3:
                    m_priority = st.selectbox("우선순위", ["normal", "urgent", "routine"], format_func=lambda x: {"urgent": "긴급", "normal": "일반", "routine": "정기"}[x], key="monthly_pri")
                with mc4:
                    m_writer = st.selectbox("작성자", ["MD", "CS", "CEO", "기타"], key="monthly_writer")
                m_sub = st.form_submit_button("\U0001f4be 월간 업무 추가", use_container_width=True)
                if m_sub and m_title.strip():
                    add_task(m_title.strip(), task_type="monthly", priority=m_priority, due=m_due.strftime("%Y-%m-%d"), writer=m_writer)
                    st.success("월간 업무가 추가되었습니다!")
                    st.rerun()

    # ════════════════════════════════════════════
    # Tab 3: 공유 메모
    # ════════════════════════════════════════════
    with tab3:
        color_map = {
            "yellow": "#fff9c4",
            "blue": "#bbdefb",
            "pink": "#f8bbd0",
            "green": "#c8e6c9",
        }
        color_labels = {"yellow": "\U0001f7e1 노랑", "blue": "\U0001f535 파랑", "pink": "\U0001f7e3 분홍", "green": "\U0001f7e2 초록"}

        if all_notes:
            note_cols = st.columns(3)
            rotations = ["rot-1", "rot-2", "rot-3"]
            for ni, note in enumerate(reversed(all_notes)):
                bg = color_map.get(note.get("color", "yellow"), "#fff9c4")
                rot = rotations[ni % 3]
                writer_badge = note.get("writer", "")
                created = note.get("created", "")
                text = note.get("text", "").replace("\n", "<br>")

                with note_cols[ni % 3]:
                    st.markdown(f"""
                    <div class="sticky-note {rot}" style="background:{bg};">
                        <div>{text}</div>
                        <div class="note-meta">
                            <span><b>{writer_badge}</b> · {created}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("\U0001f5d1 삭제", key=f"del_note_{note['id']}"):
                        all_notes[:] = [n for n in all_notes if n["id"] != note["id"]]
                        save_notes()
                        st.rerun()
        else:
            st.info("등록된 공유 메모가 없습니다. 아래에서 새 메모를 추가하세요.")

        st.markdown("---")
        st.markdown("**\U0001f4dd 새 메모 추가**")
        with st.form("add_sticky_form", clear_on_submit=True):
            sc1, sc2, sc3 = st.columns([5, 2, 2])
            with sc1:
                s_text = st.text_area("메모 내용", height=80, placeholder="공유할 메모를 입력하세요...", key="sticky_text")
            with sc2:
                s_color = st.selectbox("색상", list(color_labels.keys()), format_func=lambda x: color_labels[x], key="sticky_color")
            with sc3:
                s_writer = st.selectbox("작성자", ["CEO", "MD", "CS", "기타"], key="sticky_writer")
            s_sub = st.form_submit_button("\U0001f4cc 메모 추가", type="primary", use_container_width=True)
            if s_sub and s_text.strip():
                new_note = {
                    "id": str(uuid.uuid4()),
                    "text": s_text.strip(),
                    "color": s_color,
                    "writer": s_writer,
                    "created": now.strftime("%Y-%m-%d %H:%M"),
                }
                all_notes.append(new_note)
                save_notes()
                st.success("메모가 추가되었습니다!")
                st.rerun()
            elif s_sub:
                st.warning("메모 내용을 입력해주세요.")


# ═════════════════════════════════════════════
# 🔍 상품 재발굴 (독립 페이지)
# ═════════════════════════════════════════════
elif current_page == "slow_moving":
    st.markdown('<h3 style="margin:0 0 0.3rem 0;">🔍 상품 재발굴</h3>', unsafe_allow_html=True)
    st.caption("장기 무출고 상품을 발굴하여 매출 기회를 만듭니다")

    _SLOW_TIER_META = {
        "remind":       {"icon": "🟡", "label": "리마인드",  "desc": "30~89일", "color": "#f59e0b", "bg": "linear-gradient(135deg,#fffbf0,#fff8e1)", "border": "#ffe082"},
        "review":       {"icon": "🟠", "label": "재점검",    "desc": "90~179일", "color": "#e65100", "bg": "linear-gradient(135deg,#fff3e0,#ffe0b2)", "border": "#ffcc80"},
        "rediscover":   {"icon": "🔴", "label": "재발굴",    "desc": "180~364일", "color": "#d32f2f", "bg": "linear-gradient(135deg,#fff5f5,#ffebee)", "border": "#ef9a9a"},
        "convert":      {"icon": "🔵", "label": "전환검토",  "desc": "365일+",   "color": "#1565c0", "bg": "linear-gradient(135deg,#e3f2fd,#bbdefb)", "border": "#90caf9"},
        "discontinued": {"icon": "⬛", "label": "단종",      "desc": "단종상품",  "color": "#616161", "bg": "linear-gradient(135deg,#f5f5f5,#e0e0e0)", "border": "#bdbdbd"},
    }

    with st.spinner("📦 상품 재발굴 데이터 분석 중... (최초 로딩 시 1~2분 소요)"):
        _slow_data = fetch_slow_moving_products()

    if _slow_data["status"] == "분석 완료":
        _tiers = _slow_data["tiers"]
        _total_products = _slow_data["total_products"]
        _total_slow = _slow_data["total_slow"]
        _active_count = _total_products - _total_slow

        # ── KPI 카드 (가로 컴팩트) ──
        _kpi_cards_html = ""
        for _tk, _tm in _SLOW_TIER_META.items():
            _cnt = len(_tiers.get(_tk, []))
            _kpi_cards_html += f"""
            <div style="flex:1; background:{_tm['bg']}; border:1px solid {_tm['border']}; border-radius:8px; padding:0.35rem 0.6rem; display:flex; align-items:center; gap:0.4rem;">
                <span style="font-size:0.9rem;">{_tm['icon']}</span>
                <span style="font-size:0.78rem; font-weight:600; color:#444;">{_tm['label']}</span>
                <span style="font-size:0.95rem; font-weight:800; color:{_tm['color']}; margin-left:auto;">{_cnt}건</span>
                <span style="font-size:0.65rem; color:#999;">{_tm['desc']}</span>
            </div>"""

        st.markdown(f'<div style="display:flex; gap:0.4rem; margin-bottom:0.5rem;">{_kpi_cards_html}</div>', unsafe_allow_html=True)

        # 요약 바
        _total_disc = _slow_data.get("total_discontinued", 0)
        _slow_pct = round(_total_slow / _total_products * 100) if _total_products > 0 else 0
        st.markdown(f"""
        <div style="background:#f8f9fa; border-radius:8px; padding:0.3rem 0.8rem; margin-bottom:0.6rem; font-size:0.75rem; color:#555; display:flex; justify-content:space-between;">
            <span>전체 <b>{_total_products:,}</b> SKU 중 부진 <b style="color:#d32f2f;">{_total_slow:,}</b>건({_slow_pct}%) · 단종 <b style="color:#616161;">{_total_disc:,}</b>건</span>
            <span>정상 판매: <b style="color:#2e7d32;">{_active_count:,}</b>건</span>
        </div>
        """, unsafe_allow_html=True)

        # ── 등급별 섹션 ──
        _SLOW_ACTION_OPTIONS = {
            "select": "— 액션 선택 —",
            "price": "💰 가격 확인",
            "page": "📝 상세페이지",
            "detail": "🔍 판매처 상세",
        }

        for tier_key, tier_meta in _SLOW_TIER_META.items():
            tier_items = _tiers.get(tier_key, [])
            if not tier_items:
                continue

            _expanded = tier_key == "remind"  # 리마인드만 기본 펼침, 단종은 항상 접힘

            st.markdown(f"""
            <div class="log-section" style="border-left:4px solid {tier_meta['color']};">
                <span>{tier_meta['icon']} {tier_meta['label']} — {tier_meta['desc']}</span>
                <span class="sec-count">{len(tier_items)}건</span>
            </div>
            """, unsafe_allow_html=True)

            # 브랜드별 그룹핑
            _slow_brand_groups = {}
            for item in tier_items:
                brand = extract_brand(item["product_name"])
                if brand not in _slow_brand_groups:
                    _slow_brand_groups[brand] = []
                _slow_brand_groups[brand].append(item)
            _slow_brand_groups = dict(sorted(_slow_brand_groups.items(), key=lambda x: -len(x[1])))
            _slow_brand_list = list(_slow_brand_groups.items())

            # 2열 브랜드 배치
            for _row_i in range(0, len(_slow_brand_list), 2):
                _grid = st.columns(2)
                for _col_i in range(2):
                    _bi = _row_i + _col_i
                    if _bi >= len(_slow_brand_list):
                        break
                    _brand, _items = _slow_brand_list[_bi]
                    with _grid[_col_i]:
                        with st.expander(f"📦 {_brand} ({len(_items)}건)", expanded=_expanded):
                            for _si in _items:
                                _sid = _si["product_id"]
                                _sname = _si["product_name"]
                                _sdays = _si["days_since"]
                                _sstock = _si["stock_qty"]
                                _slast = _si.get("last_sale") or "기록없음"
                                _short_name = _sname.replace(f"{_brand}-", "").replace(f"{_brand} ", "") if _brand != _sname else _sname

                                # 무출고 기간에 따른 배지 색상
                                if _sdays >= 365:
                                    _day_badge_color = "#1565c0"
                                elif _sdays >= 180:
                                    _day_badge_color = "#d32f2f"
                                elif _sdays >= 90:
                                    _day_badge_color = "#e65100"
                                else:
                                    _day_badge_color = "#f59e0b"

                                _stock_color = "#d32f2f" if _sstock <= 5 else "#666"

                                # 상품 정보 + 액션 한 줄
                                _c_info, _c_act = st.columns([6, 4])
                                with _c_info:
                                    st.markdown(f"""
                                    <div style="padding:0.25rem 0.4rem; border-bottom:1px solid #f0f0f0;">
                                        <div style="font-size:0.78rem; font-weight:600; color:#333; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{tier_meta['icon']} {_short_name}</div>
                                        <div style="font-size:0.68rem; color:#888; margin-top:1px;">
                                            <span style="color:{_day_badge_color}; font-weight:600;">{_sdays}일</span> 무출고
                                            · 재고 <span style="color:{_stock_color}; font-weight:600;">{_sstock}개</span>
                                            · 최종 {_slast}
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                with _c_act:
                                    _slow_sel = st.selectbox(
                                        "액션", options=list(_SLOW_ACTION_OPTIONS.keys()),
                                        format_func=lambda x: _SLOW_ACTION_OPTIONS[x],
                                        key=f"slow_{tier_key}_{_sid}",
                                        label_visibility="collapsed",
                                    )
                                if _slow_sel != "select":
                                    if _slow_sel == "price":
                                        st.session_state.current_page = "price_monitor"
                                        st.session_state["_auto_price_keyword"] = _sname
                                        st.rerun()
                                    elif _slow_sel == "page":
                                        st.session_state["_pending_product_pages"] = {"pid": _sid, "pname": _sname, "avg_qty": 0}
                                        st.rerun()
                                    elif _slow_sel == "detail":
                                        st.session_state["_pending_shop_detail"] = {"pid": _sid, "pname": _sname, "avg_qty": 0}
                                        st.rerun()

    elif _slow_data["status"] == "미연동":
        st.info("📡 OneWMS API가 연동되지 않았습니다. API 연동 후 상품 재발굴 분석이 가능합니다.")
    else:
        st.warning(f"데이터 로딩 중 문제가 발생했습니다: {_slow_data['status']}")


# ─────────────────────────────────────────────
# 푸터 (모든 페이지 공통)
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
    신아인터네셔날(ShinA) 업무 대시보드 v2.0 · {datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')}
</div>
""", unsafe_allow_html=True)
