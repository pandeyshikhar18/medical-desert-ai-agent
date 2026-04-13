from __future__ import annotations

import re
from typing import List, Tuple, Optional
import pandas as pd

from models import ExtractedFacility, Evidence


# =========================
# KEYWORDS
# =========================
PROCEDURE_KEYWORDS = {
    "surgery": ["surgery", "operation"],
    "dialysis": ["dialysis"],
    "delivery": ["delivery", "c-section"],
}

EQUIPMENT_KEYWORDS = {
    "icu": ["icu"],
    "ventilator": ["ventilator"],
    "oxygen": ["oxygen"],
    "xray": ["x-ray", "xray"],
    "ct": ["ct scan"],
}

CAPABILITY_KEYWORDS = {
    "emergency": ["emergency"],
    "24/7": ["24/7"],
    "inpatient": ["inpatient"],
    "outpatient": ["outpatient"],
}

SUSPICIOUS_PHRASES = [
    "world class",
    "state of the art",
    "fully equipped"
]


# =========================
# HELPERS
# =========================
def _norm(text: str) -> str:
    return str(text).lower().strip()


def _safe_int(val) -> Optional[int]:
    try:
        return int(val)
    except:
        return None


def _safe_float(val) -> Optional[float]:
    try:
        return float(val)
    except:
        return None


def _pick_first(row, keys: List[str]) -> Optional[str]:
    for k in keys:
        if k in row and pd.notna(row[k]):
            return row[k]
    return None


def _city_region_country(row) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    return (
        _pick_first(row, ["city"]),
        _pick_first(row, ["state"]),
        _pick_first(row, ["country"]),
        _pick_first(row, ["country_code"]),
    )


def _build_blob(row) -> Tuple[str, List[str]]:
    text = []
    cols = list(row.index)

    for col in cols:
        val = row[col]
        if pd.notna(val):
            text.append(str(val))

    return " ".join(text), cols


def _extract_from_sentences(text: str, keyword_map):
    results = []
    for label, keywords in keyword_map.items():
        for kw in keywords:
            if kw in text:
                results.append(label)
                break
    return list(set(results))


# =========================
# MAIN FUNCTION
# =========================
def extract_row(row: pd.Series, row_index: int) -> ExtractedFacility:
    blob, used_cols = _build_blob(row)
    lowered = _norm(blob)

    name = _pick_first(row, ["name", "facility_name"]) or f"Row {row_index}"

    # Extraction
    procedures = _extract_from_sentences(lowered, PROCEDURE_KEYWORDS)
    equipment = _extract_from_sentences(lowered, EQUIPMENT_KEYWORDS)
    capabilities = _extract_from_sentences(lowered, CAPABILITY_KEYWORDS)

    # Numbers
    number_doctors = _safe_int(_pick_first(row, ["doctors"]))
    capacity = _safe_int(_pick_first(row, ["beds"]))

    lat = _safe_float(_pick_first(row, ["latitude"]))
    lon = _safe_float(_pick_first(row, ["longitude"]))

    city, region, country, code = _city_region_country(row)

    # Suspicious detection
    suspicious_claims = []
    if any(p in lowered for p in SUSPICIOUS_PHRASES) and not equipment:
        suspicious_claims.append("Marketing claim without proof")

    if "24/7" in lowered and "emergency" not in lowered:
        suspicious_claims.append("24/7 but no emergency support")

    if "icu" in lowered and "icu" not in equipment:
        suspicious_claims.append("ICU claim without equipment")

    # Create object
    facility = ExtractedFacility(
        row_index=row_index,
        name=name,
        procedures=procedures,
        equipment=equipment,
        capabilities=capabilities,
        number_doctors=number_doctors,
        capacity=capacity,
        latitude=lat,
        longitude=lon,
        suspicious_claims=suspicious_claims,
        evidence=[
            Evidence(
                row_index=row_index,
                source_columns=used_cols,
                snippet=blob[:300],
            )
        ],
    )

    return facility


# =========================
# DATAFRAME PROCESSOR
# =========================
def extract_dataframe(df: pd.DataFrame) -> List[ExtractedFacility]:
    results: List[ExtractedFacility] = []

    for idx, row in df.reset_index(drop=True).iterrows():
        results.append(extract_row(row, idx))

    return results