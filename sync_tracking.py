"""
OneWMS 송장번호 → 쿠팡 로켓배송 앱(Firestore) 자동 기입.

  python sync_tracking.py 2026-07-20            # 미리보기만 (기록 안 함)
  python sync_tracking.py 2026-07-20 --write    # 실제로 기록

동작 원리
---------
OneWMS는 박스 하나를 주문 여러 건으로 나눠 담고, **같은 박스에 든 주문들은
같은 송장번호(trans_no)를 공유**한다. 우리 앱의 박스도 발주번호 묶음이므로
발주번호(order_id) 기준으로 양쪽을 맞추면 박스↔송장이 1:1로 대응된다.

  · 한 발주가 여러 박스로 나뉜 경우(예: 분유 120 → 60+60)는
    OneWMS에도 주문이 여러 건 생기므로 수량으로 짝지어 배정한다.
  · 앱의 박스 구성과 OneWMS 실제 구성이 다르면 배정하지 않고 경고만 낸다
    (잘못 기입하면 쉽먼트가 틀어지므로 안전 우선).

API 키
------
  1) .streamlit/secrets.toml 의 [onewms]
  2) 환경변수 ONEWMS_PARTNER_KEY / ONEWMS_DOMAIN_KEY / ONEWMS_API_URL
  3) 실행 중 직접 입력
"""
import os
import sys
import json
from collections import defaultdict

import requests

try:
    import tomllib
except ModuleNotFoundError:
    tomllib = None

SECRETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".streamlit", "secrets.toml")

COUPANG_ROCKET_SHOP_ID = "10084"        # 쿠팡로켓배송(송장)
FS_PROJECT = "coupang-rocket-2026"
FS_KEY = "AIzaSyAzmT1tk0LmTUOGFWMY7Fop85UZ2DI8Jw8"   # 웹 공개키 (Firestore 규칙이 공개라 별도 인증 불필요)
FS_BASE = f"https://firestore.googleapis.com/v1/projects/{FS_PROJECT}/databases/(default)/documents"


# ── OneWMS ────────────────────────────────────────────────
def load_keys() -> dict:
    if tomllib and os.path.exists(SECRETS):
        with open(SECRETS, "rb") as f:
            cfg = tomllib.load(f).get("onewms", {})
        if cfg.get("partner_key"):
            return cfg
    env = {
        "partner_key": os.getenv("ONEWMS_PARTNER_KEY", ""),
        "domain_key": os.getenv("ONEWMS_DOMAIN_KEY", ""),
        "api_url": os.getenv("ONEWMS_API_URL", "https://api.onewms.co.kr/api.php"),
    }
    if env["partner_key"]:
        return env
    return {
        "partner_key": input("partner_key: ").strip(),
        "domain_key": input("domain_key : ").strip(),
        "api_url": input("api_url    : ").strip() or "https://api.onewms.co.kr/api.php",
    }


def fetch_onewms_orders(keys: dict, date: str) -> list:
    """입고예정일(order_date)이 date인 쿠팡 로켓배송 주문 전체."""
    out, page = [], 1
    while page <= 20:
        payload = {
            "partner_key": keys["partner_key"], "domain_key": keys["domain_key"],
            "action": "get_order_info", "type": "product",
            "start_date": date, "end_date": date, "date_type": "order_date",
            "limit": "100", "page": str(page),
        }
        r = requests.post(keys["api_url"], data=payload, timeout=30)
        r.raise_for_status()
        d = r.json()
        if d.get("error") not in (0, None, "0"):
            raise SystemExit(f"OneWMS 오류: {d.get('msg')}")
        batch = d.get("data") or []
        if not batch:
            break
        out.extend(batch)
        if page * 100 >= int(d.get("total", 0)):
            break
        page += 1
    return [o for o in out if str(o.get("shop_id")) == COUPANG_ROCKET_SHOP_ID]


# ── Firestore REST ────────────────────────────────────────
def fs_get(path: str) -> dict:
    r = requests.get(f"{FS_BASE}/{path}", params={"key": FS_KEY, "pageSize": 300}, timeout=20)
    r.raise_for_status()
    return r.json()


