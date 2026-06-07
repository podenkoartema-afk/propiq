"""
DLD Data Loader — Dubai Land Department Open Data
--------------------------------------------------
Reads CSV files downloaded from dubailand.gov.ae/en/open-data/real-estate-data/
and computes per-district benchmarks for the Deal Score algorithm.

How to update data:
1. Go to https://dubailand.gov.ae/en/open-data/real-estate-data/
2. Select: Transactions → Sales → last 6–12 months → Download CSV
3. (Optional) Select: Rents → last 6–12 months → Download CSV
4. Place files in the data/ folder as:
   - data/dld_transactions.csv
   - data/dld_rents.csv  (optional)
5. Restart the app — benchmarks update automatically.
"""

import os
import csv
from datetime import datetime, timedelta
from statistics import median

# ── Paths ──────────────────────────────────────────────────────────────────────
DATA_DIR          = os.path.join(os.path.dirname(__file__), "data")
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "dld_transactions.csv")
RENTS_FILE        = os.path.join(DATA_DIR, "dld_rents.csv")

# ── Fallback hardcoded benchmarks (used when no CSV is present) ────────────────
# Based on Dubai market estimates for 2026
FALLBACK_BENCHMARKS = {
    "Dubai Marina":    2200,
    "Downtown Dubai":  2900,
    "Business Bay":    2000,
    "Palm Jumeirah":   4200,
    "JVC":             1200,
    "JBR":             2500,
    "DIFC":            2700,
    "Arabian Ranches": 1600,
    "Creek Harbour":   2300,
    "MBR City":        2000,
}

FALLBACK_RENTS = {
    "Dubai Marina":    130000,
    "Downtown Dubai":  185000,
    "Business Bay":    120000,
    "Palm Jumeirah":   260000,
    "JVC":             75000,
    "JBR":             155000,
    "DIFC":            170000,
    "Arabian Ranches": 155000,
    "Creek Harbour":   130000,
    "MBR City":        125000,
}

# ── District name mapping (DLD names → our app names) ─────────────────────────
DISTRICT_MAP = {
    "DUBAI MARINA":              "Dubai Marina",
    "MARSA DUBAI":               "Dubai Marina",
    "DOWNTOWN DUBAI":            "Downtown Dubai",
    "BURJ KHALIFA":              "Downtown Dubai",
    "BUSINESS BAY":              "Business Bay",
    "PALM JUMEIRAH":             "Palm Jumeirah",
    "JUMEIRAH VILLAGE CIRCLE":   "JVC",
    "JVC":                       "JVC",
    "JUMEIRAH BEACH RESIDENCE":  "JBR",
    "JBR":                       "JBR",
    "DIFC":                      "DIFC",
    "DUBAI INTERNATIONAL FINANCIAL CENTRE": "DIFC",
    "ARABIAN RANCHES":           "Arabian Ranches",
    "ARABIAN RANCHES 2":         "Arabian Ranches",
    "ARABIAN RANCHES 3":         "Arabian Ranches",
    "DUBAI CREEK HARBOUR":       "Creek Harbour",
    "CREEK HARBOUR":             "Creek Harbour",
    "MOHAMMED BIN RASHID CITY":  "MBR City",
    "MBR CITY":                  "MBR City",
    "MEYDAN":                    "MBR City",
}


def _normalize_district(raw: str) -> str | None:
    """Map raw DLD district name to our app district name."""
    upper = raw.strip().upper()
    for key, value in DISTRICT_MAP.items():
        if key in upper or upper in key:
            return value
    return None


def _parse_date(date_str: str) -> datetime | None:
    """Try common DLD date formats."""
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None


