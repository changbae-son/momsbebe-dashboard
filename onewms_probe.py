"""
OneWMS 응답에 송장번호가 들어 있는지 확인하는 점검 스크립트.

쿠팡 로켓배송 앱(coupang-rocket-2026)에 송장번호를 자동으로 채워 넣으려면
OneWMS get_order_info 응답에 송장번호 필드가 있는지 먼저 확인해야 한다.
이 스크립트는 응답의 "필드 이름"과 샘플 값을 보여줄 뿐 아무것도 저장하지 않는다.

실행 방법
---------
  python onewms_probe.py                    # 최근 7일
  python onewms_probe.py 2026-07-15 2026-07-18

API 키는 아래 순서로 찾는다.
  1) .streamlit/secrets.toml 의 [onewms] 섹션
  2) 환경변수 ONEWMS_PARTNER_KEY / ONEWMS_DOMAIN_KEY / ONEWMS_API_URL
  3) 실행 중 직접 입력
"""
import os
import sys
import json
from datetime import datetime, timedelta

import requests

try:
    import tomllib                      # Python 3.11+
except ModuleNotFoundError:
    tomllib = None

SECRETS = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")

# 송장번호일 가능성이 있는 필드 이름들 (부분 일치로 찾는다)
INVOICE_HINTS = [
    "invoice", "waybill", "tracking", "delivery_no", "deliv_no",
    "song", "송장", "운송장", "delivery_num", "bill_no", "wbl",
]
# 택배사일 가능성이 있는 필드
COURIER_HINTS = ["courier", "delivery_com", "deliv_com", "parcel", "택배", "company"]


def load_keys() -> dict:
    if tomllib and os.path.exists(SECRETS):
        with open(SECRETS, "rb") as f:
            cfg = tomllib.load(f).get("onewms", {})
        if cfg.get("partner_key"):
            print(f"[키] {SECRETS} 에서 읽음")
            return cfg

    env = {
        "partner_key": os.getenv("ONEWMS_PARTNER_KEY", ""),
        "domain_key": os.getenv("ONEWMS_DOMAIN_KEY", ""),
        "api_url": os.getenv("ONEWMS_API_URL", ""),
    }
    if env["partner_key"]:
        print("[키] 환경변수에서 읽음")
        return env

    print("[키] 직접 입력 (화면에만 쓰이고 저장되지 않습니다)")
    return {
        "partner_key": input("  partner_key: ").strip(),
        "domain_key": input("  domain_key : ").strip(),
        "api_url": input("  api_url    : ").strip(),
    }


def call(keys: dict, action: str, params: dict) -> dict:
    """OneWMS 공식 안내는 POST. 혹시 몰라 실패하면 GET으로도 시도한다."""
    payload = {
        "partner_key": keys["partner_key"],
        "domain_key": keys["domain_key"],
        "action": action,
        "type": "product",
    }
    payload.update(params)

    resp = requests.post(keys["api_url"], data=payload, timeout=20)
    resp.raise_for_status()
    try:
        return resp.json()
    except ValueError:
        pass
    resp = requests.get(keys["api_url"], params=payload, timeout=20)
    resp.raise_for_status()
    return resp.json()


def walk_fields(obj, prefix="", out=None):
    """중첩 구조까지 모든 필드 경로를 모은다."""
    if out is None:
        out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else k
            if isinstance(v, (dict, list)):
                walk_fields(v, path, out)
            else:
                out.setdefault(path, v)
    elif isinstance(obj, list) and obj:
        walk_fields(obj[0], f"{prefix}[]", out)
    return out


def main():
    if len(sys.argv) >= 3:
        start, end = sys.argv[1], sys.argv[2]
    else:
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    keys = load_keys()
    if not all(keys.get(k) for k in ("partner_key", "domain_key", "api_url")):
        print("키가 모자랍니다. 중단합니다.")
        return

    print(f"\n[조회] get_order_info  {start} ~ {end}")
    data = call(keys, "get_order_info", {
        "start_date": start, "end_date": end,
        "date_type": "order_date", "limit": "5", "page": "1",
    })

    if not isinstance(data, dict):
        print("예상과 다른 응답:", str(data)[:500]); return
    if data.get("error") not in (0, None, "0"):
        print("API 오류:", json.dumps(data, ensure_ascii=False)[:500]); return

    orders = data.get("data") or data.get("list") or []
    print(f"[결과] 주문 {len(orders)}건 (total={data.get('total')})")
    if not orders:
        print("이 기간에 주문이 없습니다. 발송이 있었던 날짜로 다시 실행해 보세요.")
        return

    fields = walk_fields(orders[0])
    print(f"\n=== 주문 1건의 전체 필드 ({len(fields)}개) ===")
    for path, val in fields.items():
        s = str(val)
        print(f"  {path:<38} = {s[:60]}")

    def hits(hints):
        return [p for p in fields if any(h in p.lower() for h in hints)]

    inv, cou = hits(INVOICE_HINTS), hits(COURIER_HINTS)
    print("\n=== 판정 ===")
    if inv:
        print("✅ 송장번호로 보이는 필드:")
        for p in inv:
            print(f"     {p} = {fields[p]}")
    else:
        print("❌ 송장번호 필드를 못 찾았습니다.")
        print("   → 발송 완료된 주문이 포함된 날짜로 다시 실행해 보세요.")
        print("   → 그래도 없으면 get_order_info에는 송장이 없다는 뜻입니다.")
    if cou:
        print("📦 택배사로 보이는 필드:", ", ".join(f"{p}={fields[p]}" for p in cou))

    print("\n※ 이 출력에는 API 키가 포함되지 않습니다. 그대로 복사해 공유해도 됩니다.")


if __name__ == "__main__":
    main()