def fs_val(v):
    """Firestore REST 값 → 파이썬 값"""
    if "stringValue" in v: return v["stringValue"]
    if "integerValue" in v: return int(v["integerValue"])
    if "doubleValue" in v: return float(v["doubleValue"])
    if "booleanValue" in v: return v["booleanValue"]
    if "nullValue" in v: return None
    if "arrayValue" in v: return [fs_val(x) for x in v["arrayValue"].get("values", [])]
    if "mapValue" in v: return {k: fs_val(x) for k, x in v["mapValue"].get("fields", {}).items()}
    return None


def fs_doc(doc: dict) -> dict:
    return {k: fs_val(v) for k, v in (doc.get("fields") or {}).items()}


def fs_write_tracking(center: str, date: str, tracking: dict, tracking_sig: dict):
    """송장번호와 함께 '그때의 박스 내용 지문'도 남긴다.
       나중에 박스 구성이 바뀌면 앱이 이 지문으로 알아채고 재동기화를 요구한다."""
    body = {"fields": {
        "tracking": {"mapValue": {"fields": {
            str(k): {"stringValue": str(v)} for k, v in tracking.items()}}},
        "trackingSig": {"mapValue": {"fields": {
            str(k): {"stringValue": str(v)} for k, v in tracking_sig.items()}}},
    }}
    r = requests.patch(
        f"{FS_BASE}/batches/{date}/plans/{center}",
        params=[("key", FS_KEY), ("updateMask.fieldPaths", "tracking"),
                ("updateMask.fieldPaths", "trackingSig")],
        json=body, timeout=20)
    r.raise_for_status()


# ── 매칭 ──────────────────────────────────────────────────
def sig(items):
    """박스 내용 지문: (발주번호, 수량) 다중집합"""
    return tuple(sorted((str(p), int(q)) for p, q in items))


def box_sig(items) -> str:
    """앱(app.js boxSig)과 동일한 문자열 지문 — 나중에 박스가 바뀌면 앱이 알아챈다."""
    return "|".join(sorted(f"{p}:{q}" for p, q in items))