def load_transaction_benchmarks(days: int = 180) -> dict:
    """
    Returns dict: {district: median_price_per_sqft}
    Falls back to FALLBACK_BENCHMARKS if file missing or unreadable.
    """
    if not os.path.exists(TRANSACTIONS_FILE):
        return FALLBACK_BENCHMARKS.copy()

    cutoff = datetime.now() - timedelta(days=days)
    district_prices: dict[str, list[float]] = {}

    try:
        with open(TRANSACTIONS_FILE, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = [h.lower().strip() for h in (reader.fieldnames or [])]

            # Auto-detect column names
            date_col  = _find_col(headers, ["transaction_date", "date", "trans_date", "instance_date"])
            price_col = _find_col(headers, ["price", "amount", "trans_value", "procedure_value"])
            area_col  = _find_col(headers, ["procedure_area", "area_sqft", "area", "property_size"])
            dist_col  = _find_col(headers, ["area_en", "area", "district", "location", "property_area"])
            type_col  = _find_col(headers, ["trans_group", "transaction_type", "type", "procedure_name"])

            for row in reader:
                try:
                    # Only sales (skip mortgages, gifts)
                    if type_col:
                        t = row.get(type_col, "").upper()
                        if t and "SALE" not in t and "SELL" not in t and "BUY" not in t:
                            continue

                    # Date filter
                    if date_col:
                        dt = _parse_date(row.get(date_col, ""))
                        if dt and dt < cutoff:
                            continue

                    # District
                    raw_dist = row.get(dist_col, "") if dist_col else ""
                    district = _normalize_district(raw_dist)
                    if not district:
                        continue

                    # Price per sqft
                    price = float(str(row.get(price_col, "0")).replace(",", "") or 0)
                    area  = float(str(row.get(area_col,  "0")).replace(",", "") or 0)
                    if price <= 0 or area <= 0:
                        continue
                    ppsf = price / area
                    if ppsf < 200 or ppsf > 20000:   # sanity filter
                        continue

                    district_prices.setdefault(district, []).append(ppsf)

                except (ValueError, TypeError):
                    continue

    except Exception:
        return FALLBACK_BENCHMARKS.copy()

    # Build result — use median, fall back to hardcoded where no data
    result = FALLBACK_BENCHMARKS.copy()
    for district, prices in district_prices.items():
        if len(prices) >= 5:                         # need at least 5 data points
            result[district] = round(median(prices))

    return result


def load_rent_benchmarks(days: int = 180) -> dict:
    """
    Returns dict: {district: median_annual_rent_aed}
    Falls back to FALLBACK_RENTS if file missing or unreadable.
    """
    if not os.path.exists(RENTS_FILE):
        return FALLBACK_RENTS.copy()

    cutoff = datetime.now() - timedelta(days=days)
    district_rents: dict[str, list[float]] = {}

    try:
        with open(RENTS_FILE, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = [h.lower().strip() for h in (reader.fieldnames or [])]

            date_col   = _find_col(headers, ["contract_date", "start_date", "date", "registration_date"])
            amount_col = _find_col(headers, ["annual_amount", "rent_amount", "amount", "yearly_rent"])
            dist_col   = _find_col(headers, ["area_en", "area", "district", "location"])

            for row in reader:
                try:
                    if date_col:
                        dt = _parse_date(row.get(date_col, ""))
                        if dt and dt < cutoff:
                            continue

                    raw_dist = row.get(dist_col, "") if dist_col else ""
                    district = _normalize_district(raw_dist)
                    if not district:
                        continue

                    amount = float(str(row.get(amount_col, "0")).replace(",", "") or 0)
                    if amount < 10000 or amount > 5000000:
                        continue

                    district_rents.setdefault(district, []).append(amount)

                except (ValueError, TypeError):
                    continue

    except Exception:
        return FALLBACK_RENTS.copy()

    result = FALLBACK_RENTS.copy()
    for district, rents in district_rents.items():
        if len(rents) >= 5:
            result[district] = round(median(rents))

    return result


def load_transaction_counts(days: int = 90) -> dict:
    """
    Returns dict: {district: transaction_count_last_N_days}
    Used for liquidity score.
    """
    if not os.path.exists(TRANSACTIONS_FILE):
        return {}

    cutoff = datetime.now() - timedelta(days=days)
    counts: dict[str, int] = {}

    try:
        with open(TRANSACTIONS_FILE, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = [h.lower().strip() for h in (reader.fieldnames or [])]

            date_col = _find_col(headers, ["transaction_date", "date", "trans_date", "instance_date"])
            dist_col = _find_col(headers, ["area_en", "area", "district", "location"])
            type_col = _find_col(headers, ["trans_group", "transaction_type", "type"])

            for row in reader:
                try:
                    if type_col:
                        t = row.get(type_col, "").upper()
                        if t and "SALE" not in t:
                            continue
                    if date_col:
                        dt = _parse_date(row.get(date_col, ""))
                        if not dt or dt < cutoff:
                            continue
                    raw_dist = row.get(dist_col, "") if dist_col else ""
                    district = _normalize_district(raw_dist)
                    if district:
                        counts[district] = counts.get(district, 0) + 1
                except (ValueError, TypeError):
                    continue

    except Exception:
        return {}

    return counts


def get_data_status() -> dict:
    """Returns info about loaded data for display in the UI."""
    tx_exists   = os.path.exists(TRANSACTIONS_FILE)
    rent_exists = os.path.exists(RENTS_FILE)

    tx_rows   = _count_rows(TRANSACTIONS_FILE) if tx_exists else 0
    rent_rows = _count_rows(RENTS_FILE)        if rent_exists else 0
    tx_date   = _file_date(TRANSACTIONS_FILE)  if tx_exists else None
    rent_date = _file_date(RENTS_FILE)         if rent_exists else None

    return {
        "transactions_loaded": tx_exists,
        "rents_loaded":        rent_exists,
        "tx_rows":             tx_rows,
        "rent_rows":           rent_rows,
        "tx_updated":          tx_date,
        "rent_updated":        rent_date,
        "is_live":             tx_exists or rent_exists,
    }


def _find_col(headers: list[str], candidates: list[str]) -> str | None:
    for c in candidates:
        if c in headers:
            return c
    return None


def _count_rows(filepath: str) -> int:
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            return sum(1 for _ in f) - 1   # minus header
    except Exception:
        return 0


def _file_date(filepath: str) -> str:
    try:
        ts = os.path.getmtime(filepath)
        return datetime.fromtimestamp(ts).strftime("%d %b %Y")
    except Exception:
        return "unknown"