def match_boxes(app_boxes: dict, wms_boxes: list) -> tuple:
    """
    app_boxes : {박스번호: [(poNo, qty), ...]}
    wms_boxes : [{"trans_no":..., "items":[(order_id, qty), ...]}]
    반환: ({박스번호: trans_no}, [경고문])
    """
    result, warns = {}, []
    remaining = list(wms_boxes)

    # 1단계 — 내용이 완전히 같은 것끼리 (수량까지 일치)
    for box, items in sorted(app_boxes.items()):
        s = sig(items)
        hit = next((w for w in remaining if sig(w["items"]) == s), None)
        if hit:
            result[box] = hit["trans_no"]
            remaining.remove(hit)

    # 2단계 — 남은 박스는 발주번호 구성만으로 (수량이 조금 달라도)
    for box, items in sorted(app_boxes.items()):
        if box in result:
            continue
        pos = {str(p) for p, _ in items}
        hit = next((w for w in remaining if {str(p) for p, _ in w["items"]} == pos), None)
        if hit:
            result[box] = hit["trans_no"]
            remaining.remove(hit)
            warns.append(f"박스 {box}: 발주 구성은 같은데 수량이 다릅니다 "
                         f"(앱 {sum(q for _,q in items)}개 / OneWMS {sum(q for _,q in hit['items'])}개)")

    for box in sorted(app_boxes):
        if box not in result:
            pos = ", ".join(sorted({str(p) for p, _ in app_boxes[box]}))
            warns.append(f"박스 {box}: OneWMS에서 짝을 못 찾음 (발주 {pos}) — 아직 발송 전이거나 박스 구성이 다릅니다")
    for w in remaining:
        pos = ", ".join(sorted({str(p) for p, _ in w["items"]}))
        warns.append(f"OneWMS 송장 {w['trans_no']}: 앱에 대응 박스 없음 (발주 {pos})")
    return result, warns


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    write = "--write" in sys.argv
    if not args:
        print(__doc__); return
    date = args[0]

    print(f"■ 입고예정일 {date}   ({'실제 기록' if write else '미리보기 — 기록하지 않음'})\n")

    keys = load_keys()
    orders = fetch_onewms_orders(keys, date)
    print(f"[OneWMS] 쿠팡 로켓배송 주문 {len(orders)}건")

    # 발주번호 → OneWMS 주문들
    by_po = defaultdict(list)
    for o in orders:
        by_po[str(o.get("order_id"))].append(o)
    # 송장번호 → 실제 박스
    wms_by_trans = defaultdict(list)
    for o in orders:
        if o.get("trans_no"):
            wms_by_trans[str(o["trans_no"])].append(o)
    print(f"[OneWMS] 송장 {len(wms_by_trans)}개 = 실제 박스 {len(wms_by_trans)}개\n")

    # 앱 데이터
    pos_docs = fs_get(f"batches/{date}/pos").get("documents", [])
    plans_docs = fs_get(f"batches/{date}/plans").get("documents", [])
    if not pos_docs:
        print(f"앱에 {date} 발주서가 없습니다."); return

    po_center = {}
    for d in pos_docs:
        p = fs_doc(d)
        po_center[str(p.get("poNo"))] = p.get("moveTo") or p.get("center")

    total_set = 0
    for d in plans_docs:
        center = d["name"].split("/")[-1]
        plan = fs_doc(d)
        allocs = plan.get("allocs") or []
        if not allocs:
            continue

        app_boxes = defaultdict(list)
        for a in allocs:
            app_boxes[int(a["box"])].append((str(a["poNo"]), int(a["qty"])))

        # 이 센터 박스에 등장하는 발주들이 속한 OneWMS 박스만 후보로
        my_pos = {p for items in app_boxes.values() for p, _ in items}
        cands = []
        for tno, os_ in wms_by_trans.items():
            if any(str(o.get("order_id")) in my_pos for o in os_):
                cands.append({"trans_no": tno,
                              "items": [(str(o.get("order_id")), int(o.get("qty") or 0)) for o in os_]})

        matched, warns = match_boxes(dict(app_boxes), cands)

        print(f"── {center} ──  앱 {len(app_boxes)}박스 / 후보 송장 {len(cands)}개")
        for box in sorted(app_boxes):
            items = app_boxes[box]
            desc = ", ".join(f"{p}({q})" for p, q in sorted(items))
            tno = matched.get(box)
            mark = "✅" if tno else "⚠️ "
            print(f"   {mark} 박스 {box}  {sum(q for _,q in items):>4}개  {desc[:58]:<58} → {tno or '-'}")
        for w in warns:
            print(f"      · {w}")

        if write and matched:
            # 지금 있는 박스만 남긴다. 짝을 못 찾은 박스의 옛 송장은 지운다
            # (그대로 두면 어긋난 번호가 계속 보인다). 수동 입력분은 내용이
            # 그대로면 보존한다.
            old_tr = plan.get("tracking") or {}
            old_sg = plan.get("trackingSig") or {}
            merged, merged_sig = {}, {}
            for b in app_boxes:
                cur = box_sig(app_boxes[b])
                if b in matched:
                    merged[str(b)], merged_sig[str(b)] = matched[b], cur
                elif old_tr.get(str(b)) and old_sg.get(str(b)) == cur:
                    merged[str(b)], merged_sig[str(b)] = old_tr[str(b)], cur
            fs_write_tracking(center, date, merged, merged_sig)
            total_set += len(merged)
            print(f"      💾 {len(matched)}개 송장 기록 완료")
        print()

    if write:
        print(f"■ 총 {total_set}개 박스에 송장번호를 기록했습니다.")
    else:
        print("■ 미리보기입니다. 맞으면 뒤에 --write 를 붙여 다시 실행하세요.")


if __name__ == "__main__":
    main()
